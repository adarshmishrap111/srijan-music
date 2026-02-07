
import os
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from midiutil import MIDIFile
import librosa
import soundfile as sf
import logging
from gtts import gTTS
from pydub import AudioSegment

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# --- Raga, Scale, and Drum Definitions ---
RAGA_NOTES = {
    'yaman': ['C', 'D', 'E', 'F#', 'G', 'A', 'B'],
    'bhairav': ['C', 'Db', 'E', 'F', 'G', 'Ab', 'B'],
    'bageshri': ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb'],
    'kafi': ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb'],
}

SCALE_NOTES = {
    'happy': ['C', 'D', 'E', 'G', 'A'],
    'sad': ['C', 'Eb', 'F', 'G', 'Bb'],
    'calm': ['C', 'D', 'F', 'G', 'A'],
    'motivational': ['C', 'D', 'E', 'F', 'G', 'A', 'B'], # Major scale
    'classical': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B'], # Harmonic Minor
}

DRUM_MAP = {
    'kick': 36,
    'snare': 38,
    'hihat_closed': 42,
    'hihat_open': 46,
    'dhol_kick': 36, # Using kick for dhol sound
    'dhol_snare': 40, # Using a different snare for dhol
}

# --- Music Generation Logic ---

def get_base_note(artist):
    if artist == 'male':
        return 60  # C4
    elif artist == 'female':
        return 72  # C5
    elif artist == 'kid':
        return 76  # E5
    return 60

def get_scale_notes(scale_name, base_note):
    notes_in_scale = SCALE_NOTES.get(scale_name, SCALE_NOTES['happy'])
    return [base_note + librosa.note_to_midi(n) - librosa.note_to_midi('C4') for n in notes_in_scale]

def get_raga_notes(raga_name, base_note):
    notes_in_raga = RAGA_NOTES.get(raga_name)
    if not notes_in_raga:
        return []
    return [base_note + librosa.note_to_midi(n) - librosa.note_to_midi('C4') for n in notes_in_raga]

def generate_melody_from_lyrics(lyrics, notes, tempo):
    tts = gTTS(text=lyrics, lang='hi')
    tts.save("static/lyrics.mp3")
    
    # Analyze the rhythm of the speech
    y, sr = librosa.load("static/lyrics.mp3")
    onset_env = librosa.onset.onset_detect(y=y, sr=sr)
    melody = []
    for i in range(len(onset_env) - 1):
        start_time = librosa.frames_to_time(onset_env[i], sr=sr)
        end_time = librosa.frames_to_time(onset_env[i+1], sr=sr)
        duration = end_time - start_time
        
        # Map the duration to a note length
        note_length = int(round(duration * (tempo / 60)))
        
        # Choose a note from the scale
        melody.extend([int(np.random.choice(notes))] * note_length)
        
    return melody

def generate_melody(notes, length=32):
    return [int(note) for note in np.random.choice(notes, length)]

def generate_harmony(melody, notes):
    harmony = []
    for note in melody:
        interval = np.random.choice([3, 4, 7])
        harmony_note = note + interval
        if harmony_note not in notes:
            harmony_note = notes[np.argmin(np.abs(np.array(notes) - harmony_note))]
        harmony.append(harmony_note)
    return harmony

def generate_bassline(melody, notes):
    bassline = []
    for i in range(len(melody)):
        if i % 4 == 0:
            bass_note = notes[0] - 12 if notes else 48
            bassline.extend([bass_note] * 4)
    return bassline[:len(melody)]

def generate_drums(language, length=32):
    drums = [[] for _ in range(length)]
    if language == 'punjabi':
        for i in range(length):
            if i % 4 == 0: drums[i].append(DRUM_MAP['dhol_kick'])
            if i % 8 == 2: drums[i].append(DRUM_MAP['hihat_closed'])
            if i % 4 == 2: drums[i].append(DRUM_MAP['dhol_snare'])
            if i % 8 == 6: drums[i].append(DRUM_MAP['hihat_open'])
    elif language == 'bhojpuri':
        for i in range(length):
            if i % 4 == 0: drums[i].append(DRUM_MAP['kick'])
            if i % 8 == 4: drums[i].append(DRUM_MAP['snare'])
            if i % 2 == 1: drums[i].append(DRUM_MAP['hihat_closed'])
    else: # Default for Hindi and others
        for i in range(length):
            if i % 4 == 0: drums[i].append(DRUM_MAP['kick'])
            if i % 8 == 4: drums[i].append(DRUM_MAP['snare'])
            if i % 2 == 0: drums[i].append(DRUM_MAP['hihat_closed'])
    return drums

