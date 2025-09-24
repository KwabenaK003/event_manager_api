from fastapi import Form, File, UploadFile, HTTPException, status, APIRouter, Depends
from db import events_collection
from bson.objectid import ObjectId
from utils import replace_mongo_id, genai_client
from typing import Annotated
import cloudinary
import cloudinary.uploader
from datetime import date, time
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles
from google.genai import types

# Create User's router
events_router = APIRouter()

# Events endpoints
@events_router.get("/events", tags=["Events"], summary="Get all events")
def get_events(title="", description="", limit=10, skip= 0):
    # Get all events from database
    events = events_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}},
                {"description": {"$regex": description, "$options": "i"}},
        ]},
        limit= int(limit),
        skip= int(skip)
    ).to_list()
    # Return response
    return {"data": list(map(replace_mongo_id, events))}


@events_router.post("/events", tags=["Events"], summary="Create event", dependencies=[Depends(has_roles(roles=["host", "admin"]))])
def post_events(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    event_date: Annotated[date, Form(...)],
    start_time: Annotated[time, Form(...)],
    end_time: Annotated[time, Form(...)],
    user_id: Annotated[str, Depends(is_authenticated)],
    flyer: Annotated[bytes, File()] = None
    ):
    if not flyer:
        # Generate AI flyer with hugging face
        response = genai_client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=title,
            config=types.GenerateImagesConfig(
                number_of_images= 1
            )
)
        image = response.generated_images[0].image.image_bytes

    event_count = events_collection.count_documents(filter={"$and":[
        {"title": title},
        {"owner": user_id}
    ]})
    if event_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Event with title: {title} and user_id{user_id} already exist!")
    # Upload flyer to cloudinary to get a url 
    upload_result= cloudinary.uploader.upload(image)

    
    # Insert event into database
    events_collection.insert_one({
        "title": title,
        "description": description,
        "flyer": upload_result["secure_url"],
        "event_date": str(event_date),
        "start_time": start_time.replace(tzinfo=None).isoformat(),
        "end_time": end_time.replace(tzinfo=None).isoformat(),
        "owner": user_id
    })
    # Return response
    return {"message": "Event added successfully"}


@events_router.get("/events{event_id}", tags=["Events"], summary="Get event by ID")
def get_event_by_id(event_id):
    # Check if event id is valid
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid momgo id received!")
    # Get all events from database by id
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    return {"data": replace_mongo_id(event)}


@events_router.get("/events/{event_id}/similar")
def get_similar_events(event_id, limit=10, skip= 0):
    # Check if event id is valid
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!")
    # Get all events from database by id
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found!")
    # Get similar event in the database
    similar_events = events_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": event["title"], "$options": "i"}},
                {"description": {"$regex": event["description"], "$options": "i"}}
        ]},
        limit= int(limit),
        skip= int(skip)
    ).to_list()
    # Return response
    return {"data": list(map(replace_mongo_id, similar_events))}



@events_router.put("/events/{event_id}", tags=["Events"], summary="Update an Event", dependencies=[Depends(has_roles(roles=["host", "admin"]))])
def replace_event(
    event_id,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()]= None
    ):
    # Handle when no image is uploaded
    if not flyer:
        # Generate AI flyer with hugging face
        response = genai_client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=title,
            config=types.GenerateImagesConfig(
                number_of_images= 1
            )
)
        image = response.generated_images[0].image.image_bytes
    # Upload fyer to cloudinary to get a url
    upload_result= cloudinary.uploader.upload(image)
    print(upload_result)
    # Replace event in a database
    events_collection.replace_one(
        filter={"_id": event_id},
        replacement={"title": title,
        "description": description,
        "flyer": upload_result["secure_url"]
    })
    # Return response
    return {"message": " Event replaced successfully"}


@events_router.delete("/events/{event_id}", tags=["Events"], summary="Delete an Event", dependencies= [Depends(is_authenticated)])
def delete_event_id(event_id, user_id: Annotated[str, Depends(is_authenticated)]):
    # Check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")
    # Delete event from database
    delete_result =  events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")
             
    # Return response
    return {"message": " Event deleted successfully"}
