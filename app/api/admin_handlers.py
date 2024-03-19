from fastapi import APIRouter, Depends, HTTPException
from fastapi import HTTPException
from pydantic import ValidationError
from pynamodb.exceptions import DoesNotExist

from app.models import schemas
from app.service.idgenerator import randomID
from app.models.database import Urls, Users
from app.auth.auth import get_current_user


router = APIRouter()

# grab all url pairs
@router.get("/list_urls")
def get_all_urls(current_user: Users = Depends(get_current_user)):
    """
    Get request to retrieve all short url to long url pairs
    
    Only users with admin privileges can access this endpoint.

    Returns:
        dict: All short url to long url pairs
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    url_pairs = {(urlpair.short_url, urlpair.long_url, urlpair.creator_email) for urlpair in Urls.scan()}
    
    return url_pairs


@router.patch("/update_url_limit")
def update_url_limit(
    user_email: schemas.Email,
    new_limit: int,
    current_user: Users = Depends(get_current_user)
):
    """
    Update the URL limit for a user. This endpoint is admin protected.
    Input a user's email and a new URL limit. If the new limit is less than
    the user's existing URL count, return an error.

    Args:
        user_email (str): Email of the user to update the URL limit.
        new_limit (int): New URL limit for the user.
        current_user (Users): Current logged-in user obtained from JWT token.

    Returns:
        dict: Message indicating success or failure.
    """
    # Check if the current user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin users can update URL limits.")
    
    
    # Retrieve the user from the database
    try:
        user = Users.get(user_email.email)
    except DoesNotExist:
        user = None
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {user_email} not found.")

    # Check if the new limit is less than the existing URL count for the user
    if new_limit < len(user.urls):
        raise HTTPException(status_code=400, detail="New limit cannot be less than the existing URL count.")

    # Update the URL limit for the user
    user.url_limit = new_limit
    user.save()

    return {"message": f"URL limit updated successfully for user {user_email}."}