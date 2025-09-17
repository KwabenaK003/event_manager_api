from fastapi import Form, File, UploadFile, HTTPException, status, APIRouter, Depends
from db import events_collection
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
from datetime import date, time
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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


@events_router.post("/events", tags=["Events"], summary="Create event")
def post_events(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    event_date: Annotated[date, Form(...)],
    start_time: Annotated[time, Form(...)],
    end_time: Annotated[time, Form(...)]
    ):
    print(credentials)
    # Upload flyer to cloudinary to get a url 
    upload_result= cloudinary.uploader.upload(flyer.file)
    
    # Insert event into database
    events_collection.insert_one({
        "title": title,
        "description": description,
        "flyer": upload_result["secure_url"],
        "event_date": str(event_date),
        "start_time": start_time.replace(tzinfo=None).isoformat(),
        "end_time": end_time.replace(tzinfo=None).isoformat()
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


@events_router.put("/events/{event_id}", tags=["Events"], summary="Update an Event")
def replace_event(
    event_id,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()],
    event_date: Annotated[date, Form(...)],
    start_time: Annotated[time, Form(...)],
    end_time: Annotated[time, Form(...)]
    ):
     # Check if event_id is valid mongo id
    # Upload fyer to cloudinary to get a url
    upload_result= cloudinary.uploader.upload(flyer.file)
    print(upload_result)
    # Replace event in a database
    events_collection.replace_one(
        filter={"_id": event_id},
        replacement={"title": title,
        "description": description,
        "flyer": upload_result["secure_url"],
        "event_date": str(event_date),
        "start_time": start_time.replace(tzinfo=None).isoformat(),
        "end_time": end_time.replace(tzinfo=None).isoformat()
    })
    # Return response
    return {"message": " Event replaced successfully"}


@events_router.delete("/events/{event_id}", tags=["Events"], summary="Delete an Event")
def delete_eventevent_id(event_id):
    # Check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")
    # Delete event from database
    delete_result =  events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")
             
    # Return response
    return {"message": " Event deleted successfully"}
