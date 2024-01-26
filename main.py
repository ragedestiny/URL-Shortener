from models.schemas import validateLongUrl, validateShortUrl


print('Enter a url to shorten:')
validateLongUrl(input())

print('Enter a short url:')
validateShortUrl(input())

