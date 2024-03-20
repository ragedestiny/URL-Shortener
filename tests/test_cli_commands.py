import os
import sys

DIR = os.path.dirname(os.path.dirname(__file__))  # The repo root directory
# print(DIR)  # In case you want to take a look at it...
sys.path.append(DIR)  # Temporarily add the repo root to sys.path so the 'src' module can be imported

import unittest
from unittest.mock import patch, MagicMock

from app.commands.auth_commands import login
from app.commands.admin_commands import list_all_urls, update_url_limit
from app.commands.user_commands import list_my_urls, shorten_url, create_user, change_password, delete_url
from app.commands.url_commands import lookup_url

class TestAuthCLI(unittest.TestCase):
    
    @patch('app.commands.auth_commands.typer.echo')
    @patch('app.commands.auth_commands.requests.post')
    def test_login_successful(self, mock_post, mock_echo):
        # Mock successful response from the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "mocked_access_token"}
        mock_post.return_value = mock_response

        # Call the login function with valid credentials
        login("test@example.com", "Password123")

        # Check if the access token is echoed
        mock_echo.assert_called_once_with("Access token: mocked_access_token")

    @patch('app.commands.auth_commands.typer.echo')
    @patch('app.commands.auth_commands.requests.post')
    def test_login_invalid_credentials(self, mock_post, mock_echo):
        # Mock response for invalid credentials
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_response.text = "Invalid credentials"
        mock_post.return_value = mock_response

        # Call the login function with invalid credentials
        login("test@example.com", "Invalid_password1")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Invalid credentials")
        
        
class TestAdminCLIs(unittest.TestCase):
    
    @patch('app.commands.admin_commands.typer.echo')
    @patch('app.commands.admin_commands.requests.patch')
    def test_update_url_limit_successful(self, mock_patch, mock_echo):
        # Mock successful response from the requests.patch method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        # Call the update_url_limit function with valid parameters
        update_url_limit("user@example.com", 10, "mocked_access_token")

        # Check if the success message is echoed
        mock_echo.assert_called_once_with("URL limit updated successfully.")

    @patch('app.commands.admin_commands.typer.echo')
    @patch('app.commands.admin_commands.requests.patch')
    def test_update_url_limit_invalid_email(self, mock_patch, mock_echo):
        # Mock response for invalid email
        mock_response = MagicMock()
        mock_response.status_code = 400  # Bad Request
        mock_response.text = "value is not a valid email address"
        mock_patch.return_value = mock_response

        # Call the update_url_limit function with an invalid email
        update_url_limit("invalid_email", 10, "valid_token")

        # Check if the error message contains the expected substring
        error_message = mock_echo.call_args[0][0]
        self.assertIn("value is not a valid email address", error_message)


    @patch('app.commands.admin_commands.typer.echo')
    @patch('app.commands.admin_commands.requests.patch')
    def test_update_url_limit_insufficient_limit(self, mock_patch, mock_echo):
        # Mock response for insufficient URL limit
        mock_patch.return_value.status_code = 400  # Bad Request
        mock_patch.return_value.text = "New limit cannot be less than the existing URL count."

        # Call the update_url_limit function with a new limit less than existing URL count
        update_url_limit("user@example.com", 5, "valid_token")

        # Check if the error message contains the expected substring
        mock_echo.assert_called_once_with("Error: New limit cannot be less than the existing URL count.")
        

    @patch('app.commands.admin_commands.typer.echo')
    @patch('app.commands.admin_commands.requests.get')
    def test_list_all_urls_successful(self, mock_get, mock_echo):
        # Mock successful response from the requests.get method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [("short_url_1", "long_url_1", "user1@test.com"), ("short_url_2",  "long_url_2", "user2@test.com")]
        mock_get.return_value = mock_response

        # Call the list_all_urls function with valid token
        list_all_urls("mocked_access_token")

        # Check if the URL pairs are echoed
        mock_echo.assert_any_call("Here are all the URLs:")
        mock_echo.assert_any_call(("short_url_1", "long_url_1", "user1@test.com"))
        mock_echo.assert_any_call(("short_url_2", "long_url_2", "user2@test.com"))

    @patch('app.commands.admin_commands.typer.echo')
    @patch('app.commands.admin_commands.requests.get')
    def test_list_all_urls_invalid_token(self, mock_get, mock_echo):
        # Mock response for unauthorized token
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        # Call the list_all_urls function with an invalid token
        list_all_urls("invalid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Unauthorized")



