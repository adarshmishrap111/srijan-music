
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
        # --- Get Parameters from the new advanced UI --- #
        prompt = request.args.get('prompt', '')
        duration = int(request.args.get('duration', 8))

        if not prompt:
            return jsonify({'error': 'Prompt cannot be empty.'}), 400

        logging.info(f"Received Advanced Prompt: {prompt}")
        logging.info(f"Duration: {duration} seconds")

        # --- Call Replicate API with the consolidated prompt --- #
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

# --- Static File Serving --- #
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
