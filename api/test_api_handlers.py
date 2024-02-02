import os
import sys

DIR = os.path.dirname(os.path.dirname(__file__))  # The repo root directory
# print(DIR)  # In case you want to take a look at it...
sys.path.append(DIR)  # Temporarily add the repo root to sys.path so the 'src' module can be imported


import unittest
from unittest import mock
import boto3
from moto import mock_aws

import api_handlers
from models.schemas import longURL, shortURL



class TestAPI(unittest.TestCase):
    # def setUp(self):
    #     """Create the mock database and table"""
    #     self.dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
        
    #     from models.test_table import create_url_table
    #     self.table = create_url_table(self.dynamodb)
    #     print(self.table)
        
    # def tearDown(self) -> None:
    #     self.table.delete()
    #     self.dynamodb = None
        
    #     return super().tearDown()
        
    # def test_table_exists(self):
    #     self.assertTrue(self.table)
    #     self.assertIn('Short_URL-to-Long_URL', self.table.name)
   
   
    def test_get_root(self):
        self.assertEqual(api_handlers.test(), { 'Hello': 'World' })
        
        
    def test_getAll(self):
        self.assertIsInstance(api_handlers.getAll(), dict)
        
        
    def test_toShorten(self):
        # dummy variables for testing
        longUrlwoHttp = longURL(url='http://www.testing.com')
        validshortUrl = shortURL(short_Url='98uwefowiefs')
        preexistUrl = shortURL(short_Url='2039jf0wf9js')
        
        # test for a valid response (valid long URL, valid non existing short URL)
        self.assertEqual(api_handlers.toShorten(long_url=longUrlwoHttp, short_url=validshortUrl), { 'short_url' : validshortUrl.short_Url })
        
        # test for a valid response (valid long URL, none short URL)
        self.assertIsInstance(api_handlers.toShorten(long_url=longUrlwoHttp), dict)
        
        # test for an error with preexist short URL is entered
        with self.assertRaises(Exception):
            api_handlers.toShorten(long_url=longUrlwoHttp, short_url=preexistUrl)
    
    
    def test_getLongUrl(self):
        NotexistshortURL = 'Notexist'
        
        # test for an error with non existing short URL for redirect
        with self.assertRaises(Exception):
            api_handlers.getLongUrl(NotexistshortURL)
            
        
if __name__ == '__main__':
    unittest.main()