class TestUserCLIs(unittest.TestCase):

    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_create_user_successful(self, mock_post, mock_echo):
        # Mock successful response from the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call the create_user function with valid parameters
        create_user("test@example.com", "Password123")

        # Check if the success message is echoed
        mock_echo.assert_called_once_with("User account created successfully.")
        

    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_create_user_validation_error(self, mock_post, mock_echo):
        # Mock validation error response from the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Validation error: Email must be a valid email address."
        mock_post.return_value = mock_response

        # Call the create_user function with invalid email format
        create_user("invalid_email", "Password123")

        # Check if the error message is echoed
        error_message = mock_echo.call_args[0][0]
        self.assertIn("value is not a valid email address", error_message)

    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_create_user_existing_email(self, mock_post, mock_echo):
        # Mock response for existing email
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Email already exists."
        mock_post.return_value = mock_response

        # Call the create_user function with an existing email
        create_user("existing@example.com", "Password123")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Email already exists.")


    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.get')
    def test_list_my_urls_successful(self, mock_get, mock_echo):
        # Mock successful response from the requests.get method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["url1", "url2"]  # Example URLs
        mock_get.return_value = mock_response

        # Call the list_my_urls function with valid token
        list_my_urls("mocked_access_token")

        # Check if the URL list is echoed
        mock_echo.assert_any_call("Here is your URL list:")
        mock_echo.assert_any_call("url1")
        mock_echo.assert_any_call("url2")


    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.get')
    def test_list_my_urls_unauthorized(self, mock_get, mock_echo):
        # Mock response for unauthorized token
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_response.text = "Authentication required"
        mock_get.return_value = mock_response

        # Call the list_my_urls function with an unauthorized token
        list_my_urls("invalid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Authentication required")


    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.get')
    def test_list_my_urls_server_error(self, mock_get, mock_echo):
        # Mock response for server error
        mock_response = MagicMock()
        mock_response.status_code = 500  # Internal Server Error
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Call the list_my_urls function
        list_my_urls("valid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Internal Server Error")

    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.patch')
    def test_change_password_successful(self, mock_patch, mock_echo):
        # Mock successful response from the requests.patch method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        # Call the change_password function with valid parameters
        change_password("NewPassword123", "mocked_access_token")

        # Check if the success message is echoed
        mock_echo.assert_called_once_with("Password changed successfully.")


    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.patch')
    def test_change_password_validation_error(self, mock_patch, mock_echo):
        # Mock response for validation error
        mock_response = MagicMock()
        mock_response.status_code = 400  # Bad Request
        mock_response.text = "Password must have at least 8 characters."
        mock_patch.return_value = mock_response

        # Call the change_password function with invalid parameters
        change_password("weak", "valid_token")

        # Check if the error message is echoed
        error_message = mock_echo.call_args[0][0]
        self.assertIn("Password must have at least 8 characters.", error_message)


    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.patch')
    def test_change_password_unauthorized(self, mock_patch, mock_echo):
        # Mock response for unauthorized token
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_response.text = "Unauthorized"
        mock_patch.return_value = mock_response

        # Call the change_password function with an unauthorized token
        change_password("StrongPassword123", "invalid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Unauthorized")

    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.patch')
    def test_change_password_server_error(self, mock_patch, mock_echo):
        # Mock response for server error
        mock_response = MagicMock()
        mock_response.status_code = 500  # Internal Server Error
        mock_response.text = "Internal Server Error"
        mock_patch.return_value = mock_response

        # Call the change_password function
        change_password("StrongPassword123", "valid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Internal Server Error")


    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_shorten_url_successful(self, mock_post, mock_echo):
        # Mock successful response from the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"short_url": "mocked_short_url"}
        mock_post.return_value = mock_response

        # Call the shorten_url function with valid parameters
        shorten_url("https://example.com", "mocked_access_token", "test_short_url")

        # Check if the short URL is echoed
        mock_echo.assert_called_once_with("Short URL: mocked_short_url")

        
    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_shorten_url_invalid_long_url(self, mock_post, mock_echo):
        # Mock response for invalid long URL
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Input should be a valid URL"
        mock_post.return_value = mock_response

        # Call the shorten_url function with an invalid long URL
        shorten_url("invalid_url", "mocked_access_token")

        # Check if the error message is echoed
        error_message = mock_echo.call_args[0][0]
        self.assertIn("Input should be a valid URL", error_message)
        
        
    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_shorten_url_unauthorized(self, mock_post, mock_echo):
        # Mock response for unauthorized token
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        # Call the shorten_url function with an unauthorized token
        shorten_url("https://example.com", "invalid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Unauthorized")
        
    @patch('app.commands.user_commands.typer.echo')
    @patch('app.commands.user_commands.requests.post')
    def test_shorten_url_server_error(self, mock_post, mock_echo):
        # Mock response for server error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        # Call the shorten_url function
        shorten_url("https://example.com", "valid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Internal Server Error")
        
    @patch("app.commands.user_commands.typer.echo")
    @patch("app.commands.user_commands.requests.delete")
    def test_delete_url_successful(self, mock_delete, mock_echo):
        # Mock successful response from the requests.delete method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Short URL deleted successfully."
        mock_delete.return_value = mock_response

        # Call the delete_url function with valid parameters
        delete_url("test_short_url", "mocked_access_token")

        # Check if the success message is echoed
        mock_echo.assert_called_once_with("Short URL deleted successfully.")

    @patch("app.commands.user_commands.typer.echo")
    @patch("app.commands.user_commands.requests.delete")
    def test_delete_url_invalid_short_url(self, mock_delete, mock_echo):
        # Mock response for invalid short URL
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Short URL 'test_short_url' not found or does not belong to the current user."
        mock_delete.return_value = mock_response

        # Call the delete_url function with an invalid short URL
        delete_url("invalid_url", "mocked_access_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Short URL 'test_short_url' not found or does not belong to the current user.")

    @patch("app.commands.user_commands.typer.echo")
    @patch("app.commands.user_commands.requests.delete")
    def test_delete_url_unauthorized(self, mock_delete, mock_echo):
        # Mock response for unauthorized token
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Authentication required to access this endpoint."
        mock_delete.return_value = mock_response

        # Call the delete_url function with an unauthorized token
        delete_url("test_short_url", "invalid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Authentication required to access this endpoint.")

    @patch("app.commands.user_commands.typer.echo")
    @patch("app.commands.user_commands.requests.delete")
    def test_delete_url_server_error(self, mock_delete, mock_echo):
        # Mock response for server error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_delete.return_value = mock_response

        # Call the delete_url function
        delete_url("test_short_url", "valid_token")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Internal Server Error")  
    
    
