from datetime import datetime
import psycopg2
import requests
from fastapi import FastAPI, Request


app = FastAPI()


DB_USER = "mavic"
DB_PASSWORD = "UugwZLn73i3X"
DB_HOST = "gp-gs5zw2z27av4l87kuo-master.gpdbmaster.singapore.rds.aliyuncs.com"
DB_PORT = 5432
DB_DATABASE = "mavic"


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
        results = analyze_review(review)

        text = review["text"]
        score = review["totalScore"]
        stars = review["stars"]
        date = datetime.fromisoformat(review["publishedAtDate"])
        sentiment = ""
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


@app.post("/clear")
async def clear():
    with conn.cursor() as cur:
        cur.execute("DELETE FROM review")
        conn.commit()


def analyze_review(review):
    result = requests.post(
        "http://quickstart-20240307-w5py.5531209519297534.ap-southeast-1.pai-eas.aliyuncs.com/",
        data={
            "prompt": "List the largest islands which begin with letter 's'.",
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
    response = result.json()

    return {}


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
