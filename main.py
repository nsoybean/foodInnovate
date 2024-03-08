from apify_client import ApifyClient
from datetime import datetime
import json
import psycopg2
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


APIFY_TOKEN = "apify_api_ATqx4ubArj7TF3UW4HaH9hiFy60bVu30MP9K"
APIFY_CACHE = {}

DB_USER = "mavic"
DB_PASSWORD = "UugwZLn73i3X"
DB_HOST = "gp-gs5zw2z27av4l87kuo-master.gpdbmaster.singapore.rds.aliyuncs.com"
DB_PORT = 5432
DB_DATABASE = "mavic"

# qwen 1.7B chat
PAI_HOST = "http://quickstart-20240307-w5py.5531209519297534.ap-southeast-1.pai-eas.aliyuncs.com/"
PAI_TOKEN = "NGUxOGFhODhmMGIyOTZiNzkzNWUzNzE2MzQzNzk5OWMwMGViYzY2NA=="

# qwen 7B chat
# PAI_HOST = "http://quickstart-20240308-sh2b.5531209519297534.ap-southeast-1.pai-eas.aliyuncs.com/"
# PAI_TOKEN = "ZGFmOTVmYzZhYzk5MmFjZDEyNGZiMmNkMTkyNWMxYjA5YjliMzJlMw=="


app = FastAPI()

conn = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_DATABASE,
)


@app.post("/analyze")
async def analyze(req: Request):
    await clear()

    data = await req.json()

    industry = data["industry"]
    if "url" in data:
        reviews = scrape_reviews(data["url"])
    else:
        reviews = data["reviews"]

    for review in reviews:
        if not review["text"]:
            continue

        # prompt
        sentiment = ""
        emotion = ""
        quality_of_food_beverage = ""
        value_for_money = ""
        customer_service = ""
        safety_and_hygiene = ""
        loyalty_and_rewards = ""
        accessibility_and_convenience = ""
        social_responsibility = ""
        brand_love = ""
        try:
            results = analyze_review(review)
            if results is not None:
                print(results)
                sentiment = results["sentiment"]
                emotion = results["emotion"]
                quality_of_food_beverage = results["quality_of_food_beverage"]
                value_for_money = results["value_for_money"]
                customer_service = results["customer_service"]
                safety_and_hygiene = results["safety_and_hygiene"]
                loyalty_and_rewards = results["loyalty_and_rewards"]
                accessibility_and_convenience = results["accessibility_and_convenience"]
                social_responsibility = results["social_responsibility"]
                brand_love = results["brand_love"]
        except Exception as ex:
            print(ex)
            pass

        text = review["text"]
        score = review["totalScore"]
        stars = review["stars"]
        date = datetime.fromisoformat(review["publishedAtDate"])
        gender = ""
        name = review["name"]
        tags = []
        if quality_of_food_beverage:
            tags.append("quality_of_food_beverage")
        if value_for_money:
            tags.append("value_for_money")
        if customer_service:
            tags.append("customer_service")
        if safety_and_hygiene:
            tags.append("safety_and_hygiene")
        if loyalty_and_rewards:
            tags.append("loyalty_and_rewards")
        if accessibility_and_convenience:
            tags.append("accessibility_and_convenience")
        if social_responsibility:
            tags.append("social_responsibility")
        if brand_love:
            tags.append("brand_love")

        # insert
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO review
                (sentiment, emotion, gender, name, text, score, stars, date, tags)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    sentiment,
                    emotion,
                    gender,
                    name,
                    text,
                    score,
                    stars,
                    date,
                    tags,
                ),
            )
            conn.commit()

    return None


# test health
@app.get("/ping")
async def health(req: Request):
    return "hehe you found me"


# test receive single json review payload
@app.post("/testReviewPayload")
async def testReviewPayload(req: Request):
    data = await req.json()
    print(f"Received {len(data)} reviews ...")
    return {f"i received {len(data)} reviews"}


@app.get("/summary")
async def summary():
    summary = {
        "sentiment": {
            "good": 0,
            "bad": 0,
            "neutral": 0,
        },
        "emotion": {
            "happy": 0,
            "angry": 0,
            "disappointed": 0,
            "sad": 0,
            "neutral": 0,
        },
        "tags": {},
        "wordCloud": {},
    }
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM review")
        reviews = cur.fetchall()
        for row in reviews:
            id = row[0]
            sentiment = row[1]
            emotion = row[2]
            name = row[4]
            text = row[5]
            score = row[6]
            stars = row[7]
            date = row[8]
            tags = row[9]

            if sentiment in summary["sentiment"]:
                summary["sentiment"][sentiment] += 1
            else:
                summary["sentiment"]["neutral"] += 1

            if emotion in summary["emotion"]:
                summary["emotion"][emotion] += 1
            else:
                summary["emotion"]["neutral"] += 1

            for tag in tags:
                if tag in summary["tags"]:
                    summary["tags"][tag] += 1
                else:
                    summary["tags"][tag] = 1

            words = text.split(" ")
            for word in words:
                word = word.lower().replace(",", "").replace(".", "")
                if len(word) > 3:
                    if word in summary["wordCloud"]:
                        summary["wordCloud"][word] += 1
                    else:
                        summary["wordCloud"][word] = 1

    return JSONResponse(content=summary)


