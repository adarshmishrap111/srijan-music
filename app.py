
import os
import logging
import replicate
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Configurations ---
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# --- Environment & API Setup ---
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
if not REPLICATE_API_TOKEN:
    logging.warning("REPLICATE_API_TOKEN not found. This is required for AI generation.")

client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    if not REPLICATE_API_TOKEN:
        return jsonify({'error': 'Replicate API token is not configured.'}), 500

    try:
        # --- Get Shared Parameters ---
        prompt = request.args.get('prompt', '')
        lyrics = request.args.get('lyrics', '')
        voice_sample_path = request.args.get('voice_sample_path', '')
        duration = int(request.args.get('duration', 8))

        if not prompt:
            return jsonify({'error': 'Music generation prompt cannot be empty.'}), 400

        logging.info(f"Music Prompt: {prompt}, Duration: {duration}")
        logging.info(f"Speech Lyrics: {lyrics}, Voice Sample: {voice_sample_path}")

        # --- 1. Generate Instrumental Music --- #
        music_model = client.models.get("facebook/musicgen-stereo")
        music_version = music_model.versions.get("dee88d05de5f873007c089450c237e8e4a77320473a21532f70337cf4614c24a")
        music_output = music_version.predict(
            prompt=prompt,
            duration=duration
        )
        logging.info(f"Generated music URL: {music_output}")

        speech_output = None
        # --- 2. Generate Cloned Voice (if applicable) --- #
        if lyrics and voice_sample_path:
            full_voice_path = voice_sample_path.lstrip('/') # Remove leading '/' to get relative path
            if os.path.exists(full_voice_path):
                logging.info(f"Found voice sample at {full_voice_path}. Cloning voice...")
                speech_model = client.models.get("replicate/xtts-v2")
                speech_version = speech_model.versions.get("5c9e6d9f3c1097858d40763529341499557b7264859530b1446a895c3b999815")
                
                with open(full_voice_path, "rb") as audio_file:
                    speech_output = speech_version.predict(
                        text=lyrics,
                        audio_file=audio_file
                    )
                logging.info(f"Generated speech URL: {speech_output}")
            else:
                logging.warning(f"Voice sample path provided, but not found at {full_voice_path}")

        # --- 3. Return both URLs --- #
        return jsonify({
            'music_path': music_output,
            'speech_path': speech_output
        })

    except Exception as e:
        logging.error(f"Error during generation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    file = request.files['audio_data']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename("user_voice_sample.wav") # Use a consistent filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f'Voice sample saved to {filepath}')
        # Return a URL-friendly path for the client
        return jsonify({'path': f'/{filepath}'})

# --- File Serving ---
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