class TestUrlCLI(unittest.TestCase):

    @patch('app.commands.url_commands.typer.echo')
    @patch('app.commands.url_commands.requests.get')
    def test_lookup_url_successful(self, mock_get, mock_echo):
        # Mock successful response from the requests.get method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"long_url": "https://example.com"}
        mock_get.return_value = mock_response

        # Call the lookup_url function with a valid short URL
        lookup_url("test_short_url")

        # Check if the long URL is echoed
        mock_echo.assert_called_once_with("Long URL for test_short_url: https://example.com")

    @patch('app.commands.url_commands.typer.echo')
    @patch('app.commands.url_commands.requests.get')
    def test_lookup_url_invalid_short_url(self, mock_get, mock_echo):
        # Mock response for invalid short URL
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "validation error for shortURL"
        mock_get.return_value = mock_response

        # Call the lookup_url function with an invalid short URL
        lookup_url("invalid_short_url")

        # Check if the error message is echoed
        error_message = mock_echo.call_args[0][0]
        self.assertIn("validation error for shortURL", error_message)

    @patch('app.commands.url_commands.typer.echo')
    @patch('app.commands.url_commands.requests.get')
    def test_lookup_url_not_found(self, mock_get, mock_echo):
        # Mock response for short URL not found
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Short URL 'not_found_short_url' doesn't exist."
        mock_get.return_value = mock_response

        # Call the lookup_url function with a short URL that doesn't exist
        lookup_url("not_found_url")

        # Check if the error message is echoed
        error_message = mock_echo.call_args[0][0]
        self.assertIn("Short URL 'not_found_short_url' doesn't exist.", error_message)

    @patch('app.commands.url_commands.typer.echo')
    @patch('app.commands.url_commands.requests.get')
    def test_lookup_url_server_error(self, mock_get, mock_echo):
        # Mock response for server error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Call the lookup_url function
        lookup_url("valid_short_url")

        # Check if the error message is echoed
        mock_echo.assert_called_once_with("Error: Internal Server Error") 
        
    
if __name__ == "__main__":
    unittest.main()