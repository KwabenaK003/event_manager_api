from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_home():
    return {"message" : "You are on the home page"}

# Events endpoints
@app.get("/events")
def get_events():
    return {"data": []}

@app.post("/events")
def post_events():
    return {"message": "Event added successfully"}

@app.get("/events{event_id}")
def get_event_by_id(event_id):
    return { "data": {"id": event_id}}