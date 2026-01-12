import streamlit as st
import pickle
import pandas as pd
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

# Set the page title
st.set_page_config(page_title="Reel Deal", page_icon=movie.png)


def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    for i in range(5):  # Retry up to 5 times
        try:
            response = requests.get(url, timeout=10)
            # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            response.raise_for_status()
            data = response.json()
            poster_path = data['poster_path']
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
        except requests.exceptions.RequestException:
            # print(f"Attempt {i + 1} failed: {e}")
            if i < 4:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)),
                         reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # fetch poster from API
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters


movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.header('Movie Recommender System')

selected_movie_name = st.selectbox('Select a movie', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
