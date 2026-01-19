"""
Complete Update Pipeline
Fetches data, processes it, and uploads to GitHub releases
"""

from data_updater import MovieDataUpdater
from github_release_manager import GitHubReleaseManager
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    print("="*70)
    print(" "*15 + "MOVIE RECOMMENDER UPDATE PIPELINE")
    print("="*70)
    print()

    # Step 1: Update movie data
    print("STEP 1: Fetching and Processing Movie Data")
    print("-"*70)

    updater = MovieDataUpdater()
    movies_df = updater.fetch_movies_from_tmdb(pages=100)
    processed_df = updater.preprocess_data(movies_df)
    index, vectors = updater.build_faiss_index(processed_df)
    updater.save_data(processed_df, index)

    print()

    # Step 2: Upload to GitHub releases
    print("STEP 2: Uploading to GitHub Releases")
    print("-"*70)

    try:
        manager = GitHubReleaseManager()

        files_to_upload = [
            'data/movies_dict.pkl',
            'data/movies.index',
            'data/vectorizer.pkl'
        ]

        tag_name = os.getenv('GITHUB_RELEASE_TAG', 'v1.0.0')
        print(f"After tag in update and release")
        manager.upload_files(tag_name, files_to_upload)

        print()
        print("="*70)
        print(" "*20 + "✅ UPDATE COMPLETE!")
        print("="*70)
        print()
        print(f"Files uploaded to release: {tag_name}")
        print(f"Repository: {os.getenv('GITHUB_REPO')}")
        print()
        print("Your Streamlit app will now use the updated data!")

    except Exception as e:
        print(f"\n❌ Error uploading to GitHub: {e}")
        print("\nMake sure you have:")
        print("  1. Set GITHUB_TOKEN in .env")
        print("  2. Set GITHUB_REPO in .env (format: username/repo)")
        print("  3. GitHub token has 'repo' permissions")


if __name__ == "__main__":
    main()