def get_instrument_program(language, artist):
    if language == 'hindi':
        return 105 # Sitar
    if language == 'bhojpuri':
        return 73 # Flute
    if language == 'punjabi':
        return 81 # Synth Lead
    
    # Fallback based on artist if language is not specific
    if artist == 'female':
        return 53 # Voice Oohs
    return 73 # Flute for male/kid as a default

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    try:
        emotion = request.args.get('emotion', 'happy')
        artist = request.args.get('artist', 'male')
        raga = request.args.get('raga', 'none')
        language = request.args.get('language', 'hindi')
        lyrics = request.args.get('lyrics', '')
        logging.info(f"Request: emotion={emotion}, artist={artist}, raga={raga}, language={language}, lyrics={lyrics}")

        base_note = get_base_note(artist)
        notes = []
        tempo = 120

        if raga != 'none':
            notes = get_raga_notes(raga, base_note)
            tempo = 90
        
        if not notes:
            notes = get_scale_notes(emotion, base_note)
            if emotion == 'sad': tempo = 80
            elif emotion == 'calm': tempo = 70

        if not notes:
             return jsonify({'error': 'Could not determine musical scale.'}), 500

        if lyrics:
            melody = generate_melody_from_lyrics(lyrics, notes, tempo)
        else:
            melody = generate_melody(notes)

        harmony = generate_harmony(melody, notes)
        bassline = generate_bassline(melody, notes)
        drums = generate_drums(language, len(melody))

        melody_program = get_instrument_program(language, artist)
        harmony_program = 1   # Piano
        bass_program = 33     # Electric Bass

        midi = MIDIFile(4)
        tracks = [(0, "Melody", melody, melody_program), 
                  (1, "Harmony", harmony, harmony_program),
                  (2, "Bassline", bassline, bass_program)]

        for track_num, name, pattern, program in tracks:
            midi.addTrackName(track_num, 0, name)
            midi.addTempo(track_num, 0, tempo)
            midi.addProgramChange(track_num, track_num, 0, program)
            for i, pitch in enumerate(pattern):
                midi.addNote(track_num, track_num, pitch, i * 0.5, 0.5, 100 if track_num == 0 else 70)
        
        # Drums track
        midi.addTrackName(3, 0, "Drums")
        midi.addTempo(3, 0, tempo)
        for i, beat in enumerate(drums):
            for note in beat:
                midi.addNote(3, 9, note, i * 0.5, 0.5, 100)

        if not os.path.exists('static'):
            os.makedirs('static')
        midi_path = "static/output.mid"
        with open(midi_path, "wb") as f:
            midi.writeFile(f)

        wav_path = "static/output.wav"
        os.system(f"fluidsynth -ni /usr/share/sounds/sf2/FluidR3_GM.sf2 {midi_path} -F {wav_path} -r 44100")
        
        mp3_path = "static/output.mp3"
        os.system(f"ffmpeg -i {wav_path} -y {mp3_path}")
        
        logging.info(f"Generated music: {mp3_path}")
        return jsonify({'melody_path': mp3_path})

    except Exception as e:
        logging.error(f"Error in /generate: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400
    
    file = request.files['audio_data']
    if not os.path.exists('static'):
        os.makedirs('static')

    filepath = os.path.join('static', 'recorded_voice.wav')
    file.save(filepath)
    
    # --- Placeholder for future voice integration ---
    # Here you would add code to process the recorded voice.
    # For example, using a library like librosa to analyze pitch
    # and then use that to influence the generated melody.
    logging.info(f"User voice saved to {filepath}. Processing not yet implemented.")
    # --- End Placeholder ---

    return jsonify({'success': True, 'path': filepath})


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
