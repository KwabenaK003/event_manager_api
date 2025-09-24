from fastapi import APIRouter, Form, HTTPException, status
from typing import Annotated
from pydantic import EmailStr
from db import users_collection
import bcrypt
import jwt
import os
from datetime import datetime, timezone, timedelta
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    HOST = "host"
    GUEST = "guest"


# Create users router
users_router = APIRouter()



# Define endpoints
@users_router.post("/users/register",
                   tags=["Users"], summary="Register User")
def register_user(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    role: Annotated[UserRole, Form()]= UserRole.GUEST):
    
    # Ensure user does not exist
    user_count = users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="User already exist")
    # Hash user password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    # Save user into database
    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "role": role
    })
    # Return response
    return {"message": "User registered successfully!"}

@users_router.post("/users/login", tags=["Users"], summary="Login User")
def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()]):
        
    # find user in the database/Ensure user exist
    user_in_db = users_collection.find_one(filter={"email": email})
    if not user_in_db:
        # User not in db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email or password not found")
    
    # Hash user password
    hashed_password_in_db = user_in_db["password"]

    # Verify the plain-text password against the stored hash
    correct_password = bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password_in_db
    )
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password!")
    # Generate for them an access token
    encoded_jwt = jwt.encode(payload={
        "id": str(user_in_db["_id"]),
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=60)
        }, key=os.getenv("JWT_SECRET_KEY"), algorithm="HS256")
    # Return response
    return {"message": "User logged in successfully!",
            "access_token":encoded_jwt}

# Ensure user exist
# Compare for their password