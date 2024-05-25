import streamlit as st
import tweepy
from textblob import TextBlob
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide", page_title="Twitter Opinion Analyzer")

# Twitter API credentials
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAHThtwEAAAAAwqSEZjldqLpDWKRApy6MKjx90so%3DJHBTQQW9q33IZuC0ZWrI701Owo86rlxQXJWi8BBQPpU6a5KaHt'  # Replace with your actual bearer token

# Authenticate with Twitter API v2
client = tweepy.Client(bearer_token=bearer_token)

# Streamlit App Setup
st.title("Twitter Opinion Analyzer")

# Input for topic
topic = st.text_input("Enter a topic to search for:")

if st.button("Analyze"):
    if topic:
        with st.spinner("Fetching tweets..."):
            try:
                # Use the recent search endpoint to fetch tweets
                query = f"{topic} -is:retweet lang:en"
                response = client.search_recent_tweets(query=query, max_results=100, tweet_fields=['text'])
                tweets = response.data
                if tweets:
                    tweet_data = [{'text': tweet.text, 'sentiment': TextBlob(tweet.text).sentiment.polarity} for tweet in tweets]
                    df = pd.DataFrame(tweet_data)
                    
                    # Display tweets
                    st.subheader(f"Fetched {len(df)} tweets")
                    st.write(df[['text', 'sentiment']])
                    
                    # Sentiment analysis visualization
                    fig = px.histogram(df, x="sentiment", nbins=20, title='Sentiment Analysis')
                    st.plotly_chart(fig)
                else:
                    st.warning("No tweets found for the given topic.")
            except tweepy.TweepyException as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a topic to search for.")
