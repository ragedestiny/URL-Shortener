import os
import sys

DIR = os.path.dirname(os.path.dirname(__file__))  # The repo root directory
# print(DIR)  # In case you want to take a look at it...
sys.path.append(DIR)  # Temporarily add the repo root to sys.path so the 'src' module can be imported


import unittest
import api_handlers
from models.schemas import longURL, shortURL
from models.testurls import urlMap


class TestAPI(unittest.TestCase):
    
   
    def test_get_root(self):
        self.assertEqual(api_handlers.test(), { 'Hello': 'World' })
        
        
    def test_getAll(self):
        self.assertEqual(api_handlers.getAll(), urlMap)
        
        
    def test_toShorten(self):
        # dummy variables for testing
        longUrlwoHttp = longURL(long_Url='http://www.testing.com')
        validshortUrl = shortURL(short_Url='98uwefowiefs')
        preexistUrl = shortURL(short_Url='2039jf0wf9js')
        
        # test for a valid response (valid long URL, valid non existing short URL)
        self.assertEqual(api_handlers.toShorten(url=longUrlwoHttp, short=validshortUrl), { 'short_url' : validshortUrl.short_Url })
        
        # test for a valid response (valid long URL, none short URL)
        self.assertIsInstance(api_handlers.toShorten(url=longUrlwoHttp), dict)
        
        # test for an error with preexist short URL is entered
        with self.assertRaises(Exception):
            api_handlers.toShorten(url=longUrlwoHttp, short=preexistUrl)
    
    
    def test_getLongUrl(self):
        NotexistshortURL = 'Notexist'
        
        # test for an error with non existing short URL for redirect
        with self.assertRaises(Exception):
            api_handlers.getLongUrl(NotexistshortURL)
            
        
if __name__ == '__main__':
    unittest.main()