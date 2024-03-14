import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from pynamodb.exceptions import DoesNotExist

from app.models.database import Users
from app.service import pwhashing

load_dotenv()

# Read environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
HASH_ALGORITHM = os.getenv("HASH_ALGORITHM")

# Initialize password context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=HASH_ALGORITHM)
    return encoded_jwt


# User authentication function
def authenticate_user(email: str, password: str) -> Optional[Users]:
    """Authenticate user by email and password."""
    try:
        user = Users.get(email)
    except DoesNotExist:
        user = None
    if not user or not pwhashing.verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[HASH_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Query the user directly by email
        try:
            user = Users.get(email)
        except DoesNotExist:
            user = None
        if not user:
            raise credentials_exception
        return user
    except (JWTError, IndexError):
        raise credentials_exception