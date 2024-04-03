import os
import sys

DIR = os.path.dirname(os.path.dirname(__file__))  # The repo root directory
# print(DIR)  # In case you want to take a look at it...
sys.path.append(DIR)  # Temporarily add the repo root to sys.path so the 'src' module can be imported


import unittest
import boto3
from moto import mock_aws
from fastapi import HTTPException

from app.api import url_handlers, admin_handlers, user_handlers
from app.models.schemas import longURL, shortURL, Email, Password
from app.service.pwhashing import hash_password
from app.auth.auth import authenticate_user
from app.models import schemas

@mock_aws
class TestAPI(unittest.TestCase):
    
    def setUp(self):
        # mock a connection using boto3
        self.dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
        
        # create table using Url Model
        from tests.test_table import create_url_table
        self.urltable = create_url_table(self.dynamodb)
        # add two dummy url pairs to mock database
        dummy_url_data = [
            {
                "short_url": "short_url_1", 
                "long_url": "http://example1.com",
                "creator_email": "regularuser@gmail.com"
            },
            {
                "short_url": "short_url_2", 
                "long_url": "http://example2.com",
                "creator_email": "regularuser@gmail.com"
            },
            {
                "short_url": "short_url_3", 
                "long_url": "http://example3.com",
                "creator_email": "adminuser@gmail.com"
            }
        ]
        with self.urltable.batch_writer() as batch:
            for data in dummy_url_data:
                batch.put_item(Item=data)
                
        # create table using User Model
        from tests.test_table import create_user_table
        self.usertable = create_user_table(self.dynamodb)
        # add two dummy users (one regular and one admin) to mock database
        PasswordHash1 = hash_password("Password1")
        PasswordHash2 = hash_password("Password2")
        dummy_user_data = [
            {
                "email": "regularuser@gmail.com",
                "password_hash": PasswordHash1,
                "is_admin": False,
                "url_limit": 2,
                "urls": [["short_url_1", "http://example1.com"], ["short_url_2", "http://example2.com"]]
            },
            {
                "email": "adminuser@gmail.com",
                "password_hash": PasswordHash2,
                "is_admin": True,
                "url_limit": 5,
                "urls": [["short_url_3", "http://example3.com"]]
            }
        ]
        
        
        with self.usertable.batch_writer() as batch:
            for data in dummy_user_data:
                batch.put_item(Item=data)
        
        # Store the original Redis client get method
        self.redis_client_get_original = url_handlers.redis_client.get
        # Mock Redis client methods for cache bypass
        url_handlers.redis_client.get = lambda key: None  # Simulate cache miss for all keys
        self.redis_client_exists_original = url_handlers.redis_client.exists
        url_handlers.redis_client.exists = lambda key: None
        
        # create dummy regular and admin user credentials        
        self.regular_user = self.simulate_login("regularuser@gmail.com","Password1")
        self.admin_user= self.simulate_login("adminuser@gmail.com","Password2")
        
        
    def tearDown(self) -> None:
        # tear down the mock table
        self.urltable.delete()
        self.usertable.delete()
        self.dynamodb = None
        url_handlers.redis_client.get = self.redis_client_get_original
        url_handlers.redis_client.exists = self.redis_client_exists_original
               
        
    def test_table_exists(self):
        # Test to see mock tables created and name matches
        self.assertTrue(self.urltable)
        self.assertIn('Short_URL-to-Long_URL', self.urltable.name)
        
        self.assertTrue(self.usertable)
        self.assertIn('Users-table', self.usertable.name)
        
        
    def simulate_login(self, email, password):
        # Simulate the authentication process
        user = authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid credentials")
        return user
        
        
