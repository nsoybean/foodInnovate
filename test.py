import requests
import json


with open("reviews.json") as f:
    reviews = json.load(f)

requests.post(
    "http://localhost:8000/analyze",
    json={"category": "eCommerce", "reviews": [reviews[0]]},
)

# requests.post("http://localhost:8000/clear")
