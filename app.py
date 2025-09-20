from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect MongoDB
client = MongoClient(MONGO_URI)
db = client["nyc_data"]
mosques_collection = db["mosques"]

# FastAPI app
app = FastAPI()

# Helper: Convert Mongo ObjectId to string
def mosque_serializer(mosque) -> dict:
    return {
        "id": str(mosque["_id"]),
        "name": mosque.get("name"),
        "address": mosque.get("address"),
        "city": mosque.get("city"),
        "state": mosque.get("state"),
        "zip_code": mosque.get("zip_code"),
        "lat": mosque.get("lat"),
        "lng": mosque.get("lng"),
        "place_id": mosque.get("place_id"),
    }

# Pydantic model for input
class Mosque(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    place_id: Optional[str] = None


# -----------------------
# ✅ CRUD Endpoints
# -----------------------

# GET (Search by name, city, state, zip_code)
@app.get("/mosques")
def get_mosques(
    name: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}  # case-insensitive
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if state:
        query["state"] = state
    if zip_code:
        query["zip_code"] = zip_code

    mosques = list(mosques_collection.find(query))
    return {"count": len(mosques), "data": [mosque_serializer(m) for m in mosques]}


# POST (Add new mosque)
@app.post("/mosques")
def add_mosque(mosque: Mosque):
    result = mosques_collection.insert_one(mosque.dict())
    return {"message": "Mosque added", "id": str(result.inserted_id)}


# PATCH (Update mosque info)
@app.patch("/mosques/{mosque_id}")
def update_mosque(mosque_id: str, mosque: dict):
    result = mosques_collection.update_one(
        {"_id": ObjectId(mosque_id)}, {"$set": mosque}
    )
    if result.matched_count == 0:
        return {"error": "Mosque not found"}
    return {"message": "Mosque updated"}


# DELETE (Remove mosque)
@app.delete("/mosques/{mosque_id}")
def delete_mosque(mosque_id: str):
    result = mosques_collection.delete_one({"_id": ObjectId(mosque_id)})
    if result.deleted_count == 0:
        return {"error": "Mosque not found"}
    return {"message": "Mosque deleted"}