@mock_aws
class TestUserAPI(TestAPI):
    
    def test_create_user(self):
        test_valid_email = Email(email="testing@gmail.com")
        test_valid_password = Password(password="9weJOWIEFj9wef")
        test_exist_email = Email(email="regularuser@gmail.com")
        
        # Positive test valid email and password are entered
        result = user_handlers.create_user(user_email=test_valid_email, user_password=test_valid_password)
        self.assertIsInstance(result, dict)
        self.assertIn('created successfully', result["message"])
        
        # Negative test with an email that already exist
        with self.assertRaises(HTTPException) as error:
            user_handlers.create_user(user_email=test_exist_email, user_password=test_valid_password)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"Email of {test_exist_email.email} already exist, try another one.")
        
        
    def test_list_my_urls(self):
        
        # Negative test with invalid user, access denied
        with self.assertRaises(HTTPException) as error:
            user_handlers.list_my_urls(current_user=None)
        self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(error.exception.detail, "Authentication required to access this endpoint.")
        
        # Positive test with valid user
        expected_result = [
                    {
                        "short_url": "short_url_1", 
                        "long_url": "http://example1.com",
                    },
                    {
                        "short_url": "short_url_2", 
                        "long_url": "http://example2.com",
                    }
                ]
        self.assertEqual(user_handlers.list_my_urls(current_user=self.regular_user), expected_result)
        
        
    def test_change_password(self):
        valid_new_password = schemas.Password(password="Password3")
        
        # Negative test with invalid user, access denied
        with self.assertRaises(HTTPException) as error:
            user_handlers.change_password(password=valid_new_password,  current_user=None)
        self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(error.exception.detail, "Authentication required to access this endpoint.")
    

        # Positive test with valid user and valid password
        self.assertEqual(user_handlers.change_password(password=valid_new_password, current_user=self.regular_user), {"message": "Password changed successfully"})    
        
        
@mock_aws
class TestAdminAPI(TestAPI):
    
    def test_get_all_urls(self):
        
        # Negative test with regular user, access not allowed
        with self.assertRaises(HTTPException) as error:
            admin_handlers.get_all_urls(current_user=self.regular_user)
        self.assertEqual(error.exception.status_code, 403)
        
        # Positive test with Admin user, return all urls
        expected_result = {
            ("short_url_1", "http://example1.com", "regularuser@gmail.com"),
            ("short_url_2", "http://example2.com", "regularuser@gmail.com"),
            ("short_url_3", "http://example3.com", "adminuser@gmail.com")
        }
        self.assertEqual(admin_handlers.get_all_urls(current_user=self.admin_user), expected_result)


    def test_update_url_limit(self):
        # Dummy test variables
        regular_user_email = schemas.Email(email=self.regular_user.email)
        admin_user_email = schemas.Email(email=self.admin_user.email)
        nonexist_email = schemas.Email(email="notexisting@gmail.com")
        valid_url_limit = 3
        not_valid_limit = 0
        
        # Negative test with regular user, access not allowed
        with self.assertRaises(HTTPException) as error:
            admin_handlers.update_url_limit(user_email=regular_user_email, new_limit=valid_url_limit, current_user=self.regular_user)
        self.assertEqual(error.exception.status_code, 403)
        self.assertEqual(error.exception.detail, "Only admin users can update URL limits.")
        
        # Negative test with admin credential but nonexistent email
        with self.assertRaises(HTTPException) as error:
            admin_handlers.update_url_limit(user_email=nonexist_email, new_limit=valid_url_limit, current_user=self.admin_user)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, f"User with email {nonexist_email} not found.")
        
        # Negative test with admin credential but new url limit greater than current created urls for target user
        with self.assertRaises(HTTPException) as error:
            admin_handlers.update_url_limit(user_email=regular_user_email, new_limit=not_valid_limit, current_user=self.admin_user)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "New limit cannot be less than the existing URL count.")
        
        # Positive test with admin credential, valid target email and url limit
        self.assertEqual(admin_handlers.update_url_limit(user_email=regular_user_email, new_limit=valid_url_limit, current_user=self.admin_user), {"message": f"URL limit updated successfully for user {regular_user_email}."})
        
        self.assertEqual(admin_handlers.update_url_limit(user_email=admin_user_email, new_limit=valid_url_limit, current_user=self.admin_user), {"message": f"URL limit updated successfully for user {admin_user_email}."})    


