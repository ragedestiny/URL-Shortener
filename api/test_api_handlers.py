import os
import sys

DIR = os.path.dirname(os.path.dirname(__file__))  # The repo root directory
# print(DIR)  # In case you want to take a look at it...
sys.path.append(DIR)  # Temporarily add the repo root to sys.path so the 'src' module can be imported


import unittest
import boto3
from moto import mock_aws
from fastapi import HTTPException

import api_handlers
from models.schemas import longURL, shortURL

@mock_aws
class TestAPI(unittest.TestCase):
    
    def setUp(self):
        # mock a connection using boto3
        self.dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
        
        # create table using Url Model
        from models.test_table import create_url_table
        self.table = create_url_table(self.dynamodb)
        # add two dummy url pairs to mock database
        dummy_data = [
            {"short_url": "short_url_1", "long_url": "http://example1.com"},
            {"short_url": "short_url_2", "long_url": "http://example2.com"}
        ]
        with self.table.batch_writer() as batch:
            for data in dummy_data:
                batch.put_item(Item=data)
        
        
    def tearDown(self) -> None:
        # tear down the mock table
        self.table.delete()
        self.dynamodb = None
               
        
    def test_table_exists(self):
        # Test to see mock table created and name matches
        self.assertTrue(self.table)
        self.assertIn('Short_URL-to-Long_URL', self.table.name)
    
    
    def test_get_root(self):
        self.assertEqual(api_handlers.test(), { 'Hello': 'World' })
        
    
    def test_getAll(self):
        # Expected result from mock database
        expected_result = {
            "short_url_1": "http://example1.com",
            "short_url_2": "http://example2.com"
        }
        self.assertEqual(api_handlers.getAll(), expected_result)


    def test_toShorten(self):
        # dummy variables for testing
        longUrlwoHttp = longURL(url='http://www.testing.com')
        validshortUrl = shortURL(short_Url='98uwefowiefs')
        preexistUrl = shortURL(short_Url='short_url_1')
        
        # test for a valid response (valid long URL, valid non existing short URL)
        self.assertEqual(api_handlers.toShorten(long_url=longUrlwoHttp, shorturl=validshortUrl), { 'short_url' : validshortUrl.short_Url })
        
        # test for a valid response (valid long URL, none short URL)
        result = api_handlers.toShorten(long_url=longUrlwoHttp)
        self.assertIsInstance(result, dict)
        self.assertIn('short_url', result)
        
        # test for an error with preexist short URL is entered
        with self.assertRaises(HTTPException) as error:
            api_handlers.toShorten(long_url=longUrlwoHttp, shorturl=preexistUrl)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"Short url {preexistUrl.short_Url} already exist, try another one.")


    def test_getLongUrl(self):
        NotexistshortURL = 'Notexist'
        existshortURL = 'short_url_1'
        
        # test if a redirect is successful
        response = api_handlers.getLongUrl(existshortURL)
        self.assertEqual(response.status_code, 307) 
        
        # test for an error with non existing short URL for redirect
        with self.assertRaises(HTTPException) as error:
            api_handlers.getLongUrl(NotexistshortURL)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, f"Short URL of {NotexistshortURL} doesn't exist.")
        
        
        
if __name__ == '__main__':
    unittest.main()