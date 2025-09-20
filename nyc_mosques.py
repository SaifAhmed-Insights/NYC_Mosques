import os
import requests
import csv
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["nyc_mosques_db"]
collection = db["mosques"]

# NYC borough queries
queries = [
    "mosques in Manhattan, NYC",
    "mosques in Brooklyn, NYC",
    "mosques in Queens, NYC",
    "mosques in Bronx, NYC",
    "mosques in Staten Island, NYC"
]

mosques = []

for query in queries:
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    for place in data.get("results", []):
        place_id = place.get("place_id")

        # Get details including reviews
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,place_id,reviews",
            "key": GOOGLE_API_KEY
        }
        details_res = requests.get(details_url, params=details_params).json()
        result = details_res.get("result", {})

        mosque = {
            "name": result.get("name"),
            "address": result.get("formatted_address"),
            "place_id": result.get("place_id"),
            "lat": result.get("geometry", {}).get("location", {}).get("lat"),
            "lng": result.get("geometry", {}).get("location", {}).get("lng"),
            "reviews": []
        }

        # Save top 3 reviews only
        for review in result.get("reviews", [])[:3]:
            mosque["reviews"].append({
                "author": review.get("author_name"),
                "rating": review.get("rating"),
                "text": review.get("text"),
                "time": review.get("relative_time_description")
            })

        mosques.append(mosque)

        # Insert/update in MongoDB
        collection.update_one(
            {"place_id": mosque["place_id"]},
            {"$set": mosque},
            upsert=True
        )

print(f"✅ Inserted/Updated {len(mosques)} mosques with top 3 reviews into MongoDB")

# Save CSV with reviews
with open("mosques_with_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "address", "place_id", "lat", "lng", "reviews"])
    writer.writeheader()
    writer.writerows(mosques)

print("✅ Saved mosques_with_reviews.csv")
