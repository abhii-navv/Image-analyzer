from flask import Flask, render_template, request, jsonify
import os
import json
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from services.image_analysis import analyze_image
from services.suggestion_engine import get_suggestions, GeminiError

# ─── LOGGING SETUP ────────────────────────────────
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
HISTORY_FILE = 'history.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(entry):
    history = load_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.route('/')
def index():
    logger.info("Home page visited")
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        logger.warning("No file in request")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']

    if file.filename == '':
        logger.warning("Empty filename submitted")
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Invalid file type"}), 400

    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    logger.info(f"Image uploaded: {file.filename} → saved as {filename}")

    analysis = analyze_image(filepath)
    logger.info(f"Image analyzed — Brightness: {analysis['brightness_value']}, Sharpness: {analysis['blur_value']}, Contrast: {analysis['contrast_value']}")
    logger.info(f"Labels — Lighting: {analysis['lighting']}, Focus: {analysis['focus']}, Contrast: {analysis['contrast']}")

    try:
        suggestions = get_suggestions(
            analysis['lighting'],
            analysis['focus'],
            analysis['contrast'],
            analysis['brightness_value'],
            analysis['blur_value'],
            analysis['contrast_value'],
            filepath
        )
        logger.info("Gemini responded successfully")

    except GeminiError as e:
        logger.error(f"Gemini error: {str(e)}")
        return render_template('error.html', code="AI Error", message=str(e)), 503

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return render_template('error.html', code=500, message="Something went wrong. Please try again."), 500

    entry = {
        'id': str(uuid.uuid4()),
        'filename': filename,
        'original_name': file.filename,
        'date': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        'lighting': analysis['lighting'],
        'focus': analysis['focus'],
        'contrast': analysis['contrast'],
        'brightness_value': analysis['brightness_value'],
        'blur_value': analysis['blur_value'],
        'contrast_value': analysis['contrast_value'],
        'lightroom': suggestions['lightroom'],
        'snapseed': suggestions['snapseed'],
        'tips': suggestions['beginner_tips']
    }
    save_history(entry)
    logger.info(f"History saved for: {file.filename}")

    return render_template('results.html',
        image_url='/' + filepath.replace('\\', '/'),
        lighting=analysis['lighting'],
        focus=analysis['focus'],
        contrast=analysis['contrast'],
        brightness_value=analysis['brightness_value'],
        blur_value=analysis['blur_value'],
        contrast_value=analysis['contrast_value'],
        lightroom=suggestions['lightroom'],
        snapseed=suggestions['snapseed'],
        tips=suggestions['beginner_tips']
    )

@app.route('/history')
def history():
    logger.info("History page visited")
    entries = load_history()
    return render_template('history.html', entries=entries)

@app.route('/history/<entry_id>')
def history_detail(entry_id):
    logger.info(f"History detail viewed: {entry_id}")
    entries = load_history()
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if not entry:
        logger.warning(f"History entry not found: {entry_id}")
        return "Not found", 404
    return render_template('results.html',
        image_url='/static/uploads/' + entry['filename'],
        lighting=entry['lighting'],
        focus=entry['focus'],
        contrast=entry.get('contrast', 'N/A'),
        brightness_value=entry['brightness_value'],
        blur_value=entry['blur_value'],
        contrast_value=entry.get('contrast_value', 'N/A'),
        lightroom=entry['lightroom'],
        snapseed=entry['snapseed'],
        tips=entry['tips']
    )

@app.errorhandler(404)
def not_found(e):
    logger.warning("404 - Page not found")
    return render_template('error.html', code=404, message="Page not found."), 404

@app.errorhandler(413)
def file_too_large(e):
    logger.warning("413 - File too large")
    return render_template('error.html', code=413, message="File too large. Maximum size is 16MB."), 413

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 - Server error: {str(e)}")
    return render_template('error.html', code=500, message="Something went wrong. Please try again."), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    logger.info("Wildlife Lens app started")
    app.run(debug=False)
