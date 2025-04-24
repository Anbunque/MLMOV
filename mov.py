import nltk
nltk.download('vader_lexicon')
import random

import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

# TMDB API KEY (replace with your valid one)
TMDB_API_KEY = "db268144f4930eb937f8addef2760ca2"

# Mood to Genre Mapping
mood_genre_map = {
    "joy": ["Adventure", "Comedy"],
    "anger": ["Comedy", "Adventure"],
    "neutral": ["Comedy", "Adventure", "Drama", "Romance", "anger", "Fantasy", "Mystery"],
    "calm": ["Comedy", "Mystery"],
    "sadness": ["Comedy", "Drama"],
}

# Genre name to ID (TMDB specific)
genre_ids = {
    "Comedy": 35,
    "Adventure": 12,
    "Drama": 18,
    "Romance": 10749,
    "anger": 28,
    "Fantasy": 14,
    "Mystery": 9648,
    "Inspiration": 9715,
}

# Get genre-matched movie recommendations from TMDB
def get_movies_by_genres(genre_list):
    genre_id_str = ",".join([str(genre_ids[g]) for g in genre_list])
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id_str}&sort_by=popularity.desc"

    try:
        response = requests.get(url, timeout=10)  # No proxies here
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            return random.sample(results, min(10, len(results)))
        else:
            st.error(f"TMDB API error: {response.status_code} — {response.reason}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {e}")
        return []

# Analyze sentiment
def detect_mood(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    if compound >= 0.6:
        return "joy"
    elif compound >= 0.2:
        return "calm"
    elif -0.2 < compound < 0.2:
        return "neutral"
    elif compound <= -0.4:
        return "anger"
    else:
        return "sadness"

# Streamlit UI
st.set_page_config(page_title="MoodFlix 🎬", page_icon="🎭")
st.title("😊 MoodFlix - Emotion-Aware Movie Recommender")

user_input = st.text_input("How are you feeling today? (Type your mood)")
search = st.button("🔍 Search")

if search and user_input:
    mood = detect_mood(user_input)
    st.subheader(f"Detected Mood: **{mood.capitalize()}**")
    genre_choices = mood_genre_map[mood]
    st.write(f"Recommended genres for your mood: {', '.join(genre_choices)}")

    movies = get_movies_by_genres(genre_choices)

    if movies:
        st.subheader("🎬 Recommended Movies:")
        for movie in movies:
            st.markdown(f"**{movie['title']}**")
            if movie.get("poster_path"):
                st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", width=150)
            st.caption(movie['overview'][:150] + "...")
    else:
        st.error("No movie recommendations found.")
