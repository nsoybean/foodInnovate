from datetime import datetime
import json
import psycopg2
import requests
from fastapi import FastAPI, Request


app = FastAPI()


DB_USER = "mavic"
DB_PASSWORD = "UugwZLn73i3X"
DB_HOST = "gp-gs5zw2z27av4l87kuo-master.gpdbmaster.singapore.rds.aliyuncs.com"
DB_PORT = 5432
DB_DATABASE = "mavic"

PAI_HOST = "http://quickstart-20240307-w5py.5531209519297534.ap-southeast-1.pai-eas.aliyuncs.com/"


conn = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_DATABASE,
)


@app.post("/analyze")
async def analyze(req: Request):
    data = await req.json()

    category = data["category"]
    reviews = data["reviews"]

    for review in reviews:
        # prompt
        try:
            results = analyze_review(review)
            sentiment = results["sentiment"]
        except:
            sentiment = ""

        text = review["text"]
        score = review["totalScore"]
        stars = review["stars"]
        date = datetime.fromisoformat(review["publishedAtDate"])
        emotion = ""
        gender = ""
        name = ""

        # insert
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO review (sentiment, emotion, gender, name, text, score, stars, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (sentiment, emotion, gender, name, text, score, stars, date),
            )
            conn.commit()

    return None

# test health
@app.get("/ping")
async def health(req:Request):
     return 'hehe you found me'

# test receive single json review payload
@app.post("/testReviewPayload")
async def testReviewPayload(req: Request):
    data = await req.json()
    print(data)
    # print(f"Received {data.length()} reviews ...")
    # if data.length() > 0:
        # print(f"First review: {data[0]}")



@app.post("/clear")
async def clear():
    with conn.cursor() as cur:
        cur.execute("DELETE FROM review")
        conn.commit()


def analyze_review(review):
    if not review['text']:
        return {"sentiment": "", "review_type": ""}
    
    print(f"Analyzing {review['text']} ...")

    text = review["text"]

    prompt = (
        """
    These are customer reviews about Yakun delimited by ###:
    ###
    %s
    ###
    
    Here is the list of review types delimited by ~~~:
    ~~~
    Quality of Food/Beverage
    Value for Money
    Staff and Customer Service
    Operational Efficiency
    Safety and Hygiene
    Product Availability
    Loyalty and Rewards
    Accessibility and Convenience
    Social Responsibility
    Dietary and Inclusivity Options
    Brand Reputation and Trust
    ~~~

    Act like a data analyst and complete the following action for the above review:
    1. Analyze the review sentiment and select from these options: good, neutral, bad // reviewSentiment
    2. Assign a review type from the list delimited by ~~~ // reviewType

    Please output as JSON object using the following format:
    {
      "reviewSentiment": "",
      "reviewType": ""
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
            "top_p": 0.9,
            "temperature": 0.8,
            "max_new_tokens": 5120,
            "use_stream_chat": False,
            "history": [["question", "answer"]],
        },
        headers={
            "Authorization": "NGUxOGFhODhmMGIyOTZiNzkzNWUzNzE2MzQzNzk5OWMwMGViYzY2NA=="
        },
    )
    response = result.json()["response"]
    response = response.replace("```json", "")
    response = response.replace("```", "")
    results = json.loads(response)

    sentiment = ""
    if "reviewSentiment" in results:
        sentiment = results["reviewSentiment"]
    elif "review_sentiment" in results:
        sentiment = results["review_sentiment"]

    review_type = ""
    if "reviewType" in results:
        review_type = results["reviewType"]
    elif "review_type" in results:
        review_type = results["review_type"]

    sentiment = sentiment.lower()
    review_type = review_type.lower()
    print(sentiment)
    print(review_type)

    return {"sentiment": sentiment, "review_type": review_type}


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
