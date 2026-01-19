"""
GitHub Release Manager - Manages model files in GitHub releases
Fixed for Windows compatibility
"""

from github import Github
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class GitHubReleaseManager:
    def __init__(self):
        token = os.getenv('GITHUB_TOKEN')
        repo_name = os.getenv('GITHUB_REPO')

        if not token or not repo_name:
            raise ValueError(
                "GITHUB_TOKEN and GITHUB_REPO must be set in .env file")

        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)

    def create_or_get_release(self, tag_name, release_name=None, description=None):
        """Create a new release or get existing one"""
        try:
            # Try to get existing release
            release = self.repo.get_release(tag_name)
            print(f"Found existing release: {tag_name}")
            return release
        except:
            # Create new release
            if release_name is None:
                release_name = f"Model Files {tag_name}"
            if description is None:
                # Fixed: Use datetime instead of os.popen for Windows
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                description = f"Movie recommender model files - Updated on {current_date}"

            print(f"Creating new release: {tag_name}")
            release = self.repo.create_git_release(
                tag=tag_name,
                name=release_name,
                message=description,
                draft=False,
                prerelease=False
            )
            print(f"✓ Release created: {tag_name}")
            return release

    def upload_files(self, tag_name, files_to_upload):
        """Upload files to a release"""
        release = self.create_or_get_release(tag_name)

        # Get existing assets
        existing_assets = {asset.name: asset for asset in release.get_assets()}

        for filepath in files_to_upload:
            filename = os.path.basename(filepath)

            if not os.path.exists(filepath):
                print(f"  ⚠️  File not found: {filepath}")
                continue

            # Delete existing asset if present
            if filename in existing_assets:
                print(f"  Deleting old {filename}...")
                existing_assets[filename].delete_asset()

            # Upload new asset
            print(f"  Uploading {filename}...")
            try:
                release.upload_asset(filepath, label=filename)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  ✓ Uploaded {filename} ({size_mb:.2f} MB)")
            except Exception as e:
                print(f"  ❌ Error uploading {filename}: {e}")

    def download_files(self, tag_name, destination_dir='data'):
        """Download files from a release"""
        os.makedirs(destination_dir, exist_ok=True)

        try:
            release = self.repo.get_release(tag_name)
            assets = list(release.get_assets())

            if not assets:
                print(f"No assets found in release {tag_name}")
                return False

            print(
                f"Downloading {len(assets)} files from release {tag_name}...")

            for asset in assets:
                filepath = os.path.join(destination_dir, asset.name)
                print(f"  Downloading {asset.name}...")

                # Download using asset browser_download_url
                import requests
                response = requests.get(asset.browser_download_url)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  ✓ Downloaded {asset.name} ({size_mb:.2f} MB)")

            return True

        except Exception as e:
            print(f"Error downloading files: {e}")
            return False

    def get_release_info(self, tag_name):
        """Get information about a release"""
        try:
            release = self.repo.get_release(tag_name)
            return {
                'tag': release.tag_name,
                'name': release.title,
                'created_at': release.created_at,
                'assets': [asset.name for asset in release.get_assets()]
            }
        except:
            return None


# Test the manager
if __name__ == "__main__":
    manager = GitHubReleaseManager()

    # Test: Get release info
    tag = os.getenv('GITHUB_RELEASE_TAG', 'v1.0.0')
    info = manager.get_release_info(tag)

    if info:
        print(f"Release: {info['tag']}")
        print(f"Created: {info['created_at']}")
        print(f"Assets: {info['assets']}")
    else:
        print(f"Release {tag} not found")
