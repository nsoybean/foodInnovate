import requests
import json


with open("reviews.json") as f:
    reviews = json.load(f)

resp = requests.post(
    "http://localhost:8000/analyze",
    json={"industry": "F&B", "reviews": reviews[0:5]},
)
print(resp.json())

# requests.post(
#     "http://localhost:8000/analyze",
#     json={
#         "industry": "F&B",
#         "url": "https://www.google.com/maps/place/Priv%C3%A9+Katong/@1.3005026,103.8411422,13.58z/data=!3m1!5s0x31da1873ad5fdb95:0xae0dd676fccd02ed!4m10!1m2!2m1!1zUHJpdsOp!3m6!1s0x31da19d1eb803f75:0x600404a326e4b674!8m2!3d1.3052002!4d103.9050645!15sCgZQcml2w6laCCIGcHJpdsOpkgEKcmVzdGF1cmFudOABAA!16s%2Fg%2F11rp41p_4d?entry=ttu",
#     },
# )

# resp = requests.get("http://localhost:8000/summary")
# print(resp.json())

# requests.post("http://localhost:8000/clear")

# from apify_client import ApifyClient

# APIFY_TOKEN = "apify_api_ATqx4ubArj7TF3UW4HaH9hiFy60bVu30MP9K"


# def scrape_reviews(url, num_reviews=10):
#     # Initialize the ApifyClient with your API token
#     client = ApifyClient(APIFY_TOKEN)

#     # Prepare the Actor input
#     run_input = {
#         "startUrls": [{"url": url}],
#         "maxReviews": num_reviews,
#         "reviewsSort": "newest",
#         "language": "en",
#         "personalData": True,
#     }

#     # Run the Actor and wait for it to finish
#     run = client.actor("Xb8osYTtOjlsgI6k9").call(run_input=run_input)

#     # Fetch and print Actor results from the run's dataset (if there are any)
#     items = []
#     for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#         items.append(item)

#     with open("output.json", "w") as f:
#         json.dump(items, f)


# scrape_reviews(
#     "https://www.google.com/maps/place/Priv%C3%A9+Katong/@1.3005026,103.8411422,13.58z/data=!3m1!5s0x31da1873ad5fdb95:0xae0dd676fccd02ed!4m10!1m2!2m1!1zUHJpdsOp!3m6!1s0x31da19d1eb803f75:0x600404a326e4b674!8m2!3d1.3052002!4d103.9050645!15sCgZQcml2w6laCCIGcHJpdsOpkgEKcmVzdGF1cmFudOABAA!16s%2Fg%2F11rp41p_4d?entry=ttu"
# )
