
import os
import logging
import re
import replicate
import requests
import io
import urllib.request
from flask import Flask, request, jsonify, render_template, send_from_directory, Response, send_file
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from pydub.utils import ratio_to_db
from indian_music_model import *
from western_music_model import *

app = Flask(__name__)

# --- Configurations and Setup ---
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
if not REPLICATE_API_TOKEN: logging.warning("REPLICATE_API_TOKEN not found.")
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# --- Helper Functions and Other Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# (proxy, parse_lyrics, suggest, suggest_genre, upload_voice routes would be here)

@app.route('/generate')
def generate():
    # This function remains as it was, generating stems, art, and signature
    # ... (Full generate logic as implemented previously)
    pass # Placeholder for brevity

# --- FINAL MASTERING ENDPOINT ---
@app.route('/master', methods=['POST'])
def master():
    try:
        data = request.get_json()
        stems_data = data.get('stems', {})
        signature_data = data.get('signature')

        logging.info(f"Starting mastering process with data: {data}")
        
        processed_stems = []
        max_duration = 0

        stem_keys = ['vocals', 'drums', 'bass', 'other', 'instrumental']

        for stem_name in stem_keys:
            stem_info = stems_data.get(stem_name)
            if not stem_info or not stem_info.get('url'):
                continue
            
            url = stem_info.get('url')
            volume_percent = int(stem_info.get('volume', 100))

            logging.info(f"Processing stem: {stem_name} from {url} at {volume_percent}% volume")
            
            with urllib.request.urlopen(url) as response:
                audio_data = io.BytesIO(response.read())
                stem_audio = AudioSegment.from_file(audio_data)

                if volume_percent == 0:
                    continue
                
                db_change = ratio_to_db(volume_percent / 100)
                adjusted_stem = stem_audio + db_change
                
                processed_stems.append(adjusted_stem)
                if len(adjusted_stem) > max_duration:
                    max_duration = len(adjusted_stem)

        if max_duration == 0:
            return jsonify({'error': 'No audio stems with duration found to master.'}), 400

        final_mix = AudioSegment.silent(duration=max_duration)

        for stem in processed_stems:
            final_mix = final_mix.overlay(stem)

        if signature_data and signature_data.get('url'):
            logging.info(f"Adding signature from {signature_data.get('url')}")
            with urllib.request.urlopen(signature_data['url']) as response:
                signature_audio_data = io.BytesIO(response.read())
                signature_audio = AudioSegment.from_file(signature_audio_data)
                final_mix = signature_audio + final_mix

        output_buffer = io.BytesIO()
        final_mix.export(output_buffer, format="mp3", bitrate="192k")
        output_buffer.seek(0)

        logging.info("Mastering complete. Sending file.")
        return send_file(
            output_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='Dhvani_AI_Masterpiece.mp3'
        )

    except Exception as e:
        logging.error(f"Error during mastering: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
