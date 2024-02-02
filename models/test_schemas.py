import os
import sys
DIR = os.path.dirname(os.path.dirname(__file__))  # The repo root directory
sys.path.append(DIR)  # Temporarily add the repo root to sys.path so the 'src' module can be imported

import unittest
import schemas

class TestAPI(unittest.TestCase):

    def test_longUrl(self):
        # error if long URL not valid        
        with self.assertRaises(Exception) as missingbase:
            schemas.longURL(url='www.yahoo.com')
        self.assertTrue('relative URL without a base' in str(missingbase.exception))


    def test_shortUrl(self):
        valid_short = 'woIfJ61243Wdf'
        tooshortUrl = 'wfd3528'
        toolongUrl = 'wofijwef032jf09ef29j2f09'
        notallowcharUrl = '736&lsdo#lsd)()'
        
        # test valid user input short URL
        self.assertEqual(schemas.shortURL(short_Url=valid_short).short_Url, valid_short)
        
        # user input short URL less than 10 chars
        with self.assertRaises(ValueError):
            schemas.shortURL(short_Url=tooshortUrl)
        
        # user input short URL more than 15 chars
        with self.assertRaises(ValueError):
            schemas.shortURL(short_Url=toolongUrl)
        
        # user input short URL contain non A-Z a-z 0-9 _ or -
        with self.assertRaises(ValueError):
            schemas.shortURL(short_Url=notallowcharUrl)
        

        
if __name__ == '__main__':
    unittest.main()