from nanoid import generate

from models.testurls import urlMap

# generate a random short URL of size 15
def randomID() -> str:
    randID = generate(size=15)
    while randID in urlMap:
        # make sure short URL doesn't already exist
        randID = generate(size=15)
    return randID