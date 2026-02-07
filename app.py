
import os
import logging
import replicate
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# --- Environment Variables --- #
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
if not REPLICATE_API_TOKEN:
    logging.warning("REPLICATE_API_TOKEN not found. Please set it in your environment variables.")

# --- Replicate Client --- #
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    if not REPLICATE_API_TOKEN:
        return jsonify({'error': 'Replicate API token is not configured. Please contact the administrator.'}), 500
    
    try:
        # --- Get Parameters --- #
        emotion = request.args.get('emotion', 'happy')
        language = request.args.get('language', 'hindi')
        lyrics = request.args.get('lyrics', '')
        instrument = request.args.get('instrument', 'auto')
        duration = int(request.args.get('duration', 8)) # Default 8 seconds

        logging.info(f"Request: emotion={emotion}, language={language}, lyrics={lyrics}, instrument={instrument}, duration={duration}")

        # --- Construct Prompt --- #
        prompt = f"{emotion} {language} song"
        if lyrics:
            prompt = f"{lyrics}, a {emotion} {language} song"
        if instrument != 'auto':
            prompt += f" with {instrument}"

        logging.info(f"Generated Prompt: {prompt}")

        # --- Call Replicate API --- #
        model = client.models.get("meta/musicgen")
        version = model.versions.get("7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906")
        output = version.predict(
            prompt=prompt,
            duration=duration
        )

        logging.info(f"Generated music URL: {output}")
        return jsonify({'melody_path': output})

    except Exception as e:
        logging.error(f"Error in /generate: {e}")
        return jsonify({'error': str(e)}), 500

# --- Static File Serving (for existing HTML/JS) --- #
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
