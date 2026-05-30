from flask import Flask, render_template, request, jsonify
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from services.image_analysis import analyze_image
from services.suggestion_engine import get_suggestions

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
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    analysis = analyze_image(filepath)
    suggestions = get_suggestions(
        analysis['lighting'],
        analysis['focus'],
        analysis['brightness_value'],
        analysis['blur_value'],
        filepath
    )

    entry = {
        'id': str(uuid.uuid4()),
        'filename': filename,
        'original_name': file.filename,
        'date': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        'lighting': analysis['lighting'],
        'focus': analysis['focus'],
        'brightness_value': analysis['brightness_value'],
        'blur_value': analysis['blur_value'],
        'lightroom': suggestions['lightroom'],
        'snapseed': suggestions['snapseed'],
        'tips': suggestions['beginner_tips']
    }
    save_history(entry)

    return render_template('results.html',
        image_url='/' + filepath.replace('\\', '/'),
        lighting=analysis['lighting'],
        focus=analysis['focus'],
        brightness_value=analysis['brightness_value'],
        blur_value=analysis['blur_value'],
        lightroom=suggestions['lightroom'],
        snapseed=suggestions['snapseed'],
        tips=suggestions['beginner_tips']
    )

@app.route('/history')
def history():
    entries = load_history()
    return render_template('history.html', entries=entries)

@app.route('/history/<entry_id>')
def history_detail(entry_id):
    entries = load_history()
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if not entry:
        return "Not found", 404
    return render_template('results.html',
        image_url='/static/uploads/' + entry['filename'],
        lighting=entry['lighting'],
        focus=entry['focus'],
        brightness_value=entry['brightness_value'],
        blur_value=entry['blur_value'],
        lightroom=entry['lightroom'],
        snapseed=entry['snapseed'],
        tips=entry['tips']
    )
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="Page not found."), 404

@app.errorhandler(413)
def file_too_large(e):
    return render_template('error.html', code=413, message="File too large. Maximum size is 16MB."), 413

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message="Something went wrong. Please try again."), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=False)