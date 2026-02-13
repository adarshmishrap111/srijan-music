
import os
import logging
import re
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

# --- Helper Function for Parsing Lyrics ---
def parse_lyrics_for_dynamics(lyrics_with_tags: str):
    """
    Parses lyrics with emotion tags to create a dynamic prompt for the music AI
    and returns cleaned lyrics.
    """
    if not lyrics_with_tags or '[' not in lyrics_with_tags:
        return lyrics_with_tags, "The song has a consistent mood throughout."

    emotions = re.findall(r'\[([a-zA-Z]+)\]', lyrics_with_tags)
    cleaned_lyrics = re.sub(r'\[/?([a-zA-Z]+)\]', '', lyrics_with_tags).strip()

    if not emotions:
        return cleaned_lyrics, "The song has a consistent mood."

    if len(emotions) == 1:
        dynamic_description = f"The song should have a primarily {emotions[0]} feeling."
    else:
        progression = ", ".join(f"a {emotion} section" for emotion in emotions[:-1])
        if len(emotions) > 1:
            progression += f", and concludes with a {emotions[-1]} section"
        dynamic_description = f"The song's structure is dynamic: it includes {progression}."

    return cleaned_lyrics, dynamic_description

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suggest')
def suggest():
    if not REPLICATE_API_TOKEN:
        return jsonify({'error': 'Replicate API token is not configured.'}), 500

    inspiration = request.args.get('inspiration', '')
    if not inspiration:
        return jsonify({'error': 'Inspiration cannot be empty.'}), 400

    try:
        logging.info(f"Getting suggestions for: {inspiration}")
        model = client.models.get("meta/llama-2-70b-chat")
        version = model.versions.get("02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3")
        
        prompt = f'''You are a creative musical assistant. Based on the following user inspiration, generate 3 distinct and creative musical prompts. The user wants ideas for generating instrumental music. Present them as a simple list.

Inspiration: '{inspiration}'

1. 
2. 
3. '''
        
        output = version.predict(prompt=prompt, max_new_tokens=300)
        
        suggestions = [line.strip() for line in "".join(output).split('\n') if line.strip() and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.'))]
        suggestions = [s.split('.', 1)[1].strip() for s in suggestions]

        logging.info(f"Generated Suggestions: {suggestions}")
        return jsonify({'suggestions': suggestions})

    except Exception as e:
        logging.error(f"Error getting suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate')
def generate():
    if not REPLICATE_API_TOKEN:
        return jsonify({'error': 'Replicate API token is not configured.'}), 500

    try:
        base_prompt = request.args.get('prompt', '')
        lyrics_with_tags = request.args.get('lyrics', '')
        voice_sample_path = request.args.get('voice_sample_path', '')
        duration = int(request.args.get('duration', 15))

        if not base_prompt:
            return jsonify({'error': 'Music generation prompt cannot be empty.'}), 400

        cleaned_lyrics, dynamic_description = parse_lyrics_for_dynamics(lyrics_with_tags)
        final_prompt = f"{base_prompt}. {dynamic_description}"
        
        logging.info(f"Final Dynamic Prompt: {final_prompt}, Duration: {duration}")
        logging.info(f"Cleaned Lyrics: {cleaned_lyrics}, Voice Sample: {voice_sample_path}")

        logging.info("Generating instrumental music with dynamic prompt...")
        music_model = client.models.get("facebook/musicgen-stereo")
        music_version = music_model.versions.get("dee88d05de5f873007c089450c237e8e4a77320473a21532f70337cf4614c24a")
        music_output = music_version.predict(
            prompt=final_prompt,
            duration=duration
        )
        logging.info(f"Generated music URL: {music_output}")

        singing_output = None
        if cleaned_lyrics:
            logging.info("Lyrics provided. Engaging text-to-singing model...")
            singing_model = client.models.get("riffusion/riffusion")
            singing_version = singing_model.versions.get("8cf61ea6c56afd61d8f5b9ffd14d7c216c0a93844ce2d82ac1c9ecc9c7f24e05")
            singing_prompt = f"{final_prompt} | Vocals: {cleaned_lyrics}"
            singing_output_obj = singing_version.predict(prompt_a=singing_prompt)
            singing_output = singing_output_obj.get('audio')
            logging.info(f"Generated singing URL: {singing_output}")

        return jsonify({
            'music_path': music_output,
            'speech_path': singing_output
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
        filename = secure_filename("user_voice_sample.wav")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f'Voice sample saved to {filepath}')
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
