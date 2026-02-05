from flask import Flask, render_template, request, jsonify, send_from_directory
import numpy as np
from midiutil import MIDIFile
import os
import librosa

app = Flask(__name__)

# --- Raga Definitions ---
# Intervals from the base note (Sa)
RAGA_NOTES = {
    "yaman": [0, 2, 4, 6, 7, 9, 11],  # S, R, G, M(tivra), P, D, N
    "bhairav": [0, 1, 4, 5, 7, 8, 11], # S, r(komal), G, m, P, d(komal), N
    "bageshri": [0, 2, 3, 5, 9, 10],   # S, R, g(komal), m, D, n(komal)
}

def get_notes_from_scale(emotion, base_note):
    major_scale = [0, 2, 4, 5, 7, 9, 11]
    minor_scale = [0, 2, 3, 5, 7, 8, 10]
    scale = major_scale if emotion != 'sad' else minor_scale
    return [base_note + interval for interval in scale]

def get_raga_notes(raga, base_note):
    if raga in RAGA_NOTES:
        return [base_note + interval for interval in RAGA_NOTES[raga]]
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    emotion = request.args.get('emotion', 'happy')
    artist = request.args.get('artist', 'male')
    raga = request.args.get('raga', 'none')
    
    recorded_voice_path = os.path.join('static', 'recorded_voice.wav')
    has_recorded_voice = os.path.exists(recorded_voice_path)

    notes = []
    base_note = 60  # Default base note (C5) if no voice
    tempo = 120

    if has_recorded_voice:
        try:
            y, sr = librosa.load(recorded_voice_path)
            f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            avg_f0 = np.nanmean(f0)
            if avg_f0 > 0:
                base_note = int(round(librosa.hz_to_midi(avg_f0)))
        except Exception as e:
            print(f"Could not process audio: {e}")
            has_recorded_voice = False # To allow fallback

    # Raga has highest priority
    if raga != 'none':
        notes = get_raga_notes(raga, base_note)
        tempo = 90 # A moderate tempo for ragas
    
    # If no raga, use emotion
    if not notes:
        notes = get_notes_from_scale(emotion, base_note)
        tempo = 80 if emotion == 'sad' else 120
    
    melody = [int(note) for note in np.random.choice(notes, 30)]

    # Instrument selection
    if has_recorded_voice:
        program = 53  # Voice Oohs
    elif artist == 'female':
        program = 73 # Flute
    else: # Male
        program = 42 # Cello

    # Create MIDI
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "AI Generated Melody")
    midi.addTempo(track, time, tempo)
    midi.addProgramChange(track, 0, time, program)

    for i, pitch in enumerate(melody):
        midi.addNote(track, 0, pitch, time + i * 0.5, 0.5, 100)

    # Save and convert to WAV
    midi_path = os.path.join('static', 'generated.mid')
    wav_path = os.path.join('static', 'generated.wav')
    with open(midi_path, "wb") as output_file:
        midi.writeFile(output_file)
    os.system(f"fluidsynth -ni /usr/share/sounds/sf2/FluidR3_GM.sf2 {midi_path} -F {wav_path} -r 44100")

    return jsonify({'melody_path': '/static/generated.wav'})

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400
    file = request.files['audio_data']
    if file:
        if not os.path.exists('static'):
            os.makedirs('static')
        filepath = os.path.join('static', 'recorded_voice.wav')
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully'})
    return jsonify({'error': 'File upload failed'}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
