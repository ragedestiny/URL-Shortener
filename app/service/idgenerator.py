from nanoid import generate


# generate a random short URL of size 15
def randomID() -> str:
    randID = generate(size=15)
    return randID