import streamlit as st
import pandas as pd
import numpy as np
import uuid
import random
import time
import plotly.express as px
import matplotlib.pyplot as plt
from itertools import chain, cycle
from collections import Counter
import requests
import json

# API_URL = "8.222.140.205:8000"
API_URL = "0.0.0.0:8000"
# global variable to store json data in memory
jsonData = None

def getJsonData():
    if jsonData is None:
        return None
    else: 
        return jsonData


st.title("GenieSpark: Your AI shopping assistant.")

color_cycle = cycle(px.colors.qualitative.Plotly)


def simulate_processing(duration=1):
    """
    Simulates the processing of data.
    The duration parameter allows you to set how long the simulation runs.
    """
    # Simulate a time-consuming process
    time.sleep(duration)
    return "Processing completed."


# Function to generate a random review
def generate_random_review():
    sentiment_choices = ["positive", "negative"]
    emotion_choices = ["sad", "happy"]
    tag_pool = ["N1", "N2", "N3", "N4", "N5"]  # Add more tags as needed
    gender_choices = ["guy", "girl"]

    review = {
        "id": str(uuid.uuid4()),  # Generates a random UUID for each review
        "sentiment": random.choice(sentiment_choices),
        "emotion": random.choice(emotion_choices),
        "tags": random.sample(tag_pool, 2),  # Picks 2 random tags from the pool
        "gender": random.choice(gender_choices),
    }

    return review


def reviews_to_dataframe(reviews):
    df = pd.DataFrame(reviews)
    return df


def plot_metric_distribution(df, column_name, chart_title):
    if column_name in df.columns:
        data = None
        # Check if the column contains lists
        if isinstance(df[column_name].iloc[0], list):
            # Flatten the list of lists and create a DataFrame for Plotly
            all_elements = list(chain.from_iterable(df[column_name].dropna()))
            counts = dict(Counter(all_elements))
            data = pd.DataFrame(list(counts.items()), columns=[column_name, "Counts"])
        else:
            # For non-list columns, calculate the value counts and reset the index to use with Plotly
            data = df[column_name].value_counts().reset_index()
            data.columns = [column_name, "Counts"]

        # pie chart
        pieChart = px.pie( data, values='Counts', names=column_name, hole=.3, title=chart_title)
        st.plotly_chart(pieChart, use_container_width=True)

        # Use Plotly Express to create the bar chart
        # fig = px.bar(
        #     data,
        #     x="Counts",
        #     y=column_name,
        #     orientation="h",
        #     title=chart_title,
        #     labels={"Counts": "Counts", column_name: column_name.capitalize()},
        #     color="Counts",
        #     color_continuous_scale=px.colors.sequential.Viridis,
        # )
        # fig.update_layout(xaxis_title="Counts", yaxis_title=column_name.capitalize())
        # st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(
            f"The specified column '{column_name}' does not exist in the DataFrame."
        )


def display_qualitative_insights(prompt_response):
    markdown_template = """
    ### Qualitative Insights

    **Insight Summary:**
    - {insights}

    **Detailed Analysis:**
    {detailed_analysis}

    **Recommendations:**
    - {recommendations}
    """
    formatted_markdown = markdown_template.format(
        insights="\n- ".join(
            prompt_response.get("insights", ["No insights provided."])
        ),
        detailed_analysis=prompt_response.get(
            "detailed_analysis", "No detailed analysis provided."
        ),
        recommendations="\n- ".join(
            prompt_response.get("recommendations", ["No recommendations provided."])
        ),
    )
    st.markdown(formatted_markdown)


uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    try:
        # Read JSON file
        jsonData = json.load(uploaded_file)
        on = st.toggle('Preview JSON data', False)
        if on:
            if uploaded_file is not None:
                st.write(jsonData[0])
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON file.")


industry_options = ("F&B", "E-commerce")
option = st.selectbox(
    "Industry",
    index=None,
    options=industry_options,
    placeholder="Choose an Industry",
)

# st.write(option)


if jsonData is not None:
    number = st.number_input("Choose number of reviews to analyze", value=len(jsonData), placeholder="Number of reviews")


if st.button('Analyze!'):
    reviewData = getJsonData()
    if reviewData is None:
        st.error("Missing JSON data. Please upload one to begin.") 
        st.stop()
    headers = {'Content-type': 'application/json'}
    
    payloadDict = {
        "category": option,
        "reviews": jsonData[:number],
    }   

    # convert into JSON:
    payloadJson = json.dumps(payloadDict)

    with st.spinner("Analyzing..."):
        # response = requests.post(f"http://{API_URL}/testReviewPayload", json=reviewData[:number],headers=headers) 
        response = requests.post(f"http://{API_URL}/analyze", json=payloadDict,headers=headers)


if st.button('Get insights!'):
    response = requests.get(f"http://{API_URL}/summary") 
    st.write(response.json())
    # df_reviews = reviews_to_dataframe(response['sentiment'])
    # st.write(f"sentiment: {df_reviews}")


if st.button("Generate Insights"):
    if uploaded_file is None and option not in industry_options:
        st.warning("Please upload a file or select an industry to continue.")
    else:
        with st.spinner("Generating insights..."):
            # Simulate processing
            simulate_processing()
            # Generate a list of 100 random reviews for demonstration
            reviews = [generate_random_review() for _ in range(100)]
            df_reviews = reviews_to_dataframe(reviews)

            tab1, tab2 = st.tabs(["Quantitative Data", "Qualitative Insights"])
            with tab1:
                # Iterate over all columns except 'id' and generate charts
                for column in df_reviews.columns:
                    if column != "id":  # Skip the 'id' column
                        chart_title = f"{column.capitalize()} Distribution"
                        plot_metric_distribution(df_reviews, column, chart_title)

            with tab2:
                example_prompt_response = {
                    "insights": [
                        "Significant mention of customer service quality",
                        "Product durability concerns",
                    ],
                    "detailed_analysis": "Upon reviewing customer feedback, it was observed that customer service quality was consistently praised, while there were several mentions of concerns regarding the durability of the product.",
                    "recommendations": [
                        "Investigate product materials for potential improvements",
                        "Highlight customer service excellence in marketing materials",
                    ],
                }
                display_qualitative_insights(example_prompt_response)



st.divider()
st.write('Developers Only')
if st.button('Test /ping'):
    response = requests.get(f"http://{API_URL}/ping") 
    st.write(f"server: {response.json()}")


if st.button('Clear!'):
    response = requests.post(f"http://{API_URL}/clear")
    st.write(f"server: {response.json()}")