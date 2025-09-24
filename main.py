from fastapi import FastAPI
from dotenv import load_dotenv
import cloudinary
from routes.events import events_router
from routes.users import users_router
from routes.genai import genai_router

import os

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    )

app = FastAPI()

# Include routers
app.include_router(events_router)
app.include_router(users_router)
app.include_router(genai_router)

# print(type(os.getenv("CLOUDINARY_NAME")))
# print("API_KEY:", os.getenv("CLOUDINARY_API_KEY"))
# print("API_SECRET:", os.getenv("CLOUDINARY_API_SECRET"))