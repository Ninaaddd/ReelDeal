"""
Movie Recommender System - Streamlit App
Uses FAISS for efficient recommendations
Data loaded from GitHub releases
"""

from PIL import Image
import streamlit as st
import pickle
import pandas as pd
import requests
import time
from dotenv import load_dotenv
import os
import faiss
from github_release_manager import GitHubReleaseManager

load_dotenv()
API_KEY = os.getenv('API_KEY')

# Page configuration
icon = Image.open("assets/movie.png")
st.set_page_config(
    page_title="Reel Deal",
    page_icon=icon,
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #E50914;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #999;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_data_from_github():
    """Download and load data from GitHub releases"""

    # Check if files exist locally
    files_needed = ['movies_dict.pkl', 'movies.index', 'vectorizer.pkl']
    files_exist = all([os.path.exists(f'data/{f}') for f in files_needed])

    if not files_exist:
        try:
            manager = GitHubReleaseManager()
            tag = os.getenv('GITHUB_RELEASE_TAG', 'v1.0.0')

            with st.spinner('Downloading latest movie data... This may take a minute.'):
                success = manager.download_files(tag, destination_dir='data')

            if not success:
                st.error("Failed to download data from GitHub releases.")
                st.stop()

        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Make sure GITHUB_TOKEN and GITHUB_REPO are set in .env file")
            st.stop()

    # Load the data
    try:
        movies_dict = pickle.load(open('data/movies_dict.pkl', 'rb'))
        movies_df = pd.DataFrame(movies_dict)
        index = faiss.read_index('data/movies.index')
        return movies_df, index
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        st.stop()


def fetch_poster(movie_id):
    """Fetch movie poster from TMDb API"""
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'

    for i in range(5):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')

            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            return None

        except requests.exceptions.RequestException:
            if i < 4:
                time.sleep(2 ** i)
            else:
                return None


def recommend(movie, movies_df, index, k=5):
    """Recommend similar movies using FAISS"""
    try:
        # Find the movie index
        movie_indices = movies_df[movies_df['title'] == movie].index

        if len(movie_indices) == 0:
            return [], []

        movie_index = movie_indices[0]

        # Get the movie's vector from the index
        query_vector = index.reconstruct(int(movie_index)).reshape(1, -1)

        # Search for k+1 nearest neighbors (including itself)
        distances, indices = index.search(query_vector, k + 1)

        # Skip the first result (the movie itself)
        recommended_indices = indices[0][1:k+1]

        recommended_movies = []
        recommended_posters = []

        for idx in recommended_indices:
            movie_id = movies_df.iloc[idx].movie_id
            title = movies_df.iloc[idx].title
            recommended_movies.append(title)
            poster = fetch_poster(movie_id)
            recommended_posters.append(poster)

        return recommended_movies, recommended_posters

    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []

# Main App


def main():
    # Header
    st.markdown('<div class="main-header">🎬 Reel Deal</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Discover your next favorite movie</div>',
                unsafe_allow_html=True)

    # Load data
    with st.spinner('Loading movie database...'):
        movies, faiss_index = load_data_from_github()

    # Movie selection
    col1, col2 = st.columns([3, 1])

    with col1:
        selected_movie = st.selectbox(
            'Select a movie you like:',
            movies['title'].values,
            index=0
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        recommend_button = st.button(
            '🎯 Get Recommendations', type="primary", use_container_width=True)

    # Show recommendations
    if recommend_button:
        with st.spinner('Finding similar movies...'):
            names, posters = recommend(selected_movie, movies, faiss_index)

        if names:
            st.success('✨ Here are your recommendations:')
            st.write("")

            cols = st.columns(5)

            for idx, col in enumerate(cols):
                with col:
                    st.markdown(f"**{names[idx]}**")
                    if posters[idx]:
                        st.image(posters[idx], use_column_width=True)
                    else:
                        st.info("🎬 No poster available")
        else:
            st.warning(
                "Could not generate recommendations. Please try another movie.")

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption(f"📊 {len(movies)} movies in database")
    with col2:
        st.caption("🔄 Data updates weekly")
    with col3:
        st.caption("🎥 Powered by TMDb API")


if __name__ == "__main__":
    main()
