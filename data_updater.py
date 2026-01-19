"""
Data Updater - Fetches movies from TMDb and processes them
Improved version with better error handling and retry logic
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import faiss
import pickle
import os
from dotenv import load_dotenv
import time

load_dotenv()
API_KEY = os.getenv('API_KEY')


class MovieDataUpdater:
    def __init__(self):
        self.ps = PorterStemmer()
        self.cv = CountVectorizer(max_features=5000, stop_words='english')
        self.session = requests.Session()  # Reuse connections
        self.session.headers.update({'Connection': 'keep-alive'})

    def fetch_with_retry(self, url, max_retries=5):
        """Fetch URL with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 0.5  # Exponential backoff
                    print(
                        f"    Retry {attempt + 1}/{max_retries} after {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    return None
        return None

    def fetch_movies_from_tmdb(self, pages=100):
        """Fetch recent popular movies from TMDb"""
        movies_data = []

        print(f"Fetching {pages} pages of movies from TMDb...")
        print("(This may take 10-15 minutes with retry logic)")
        print()

        for page in range(1, pages + 1):
            url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page={page}'

            data = self.fetch_with_retry(url)

            if data and 'results' in data:
                results = data['results']

                for movie in results:
                    movie_id = movie['id']
                    details = self.fetch_movie_details(movie_id)
                    if details:
                        movies_data.append(details)

                # Progress indicator
                if page % 10 == 0:
                    print(
                        f"  ✓ Processed {page}/{pages} pages - {len(movies_data)} movies so far")
            else:
                print(f"  ⚠ Skipped page {page}")

            # Rate limiting - be nice to the API
            time.sleep(0.5)  # Increased from 0.25

        print()
        print(f"✓ Successfully fetched {len(movies_data)} movies!")
        return pd.DataFrame(movies_data)

    def fetch_movie_details(self, movie_id):
        """Fetch detailed movie information including credits"""
        details_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'

        # Fetch details
        details = self.fetch_with_retry(details_url)
        if not details:
            return None

        # Fetch credits
        credits = self.fetch_with_retry(credits_url)
        if not credits:
            return None

        # Get keywords
        keywords = self.fetch_keywords(movie_id)

        return {
            'movie_id': movie_id,
            'title': details.get('title', ''),
            'overview': details.get('overview', ''),
            'genres': [g['name'] for g in details.get('genres', [])],
            'keywords': keywords,
            'cast': [c['name'] for c in credits.get('cast', [])[:3]],
            'crew': [c['name'] for c in credits.get('crew', []) if c.get('job') == 'Director']
        }

    def fetch_keywords(self, movie_id):
        """Fetch movie keywords"""
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={API_KEY}'
        data = self.fetch_with_retry(url)

        if data and 'keywords' in data:
            return [k['name'] for k in data['keywords']]
        return []

    def preprocess_data(self, df):
        """Preprocess the movie data"""
        print("Preprocessing data...")

        # Remove movies with missing data
        initial_count = len(df)
        df = df.dropna()
        print(f"  Removed {initial_count - len(df)} movies with missing data")

        # Process overview
        df['overview'] = df['overview'].apply(
            lambda x: x.split() if isinstance(x, str) else [])

        # Remove spaces from names
        df['genres'] = df['genres'].apply(
            lambda x: [i.replace(" ", "") for i in x])
        df['keywords'] = df['keywords'].apply(
            lambda x: [i.replace(" ", "") for i in x])
        df['cast'] = df['cast'].apply(
            lambda x: [i.replace(" ", "") for i in x])
        df['crew'] = df['crew'].apply(
            lambda x: [i.replace(" ", "") for i in x])

        # Create tags
        df['tags'] = df['overview'] + df['genres'] + \
            df['keywords'] + df['cast'] + df['crew']
        df['tags'] = df['tags'].apply(lambda x: " ".join(x))
        df['tags'] = df['tags'].apply(lambda x: x.lower())

        # Stemming
        print("  Applying stemming...")
        df['tags'] = df['tags'].apply(self.stem)

        print("  Preprocessing complete!")
        return df[['movie_id', 'title', 'tags']]

    def stem(self, text):
        """Apply stemming to text"""
        y = []
        for i in text.split():
            y.append(self.ps.stem(i))
        return " ".join(y)

    def build_faiss_index(self, df):
        """Build FAISS index for efficient similarity search"""
        print("Building FAISS index...")

        # Vectorize
        vectors = self.cv.fit_transform(df['tags']).toarray().astype('float32')
        print(f"  Vector shape: {vectors.shape}")

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)

        # Create FAISS index
        dimension = vectors.shape[1]
        # Inner Product for cosine similarity
        index = faiss.IndexFlatIP(dimension)
        index.add(vectors)

        print(f"  FAISS index created with {index.ntotal} vectors")
        return index, vectors

    def save_data(self, df, index):
        """Save processed data and FAISS index"""
        print("Saving data...")

        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        # Save movie data
        pickle.dump(df.to_dict(), open('data/movies_dict.pkl', 'wb'))
        print("  ✓ Saved movies_dict.pkl")

        # Save FAISS index
        faiss.write_index(index, 'data/movies.index')
        print("  ✓ Saved movies.index")

        # Save vectorizer
        pickle.dump(self.cv, open('data/vectorizer.pkl', 'wb'))
        print("  ✓ Saved vectorizer.pkl")

        # Print file sizes
        print("\nFile sizes:")
        for filename in ['movies_dict.pkl', 'movies.index', 'vectorizer.pkl']:
            filepath = f'data/{filename}'
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  {filename}: {size_mb:.2f} MB")

        print(f"\n✅ Data saved successfully! Total movies: {len(df)}")


# Main execution
if __name__ == "__main__":
    print("="*60)
    print("MOVIE RECOMMENDER - DATA UPDATE SCRIPT")
    print("="*60)
    print()

    updater = MovieDataUpdater()

    # Fetch movies - reduced to 50 pages for better reliability
    movies_df = updater.fetch_movies_from_tmdb(pages=50)

    # Preprocess
    processed_df = updater.preprocess_data(movies_df)

    # Build FAISS index
    index, vectors = updater.build_faiss_index(processed_df)

    # Save
    updater.save_data(processed_df, index)

    print()
    print("="*60)
    print("UPDATE COMPLETE! 🎉")
    print("="*60)
