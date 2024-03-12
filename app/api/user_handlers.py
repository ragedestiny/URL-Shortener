from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from app.models import schemas
from app.service.pwhashing import hash_password
from app.models.database import Users
from app.auth.auth import authenticate_user, create_access_token, get_current_user

router = APIRouter()

@router.post('/create_user')
def create_user(user_email: schemas.Email, user_password: schemas.Password) -> dict:
    """New User enters email and password to create an account, sends post request to server to add user to database

    Args:
        email (str): Email as user account name
        password (str): password will be hashed

    Raises:
        HTTPException: Any validation errors for email and password, email has already been registered

    Returns:
        dict: Account successfully registered
    """

    # check to see email already exists
    if any(Users.query(user_email.email)):
        raise HTTPException(status_code=400, detail=f"Email of {user_email.email} already exist, try another one.")
    
    # hash pass with bcrypt
    hashedPW = hash_password(password=user_password.password)
    
    # create new account and save to database
    new_user = Users(email=user_email.email, password_hash=hashedPW)
    new_user.save()
    
    return {"message": f"Account of {user_email.email} created successfully."}


@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user with provided credentials and generate an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username(email) and password.

    Raises:
        HTTPException: If the provided credentials are incorrect.

    Returns:
        dict: A dictionary containing the access token and its type.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/list_my_urls")
def list_my_urls(current_user: Users = Depends(get_current_user)):
    """
    Endpoint to list URLs associated with the current authenticated user.

    Args:
        current_user (Users, optional): The current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        List[dict]: A list of dictionaries containing the short URL and original URL for each URL associated with the user.
    """
    # Check if the user is authenticated
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required to access this endpoint.")
    
    # Get the URLs associated with the user
    user_urls = current_user.urls
    
    return user_urls
        


@router.patch("/change_password")
def change_password(password: str, current_user: Users = Depends(get_current_user)):
    """
    Change the password for the current user.

    Args:
        new_password (str): The new password to set for the user.
        current_user (Users): The current authenticated user.

    Returns:
        dict: A dictionary containing a success message.
    """    
    
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required to access this endpoint.")
    
    # Validate the password using the Password model
    try:
        new_password = schemas.Password(password=password)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
    # Update the user's password in the database
    hashed_password = hash_password(new_password.password)
    current_user.password_hash = hashed_password
    current_user.save()
    return {"message": "Password changed successfully"}