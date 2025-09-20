from fastapi import FastAPI, Query
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["nyc_mosques_db"]        # database
collection = db["mosques"]           # collection

# FastAPI app
app = FastAPI(title="NYC Mosques API")

@app.get("/")
def home():
    return {"message": "Welcome to NYC Mosques API"}

# ✅ Get all mosques or filter by city/state/zip
@app.get("/mosques")
def get_mosques(
    city: str = Query(None, description="Filter by city, e.g., New York"),
    state: str = Query(None, description="Filter by state, e.g., NY"),
    zip_code: str = Query(None, description="Filter by ZIP code"),
):
    query = {}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    if zip_code:
        query["zip_code"] = {"$regex": zip_code, "$options": "i"}

    mosques = list(collection.find(query, {"_id": 0}))
    return {"count": len(mosques), "data": mosques}

# ✅ Search mosque by name
@app.get("/search")
def search_mosques(name: str = Query(..., description="Search mosque by name")):
    query = {"name": {"$regex": name, "$options": "i"}}
    mosques = list(collection.find(query, {"_id": 0}))
    return {"count": len(mosques), "data": mosques}

# ✅ Get a single mosque by place_id
@app.get("/mosque/{place_id}")
def get_mosque_by_id(place_id: str):
    mosque = collection.find_one({"place_id": place_id}, {"_id": 0})
    if not mosque:
        return {"error": "Mosque not found"}
    return mosque

# ✅ New: Get top 3 reviews for a mosque
@app.get("/reviews/{place_id}")
def get_reviews(place_id: str):
    mosque = collection.find_one({"place_id": place_id}, {"_id": 0, "reviews": 1, "name": 1})
    if not mosque:
        return {"error": "Mosque not found"}
    
    reviews = mosque.get("reviews", [])[:3]  # only top 3
    return {
        "mosque": mosque.get("name"),
        "place_id": place_id,
        "review_count": len(reviews),
        "reviews": reviews
    }

# ✅ CRUD Endpoints
@app.post("/mosque")
def add_mosque(mosque: dict):
    collection.insert_one(mosque)
    return {"message": "Mosque added successfully", "mosque": mosque}

@app.patch("/mosque/{place_id}")
def update_mosque(place_id: str, mosque_update: dict):
    result = collection.update_one({"place_id": place_id}, {"$set": mosque_update})
    if result.matched_count == 0:
        return {"error": "Mosque not found"}
    return {"message": "Mosque updated successfully"}

@app.delete("/mosque/{place_id}")
def delete_mosque(place_id: str):
    result = collection.delete_one({"place_id": place_id})
    if result.deleted_count == 0:
        return {"error": "Mosque not found"}
    return {"message": "Mosque deleted successfully"}