@mock_aws
class TestUrlAPI(TestAPI):
    
    def test_get_root(self):
        self.assertEqual(url_handlers.test(), { 'Hello': 'World' })
        
        
    def test_to_shorten(self):
        # dummy variables for testing
        longUrlwoHttp = longURL(url='http://www.testing.com')
        validshortUrl = shortURL(short_Url='98uwefowiefs')
        preexistUrl = shortURL(short_Url='short_url_1')
        
        # Negative test with invalid user, access denied
        with self.assertRaises(HTTPException) as error:
            url_handlers.to_shorten(long_url=longUrlwoHttp, short_url=validshortUrl, current_user=None)
        self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(error.exception.detail, "Authentication required to access this endpoint.")

        # Negative test with valid user but url limit has been reached
        with self.assertRaises(HTTPException) as error:
            url_handlers.to_shorten(long_url=longUrlwoHttp, short_url=validshortUrl, current_user=self.regular_user)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"User has reached the maximum URL limit of {self.regular_user.url_limit} short urls.")
        
        # Negative test for an error with preexist short URL is entered
        with self.assertRaises(HTTPException) as error:
            url_handlers.to_shorten(long_url=longUrlwoHttp, short_url=preexistUrl, current_user=self.admin_user)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"Short URL {preexistUrl.short_Url} already exists, please try another one.")
        
        # Positive test for a valid response (valid long URL, valid non existing short URL, valid user with urls under limit)
        Pos_response = { 'short_url' : validshortUrl.short_Url, 'long_url' : str(longUrlwoHttp.url) }
        self.assertEqual(url_handlers.to_shorten(long_url=longUrlwoHttp, short_url=validshortUrl, current_user=self.admin_user), Pos_response)
        
        # Positive test for a valid response (valid long URL, none short URL, valid user with urls under limit)
        result = url_handlers.to_shorten(long_url=longUrlwoHttp, current_user=self.admin_user)
        self.assertIsInstance(result, dict)
        self.assertIn('short_url', result)
        

    def test_delete_url(self):
        # dummy variables for testing
        selfownUrl = shortURL(short_Url='short_url_1')
        nonexistUrl = shortURL(short_Url='NotexistingURL')
        NotOwnUurl = shortURL(short_Url='short_url_3')
        
        # Negative test with invalid user, access denied
        with self.assertRaises(HTTPException) as error:
            url_handlers.delete_url(short_url=selfownUrl, current_user=None)
        self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(error.exception.detail, "Authentication required to access this endpoint.")

        # Negative test with valid user but trying to delete a non-existing URL
        with self.assertRaises(HTTPException) as error:
            url_handlers.delete_url(short_url=nonexistUrl, current_user=self.regular_user)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, f"Short URL '{nonexistUrl.short_Url}' not found or does not belong to the current user.")

        # Negative test with valid user but trying to delete a URL created by another user
        with self.assertRaises(HTTPException) as error:
            url_handlers.delete_url(short_url=NotOwnUurl, current_user=self.regular_user)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, f"Short URL '{NotOwnUurl.short_Url}' not found or does not belong to the current user.")

        # Positive test for successfully deleting an existing URL
        response = url_handlers.delete_url(short_url=selfownUrl, current_user=self.regular_user)
        self.assertEqual(response, { "message": f"Short URL '{selfownUrl.short_Url}' deleted successfully." })


    def test_getLongUrl(self):
        NotexistshortURL = 'Notexist'
        existshortURL = 'short_url_1'
        
        # Positive test for a successful redirect
        response = url_handlers.getLongUrl(existshortURL)
        self.assertEqual(response.status_code, 307) 
        
        # Negative test with non existing short URL for redirect
        with self.assertRaises(HTTPException) as error:
            url_handlers.getLongUrl(NotexistshortURL)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"Short URL of {NotexistshortURL} doesn't exist.")    

    def test_lookupLongUrl(self):
        NotexistshortURL = 'Notexist'
        existshortURL = 'short_url_1'
        
        # Positive test for a successful redirect
        pos_response = {
            "long_url": "http://example1.com"
        }
        self.assertEqual(url_handlers.lookupLongUrl(existshortURL), pos_response) 
        
        # Negative test with non existing short URL for redirect
        with self.assertRaises(HTTPException) as error:
            url_handlers.getLongUrl(NotexistshortURL)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"Short URL of {NotexistshortURL} doesn't exist.")   


if __name__ == '__main__':
    unittest.main()