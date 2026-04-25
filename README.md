# 🪐 Jyotish Guru v3 — by Deoxys

Vedic Astrology AI with **astronomically accurate** planetary positions.

**What's new in v3:**
- 🔭 **Swiss Ephemeris** — real planetary positions via `pyswisseph` (Lahiri ayanamsa)
- 🤖 **Gemini AI** — significantly more accurate, nuanced, and context-aware than Gemini
- 📐 **True Lagna calculation** — using birth coordinates (lat/lon)
- ⏳ **Precise Dasha engine** — Vimshottari dasha from exact Moon nakshatra position
- 🔴 **Atmakaraka detection** — planet with highest degree across all positions
- 🧲 **Coordinate autofill** — built-in city coordinates for 30+ major cities
- 📍 **"Use My Location"** — browser geolocation for maximum accuracy
- 📊 **Visual chart display** — planetary table + dasha progress bar before AI analysis
- 🚀 **Railway-optimized** — `railway.json`, `Procfile`, `nixpacks.toml` included

---

## 🔑 Get Your API Key

1. Go to → https://aistudio.google.com/app/apikey
2. Sign in → API Keys → Create Key
3. Copy it — looks like `AIzaSy...`

---

## 🚀 Deploy to Railway (Recommended — always online)

1. Push this folder to a **new GitHub repo**
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your repo
4. Go to **Variables** tab → Add:
   - `GEMINI_API_KEY` = your key from aistudio.google.com/app/apikey
5. Railway auto-deploys in ~90 seconds. Your site stays **always online**.

**No credit card needed on Railway's free tier (500 hours/month).**

---

## 🚀 Deploy to Render

1. [render.com](https://render.com) → New → Web Service → Connect GitHub repo
2. **Runtime:** Python 3
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Add Environment Variable: `GEMINI_API_KEY`

---

## 💻 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=AIzaSy..." > .env

# Run
python server.py
# → Open http://localhost:3000
```

Or with gunicorn:
```bash
GEMINI_API_KEY=AIzaSy... gunicorn server:app --bind 0.0.0.0:3000 --workers 2
```

---

## 🔭 Accuracy Notes

| Feature | v2 (Gemini) | v3 (Swiss Ephemeris + Claude) |
|---|---|---|
| Planetary positions | AI-estimated | Swiss Ephemeris (JPL-precision) |
| Ayanamsa | None (AI guesses) | Lahiri (standard Indian) |
| Lagna calculation | AI-estimated | True geometric calculation |
| Dasha calculation | AI-estimated | Computed from exact Moon longitude |
| AI model | Gemini 1.5 Flash | Gemini 2.0 Flash (superior reasoning) |
| Koota matching | AI + lookup | Ephemeris data + lookup tables |
| Atmakaraka | None | Detected from exact degrees |

---

## API Endpoints

- `GET  /health` — Status check
- `POST /api/chart` — Raw chart data (JSON)
- `POST /api/kundali` — Full kundali report with AI analysis
- `POST /api/match` — Kundali matching with koota scores + AI narrative

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Your Anthropic API key |
| `PORT` | No | Port to run on (default: 3000) |
| `FLASK_ENV` | No | Set to `development` for debug mode |
