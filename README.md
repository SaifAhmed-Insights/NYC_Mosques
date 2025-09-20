NYC Mosques Data Project – Technical Documentation

📌 Overview
This project collects mosque data from Google Maps Places API, stores it in a MongoDB Atlas database, and provides a FastAPI backend with endpoints to search, manage, and fetch reviews of mosques across New York City.

It is designed as a data scraping + REST API project for use in data analysis, search applications, or community platforms.
⚙️ Architecture
1. Data Source: Google Places API (Text Search + Details API).
2. Data Storage: MongoDB Atlas (cloud-hosted NoSQL database).
3. Backend: FastAPI (Python web framework).
📂 Project Structure
nyc_mosques/
│── nyc_mosques.py      # Scraper script for Google Places API
│── main.py             # FastAPI backend
│── mosques_with_reviews.csv # Exported mosque data
│── .env                # Stores API keys and MongoDB URI
│── requirements.txt    # Python dependencies
🗄️ Data Schema
Each mosque document in MongoDB follows this structure:
{
  "name": "Masjid Malcolm Shabazz",
  "address": "102 W 116th St, New York, NY 10026, USA",
  "place_id": "ChIJw6noUxD2wokRnj5_OciSlA8",
  "lat": 40.8020169,
  "lng": -73.9502393,
  "city": "New York",
  "state": "NY",
  "zip_code": "10026",
  "reviews": [
    {
      "author": "John Doe",
      "rating": 5,
      "text": "Beautiful mosque with a welcoming community.",
      "time": "a week ago"
    },
    {
      "author": "Aisha K.",
      "rating": 4,
      "text": "Great place for Jummah prayer.",
      "time": "2 months ago"
    }
  ]
}
📜 Scripts
1. Scraper – nyc_mosques.py
- Queries mosques across NYC boroughs.
- Calls Google Places Text Search API → gets place IDs.
- Calls Google Places Details API → fetches address, coordinates, and top 3 reviews.
- Saves results to MongoDB Atlas (upsert by place_id) and CSV file.
2. Backend – main.py
FastAPI service with endpoints:
Endpoints:
GET / → Welcome message
GET /mosques → List all mosques, filter by city/state/zip
GET /search?name= → Search by mosque name
GET /mosque/{place_id} → Get full details of one mosque
GET /reviews/{place_id} → Get top 3 reviews of one mosque
POST /mosque → Add a new mosque
PATCH /mosque/{place_id} → Update mosque info
DELETE /mosque/{place_id} → Delete mosque
🔑 Setup Instructions
1. Clone Project
   git clone <repo-url>
   cd nyc_mosques

2. Create Virtual Environment
   python -m venv .venv
   source .venv/bin/activate (Linux/Mac)
   .venv\Scripts\activate (Windows)

3. Install Dependencies
   pip install -r requirements.txt

4. Set Environment Variables in .env
   GOOGLE_API_KEY=your_google_places_api_key
   MONGO_URI=your_mongodb_atlas_uri

5. Run Scraper
   python nyc_mosques.py

6. Run API Server
   uvicorn main:app --reload

7. Test with Postman
   Example: http://127.0.0.1:8000/mosques?city=New York
   Example: http://127.0.0.1:8000/reviews/{place_id}
📊 Usage for Data Analysts
- Analyze distribution of mosques by borough/city/ZIP.
- Compare review sentiments (positive/negative) for community insights.
- Use as a search engine backend for mosque-finding apps.
⚠️ Notes
- Google Places API has usage limits; heavy scraping may incur billing.
- Reviews are limited to top 3 per mosque (as per project design).
- MongoDB is updated with upserts to avoid duplicate entries.