@app.post("/clear")
async def clear():
    with conn.cursor() as cur:
        cur.execute("DELETE FROM review")
        conn.commit()


def scrape_reviews(url, num_reviews=10):
    key = url + "_" + str(num_reviews)
    if key in APIFY_CACHE:
        return APIFY_CACHE[key]

    # Initialize the ApifyClient with your API token
    client = ApifyClient(APIFY_TOKEN)

    # Prepare the Actor input
    run_input = {
        "startUrls": [{"url": url}],
        "maxReviews": num_reviews,
        "reviewsSort": "newest",
        "language": "en",
        "personalData": True,
    }

    # Run the Actor and wait for it to finish
    run = client.actor("Xb8osYTtOjlsgI6k9").call(run_input=run_input)

    # Fetch and print Actor results from the run's dataset (if there are any)
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    APIFY_CACHE[key] = items

    return items


def analyze_review(review):
    if not review["text"]:
        return None

    print("Analyzing:\n" + review["text"] + "...")

    text = review["text"]

    prompt = (
        """
    This is a customer review about a restaurant chain, delimited by ###
    ###
    %s
    ###

    Act like a data analyst and follow the instructions below:
    - Analyze the review and determiner the customer's sentiment. Select from these options: good, neutral, bad // reviewSentiment
    - Analyze the review and determine the customer's emotion. Select from these options: happy, angry, disappointed, sad, neutral // emotion
    - Is the customer talking about quality of food/beverage? yes or no // qualityOfFoodBeverage
    - Is the customer talking about value for money? yes or no // valueForMoney
    - Is the customer talking about customer service? yes or no // customerService
    - Is the customer talking about safety and hygiene? yes or no // safetyAndHygiene
    - Is the customer talking about loyalty and rewards? yes or no // loyaltyAndRewards
    - Is the customer talking about accessibility and convenience? yes or no // accessibilityAndConvenience
    - Is the customer talking about social responsibility? yes or no // socialResponsibility
    - Is the customer talking about his/her love for the brand? yes or no // brandLove

    Please reply in English and output as JSON object using the following format:
    {
      "reviewSentiment": "",
      "emotion": "",
      "qualityOfFoodBeverage": "",
      "valueForMoney": "",
      "customerService": "",
      "safetyAndHygiene": "",
      "loyaltyAndRewards": "",
      "accessibilityAndConvenience": "",
      "socialResponsibility": "",
      "brandLove": ""
    }
    """
        % text
    )

    result = requests.post(
        PAI_HOST,
        data={
            "prompt": prompt,
            "system_prompt": "",
            "top_k": 1,
            "top_p": 1,
            "temperature": 1,
            "max_new_tokens": 4096,
            "use_stream_chat": False,
            "history": [["question", "answer"]],
        },
        headers={"Authorization": PAI_TOKEN},
    )
    response = result.json()["response"]
    response = response.replace("```json", "")
    response = response.replace("```", "")
    start = response.find("{")
    end = response.find("}")
    response = response[start : end + 1]
    print(response)
    results = json.loads(response)

    yes_no_mappings = {
        "yes": "yes",
        "good": "yes",
        "positive": "yes",
        "very positive": "yes",
        "excellent": "yes",
        "affordable": "yes",
        "highly recommended": "yes",
        "no": "no",
        "bad": "no",
        "negative": "no",
        "poor": "no",
        "terrible": "no",
        "neutral": "no",
        "average": "no",
    }

    good_neutral_bad_mappings = {
        "yes": "good",
        "good": "good",
        "positive": "good",
        "excellent": "good",
        "affordable": "good",
        "highly recommended": "good",
        "no": "bad",
        "bad": "bad",
        "negative": "bad",
        "poor": "bad",
        "terrible": "bad",
        "neutral": "neutral",
        "average": "neutral",
    }

    if "reviewSentiment" in results:
        sentiment = results["reviewSentiment"]
    elif "review_sentiment" in results:
        sentiment = results["review_sentiment"]
    else:
        sentiment = ""

    if "emotion" in results:
        emotion = results["emotion"]
    else:
        emotion = ""

    if "qualityOfFoodBeverage" in results:
        quality_of_food_beverage = results["qualityOfFoodBeverage"]
    elif "quality_of_food_beverage" in results:
        quality_of_food_beverage = results["quality_of_food_beverage"]
    else:
        quality_of_food_beverage = ""

    if "valueForMoney" in results:
        value_for_money = results["valueForMoney"]
    elif "value_for_money" in results:
        value_for_money = results["value_for_money"]
    else:
        value_for_money = ""

    if "customerService" in results:
        customer_service = results["customerService"]
    elif "customer_service" in results:
        customer_service = results["customer_service"]
    else:
        customer_service = ""

    if "safetyAndHygiene" in results:
        safety_and_hygiene = results["safetyAndHygiene"]
    elif "safety_and_hygiene" in results:
        safety_and_hygiene = results["safety_and_hygiene"]
    else:
        safety_and_hygiene = ""

    if "loyaltyAndRewards" in results:
        loyalty_and_rewards = results["loyaltyAndRewards"]
    elif "loyalty_and_rewards" in results:
        loyalty_and_rewards = results["loyalty_and_rewards"]
    else:
        loyalty_and_rewards = ""

    if "accessibilityAndConvenience" in results:
        accessibility_and_convenience = results["accessibilityAndConvenience"]
    elif "accessibility_and_convenience" in results:
        accessibility_and_convenience = results["accessibility_and_convenience"]
    else:
        accessibility_and_convenience = ""

    if "socialResponsibility" in results:
        social_responsibility = results["socialResponsibility"]
    elif "social_responsibility" in results:
        social_responsibility = results["social_responsibility"]
    else:
        social_responsibility = ""

    if "brandLove" in results:
        brand_love = results["brandLove"]
    elif "brand_love" in results:
        brand_love = results["brand_love"]
    else:
        brand_love = ""

    sentiment = (
        good_neutral_bad_mappings[sentiment.lower()]
        if sentiment.lower() in good_neutral_bad_mappings
        else "neutral"
    )
    emotion = emotion.lower()
    quality_of_food_beverage = (
        yes_no_mappings[quality_of_food_beverage.lower()]
        if quality_of_food_beverage.lower() in yes_no_mappings
        else "no"
    )
    value_for_money = (
        yes_no_mappings[value_for_money.lower()]
        if value_for_money.lower() in yes_no_mappings
        else "no"
    )
    customer_service = (
        yes_no_mappings[customer_service.lower()]
        if customer_service.lower() in yes_no_mappings
        else "no"
    )
    safety_and_hygiene = (
        yes_no_mappings[safety_and_hygiene.lower()]
        if safety_and_hygiene.lower() in yes_no_mappings
        else "no"
    )
    loyalty_and_rewards = (
        yes_no_mappings[loyalty_and_rewards.lower()]
        if loyalty_and_rewards.lower() in yes_no_mappings
        else "no"
    )
    accessibility_and_convenience = (
        yes_no_mappings[accessibility_and_convenience.lower()]
        if accessibility_and_convenience.lower() in yes_no_mappings
        else "no"
    )
    social_responsibility = (
        yes_no_mappings[social_responsibility.lower()]
        if social_responsibility.lower() in yes_no_mappings
        else "no"
    )
    brand_love = (
        yes_no_mappings[brand_love.lower()]
        if brand_love.lower() in yes_no_mappings
        else "no"
    )

    return {
        "sentiment": sentiment,
        "emotion": emotion,
        "quality_of_food_beverage": quality_of_food_beverage,
        "value_for_money": value_for_money,
        "customer_service": customer_service,
        "safety_and_hygiene": safety_and_hygiene,
        "loyalty_and_rewards": loyalty_and_rewards,
        "accessibility_and_convenience": accessibility_and_convenience,
        "social_responsibility": social_responsibility,
        "brand_love": brand_love,
    }


