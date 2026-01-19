# 🎬 Movie Recommender System

A **content-based movie recommender system** that suggests similar movies based on your preferences. Built with **Streamlit**, powered by the **TMDb API**, and optimized using **FAISS** for fast similarity search.

---

## ✨ Features

- **5000+ Movies** – Continuously growing catalog fetched from TMDb
- **Fast Recommendations** – FAISS-based vector similarity search
- **Clean UI** – Simple and intuitive Streamlit interface
- **Auto-Updating Data** – Weekly refresh using GitHub Releases
- **Scalable Design** – Ready for production-style workflows

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/movie-recommender-system.git
cd movie-recommender-system
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Download NLTK Data

```bash
python scripts/setup_nltk.py
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file in the root directory:

```env
API_KEY=your_tmdb_api_key
GITHUB_TOKEN=your_github_token
GITHUB_REPO=yourusername/movie-recommender-system
GITHUB_RELEASE_TAG=v1.0.0
```

**TMDb API Key:** [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
**GitHub Token:** GitHub → Settings → Developer settings → Personal access tokens

> Required scope: `repo`

### 5️⃣ Run the App

```bash
streamlit run app.py
```

On first run, the app will automatically download model and data files from the GitHub Release.

---

## 🔄 Updating Movie Data

To fetch the latest movies and refresh recommendations:

```bash
python update_and_release.py
```

This pipeline will:

1. Fetch latest movies from TMDb
2. Process metadata & create embeddings
3. Build a FAISS similarity index
4. Upload artifacts to a GitHub Release
5. Make them available to the Streamlit app

---

## 📁 Project Structure

```
movie-recommender-system/
├── app.py                    # Main Streamlit app
├── data_updater.py           # TMDb data fetching & preprocessing
├── github_release_manager.py # GitHub Releases handler
├── update_and_release.py     # End-to-end update pipeline
├── requirements.txt          # Python dependencies
├── .env.example              # Sample environment variables
├── assets/                   # Images & icons
├── data/                     # Model files (downloaded at runtime)
└── scripts/                  # Utility scripts (NLTK setup, etc.)
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **ML / Similarity:** Scikit-learn, FAISS
- **NLP:** NLTK
- **API:** TMDb
- **Storage:** GitHub Releases
- **Language:** Python

---

## 📄 `.env.example`

```env
# TMDb API Key
# Get it from: https://www.themoviedb.org/settings/api
API_KEY=your_tmdb_api_key_here

# GitHub Configuration
# Generate token from: GitHub Settings → Developer settings → Personal access tokens
# Required scopes: repo
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=yourusername/movie-recommender-system
GITHUB_RELEASE_TAG=v1.0.0
```

---

## 🎯 Complete Migration Steps

### Phase 1: Setup (≈30 minutes)

1. **Backup current project**

   ```bash
   cp -r movie-recommender-system movie-recommender-backup
   ```

2. **Create new folder structure**

   ```bash
   mkdir -p data assets scripts
   mv movie.png assets/
   ```

3. **Create / update files**
   - `data_updater.py`
   - `github_release_manager.py`
   - `update_and_release.py`
   - `app.py`
   - `requirements.txt`
   - `.env`
   - `.gitignore`
   - `README.md`

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   python scripts/setup_nltk.py
   ```

---

### Phase 2: GitHub Setup (≈15 minutes)

1. Create a **GitHub Personal Access Token**
   - [https://github.com/settings/tokens](https://github.com/settings/tokens)
   - Generate new token (classic)
   - Select `repo` scope

2. Add credentials to `.env`

---

### Phase 3: First Data Update (≈10 minutes)

```bash
python update_and_release.py
```

This will:

- Fetch movies from TMDb
- Create FAISS index
- Upload artifacts to release `v1.0.0`

Verify under **GitHub → Releases**.

---

### Phase 4: Test the App (≈5 minutes)

```bash
streamlit run app.py
```

- First run downloads data automatically
- Select a movie → Click **Get Recommendations**

---

### Phase 5: Deploy to Streamlit Cloud (Optional)

1. Push to GitHub

   ```bash
   git add .
   git commit -m "Migrate to FAISS and GitHub releases"
   git push
   ```

2. Deploy via [https://streamlit.io/cloud](https://streamlit.io/cloud)

3. Add secrets in Streamlit Cloud dashboard:

```toml
API_KEY = "your_tmdb_api_key"
GITHUB_TOKEN = "your_github_token"
GITHUB_REPO = "yourusername/movie-recommender-system"
GITHUB_RELEASE_TAG = "v1.0.0"
```

---

## 🔄 Weekly Update Schedule

### Option 1: Manual (Recommended initially)

```bash
python update_and_release.py
```

### Option 2: GitHub Actions (Automated)

Create `.github/workflows/update-data.yml`:

```yaml
name: Update Movie Data

on:
  schedule:
    - cron: "0 2 * * 0" # Every Sunday 2 AM UTC
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python scripts/setup_nltk.py

      - name: Update movie data
        env:
          API_KEY: ${{ secrets.API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPO: ${{ secrets.GITHUB_REPO }}
          GITHUB_RELEASE_TAG: ${{ secrets.GITHUB_RELEASE_TAG }}
        run: python update_and_release.py
```

---

## 🐛 Troubleshooting

**Issue:** `No module named 'faiss'`
**Fix:**

```bash
pip install faiss-cpu
```

**Issue:** `GITHUB_TOKEN not found`
**Fix:** Verify `.env` variables

**Issue:** Files not downloading from GitHub
**Fix:**

- Ensure release exists
- Check `GITHUB_RELEASE_TAG`
- Confirm token has `repo` scope

**Issue:** TMDb rate limit exceeded
**Fix:** Reduce page count in updater

```python
movies_df = updater.fetch_movies_from_tmdb(pages=50)
```

---

## 📊 Old vs New Comparison

| Feature     | Old System       | New System              |
| ----------- | ---------------- | ----------------------- |
| Data Source | Static CSV       | Live TMDb API           |
| Updates     | Manual           | Weekly / Automated      |
| Storage     | Git LFS (~500MB) | GitHub Releases (~50MB) |
| Search      | Linear O(n)      | FAISS (log n)           |
| Movie Count | ~5,000           | 10,000+                 |
| Deployment  | Manual           | Automatic               |

---

## 🎓 Key Improvements

- ✅ Always up-to-date data
- ✅ 10–100× faster recommendations
- ✅ 10× smaller artifacts
- ✅ No Git LFS required
- ✅ Production-style architecture
- ✅ Free & scalable storage

---

## 🚀 Future Enhancements

- User ratings integration
- Movie trailers & posters
- Genre / year / rating filters
- Collaborative filtering
- Advanced search
- Detailed movie pages

---

## 📝 License

MIT License

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

🍿 **Happy movie watching!**
