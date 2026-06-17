```markdown
# ✨ WonderSkin — AI Skincare Intelligence

WonderSkin is an AI-powered skincare analysis platform built for Indian consumers. It analyzes products, compares them head-to-head, explains ingredients, builds personalized routines, and lets users browse top Indian skincare brands — all powered by Groq's LLM and vision models.

## Features

- **Product Analyzer** — Search any product by name or brand. If it's not in the database, AI researches it live and gives a full safety score, ingredient breakdown, and community review summary.
- **Image Label Scanner** — Upload a photo of any ingredient label and get an instant AI-read safety analysis.
- **Compare Products** — Pick two products (from the database or typed manually) and get a winner verdict tailored to your skin type.
- **Ingredient Explorer** — Look up any skincare ingredient and see what it does, who should avoid it, and the top 10 Indian products that contain it.
- **Brand Directory** — Browse the top 30 Indian skincare brands ranked by safety/trust score, with AI deep-dives on each.
- **Routine Builder** — Generate a personalized AM/PM routine that works around products you already own.
- **SkinFeed** — A community review feed where users can post, like, and delete reviews (persisted locally to a JSON file).

## Setup

### Prerequisites
- Python 3.9+
- A free [Groq API key](https://console.groq.com/keys)

### Installation

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

The app will open automatically at `http://localhost:8501`.

## Project Structure

```
WonderSkin/
├── app.py                  # Main Streamlit app
├── products_db.py          # Product database, ingredient analysis logic
├── skinfeed_posts.json     # Auto-created — stores community feed posts
├── .env                    # Your API key (not committed)
├── requirements.txt
└── README.md
```

## Tech Stack

- **Streamlit** — UI framework
- **Groq API** — `llama-3.3-70b-versatile` for text analysis, `llama-4-scout-17b-16e-instruct` for vision/label reading
- **Pillow** — image handling for label uploads
- **python-dotenv** — environment variable management

## Notes

- `GROQ_API_KEY` must be set in `.env`, or the app will show "AI unavailable" errors instead of analysis results.
- `skinfeed_posts.json` is created automatically on first run to persist community reviews between sessions. Delete it to reset the feed to defaults.
- Make sure `.env` and `venv/` are listed in `.gitignore` so secrets and the virtual environment are never committed.
- All safety scores and community ratings are AI-generated estimates for informational purposes only — not a substitute for professional dermatology advice.

## requirements.txt

```
streamlit
groq
python-dotenv
Pillow
```
```