# def analyze_reviews():
#     summary = {
#         "sentiment": {
#             "good": 0,
#             "bad": 0,
#             "neutral": 0,
#         },
#         "emotion": {
#             "happy": 0,
#             "angry": 0,
#             "disappointed": 0,
#             "sad": 0,
#             "neutral": 0,
#         },
#         "tags": {},
#         "wordCloud": {},
#     }
#     with conn.cursor() as cur:
#         cur.execute("SELECT * FROM review")
#         reviews = cur.fetchall()
#         for row in reviews:
#             id = row[0]
#             sentiment = row[1]
#             emotion = row[2]
#             name = row[4]
#             text = row[5]
#             score = row[6]
#             stars = row[7]
#             date = row[8]
#             tags = row[9]

#             if sentiment in summary["sentiment"]:
#                 summary["sentiment"][sentiment] += 1
#             else:
#                 summary["sentiment"]["neutral"] += 1

#             if emotion in summary["emotion"]:
#                 summary["emotion"][emotion] += 1
#             else:
#                 summary["emotion"]["neutral"] += 1

#             for tag in tags:
#                 if tag in summary["tags"]:
#                     summary["tags"][tag] += 1
#                 else:
#                     summary["tags"][tag] = 1

#             words = text.split(" ")
#             for word in words:
#                 word = word.lower().replace(",", "").replace(".", "")
#                 if len(word) > 3:
#                     if word in summary["wordCloud"]:
#                         summary["wordCloud"][word] += 1
#                     else:
#                         summary["wordCloud"][word] = 1

#     prompt = (
#         """
#     These are customer reviews about a restaurant chain with their analysis, delimited by ###
#     ###
#     %s
#     ###

#     Act like a data analyst and follow the instructions below:
#     - Give an insights of how the resturant chain can improve in  // improvement

#     Please reply in English and output as JSON object using the following format:
#     {
#       "insights1": ""
#     }
#     """
#         % text
#     )

#     return JSONResponse(content=summary)


def main():
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM review
        """
    )
    for table in cursor.fetchall():
        print(table)


if __name__ == "__main__":
    main()
