# Wildlife Lens — AI Wildlife Photo Analyzer
A clean, professional web app that analyzes wildlife photos and generates instant editing suggestions for **Lightroom** and **Snapseed**, powered by Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.10+-4E9E72?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-4E9E72?style=flat-square&logo=flask&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-4E9E72?style=flat-square&logo=google&logoColor=white)
![Live](https://img.shields.io/badge/Live-onrender.com-4E9E72?style=flat-square&logo=render&logoColor=white)

**🌿 Live Demo → [image-analyzer-1-8u5g.onrender.com](https://image-analyzer-2.onrender.com/)**

---

## Screenshots

![Home Page](images/home.png)
![Results Page](images/results.png)

---

## Features

- Upload any wildlife photo (JPG, PNG, WEBP — up to 16MB)
- AI-powered **brightness, sharpness, and contrast** analysis using OpenCV
- Raw metric scores displayed in UI (Brightness / Sharpness / Contrast values)
- Full Lightroom editing settings (Light, Color, Effects, Detail, Color Grading)
- Full Snapseed editing settings (Tune Image, Details, Curves, HDR, and more)
- 7 beginner tips tailored to the specific photo
- Intelligent prompt — Gemini gets condition-based instructions based on actual metric values
- Friendly error messages for API errors, rate limits, and timeouts
- Full activity logging to `app.log`
- Clean dark UI with professional typography

---

## Tech Stack

- **Backend** — Python, Flask, Gunicorn
- **AI** — Google Gemini 1.5 Flash (via `google-genai`)
- **Image Analysis** — OpenCV, NumPy
- **Frontend** — HTML, CSS, Vanilla JS
- **Fonts** — Playfair Display, DM Mono, Outfit
- **Deployed on** — Render

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/abhii-navv/Image-analyzer.git
cd Image-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get your API key from [Google AI Studio](https://aistudio.google.com).

### 5. Run the app
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`

---

## Project Structure

```
ai_wildlife_analyzer/
├── app.py                   # Flask app & routes
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment config
├── app.log                  # Activity logs (auto-created)
├── services/
│   ├── image_analysis.py    # OpenCV brightness, sharpness & contrast analysis
│   └── suggestion_engine.py # Gemini AI integration, prompt builder & parser
├── templates/
│   ├── index.html           # Upload page
│   ├── results.html         # Results page with metrics panel
│   ├── history.html         # History page
│   └── error.html           # Error page
├── static/
│   ├── css/style.css        # All styles
│   ├── js/script.js         # Drag & drop, form handling
│   └── uploads/             # Uploaded photos (auto-created, not tracked)
└── images/                  # App screenshots for README
```

---

## How Image Analysis Works

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # read image once

brightness = np.mean(gray)      # average pixel brightness
sharpness  = cv2.Laplacian(gray, cv2.CV_64F).var()  # blur detection
contrast   = gray.std()         # standard deviation = contrast
```

All three values are passed to Gemini so it generates smarter, condition-aware suggestions.

---
## Error Handling

| Error | Message Shown |
|-------|--------------|
| API key expired | Renew at aistudio.google.com |
| Rate limit hit | Wait 1-2 minutes |
| Bad image | Image may be corrupted |
| Timeout | Try again in a moment |

---

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |

> Never commit your `.env` file. It is listed in `.gitignore`.

---

© 2025 Abhi. All rights reserved.
