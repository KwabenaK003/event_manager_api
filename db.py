from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Mongo Atlas Cluster
mongo_client = MongoClient(os.getenv("MONGO_URL"))

# Access database
event_manager_db = mongo_client["event_manager_db"]

# Pick a collection to operate om
events_collection = event_manager_db["events"]