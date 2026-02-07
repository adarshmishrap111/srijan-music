
import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from midiutil import MIDIFile

from music_generation import (
    get_base_note,
    get_raga_notes,
    get_scale_notes,
    generate_melody_from_lyrics,
    generate_melody,
    generate_harmony,
    generate_bassline,
    generate_drums,
    get_instrument_program,
)
from audio_processing import merge_audio

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

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
        instrument = request.args.get('instrument', 'auto')
        logging.info(f"Request: emotion={emotion}, artist={artist}, raga={raga}, language={language}, lyrics={lyrics}, instrument={instrument}")

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

        melody_program = get_instrument_program(instrument, language, artist)
        harmony_program = 1 # Piano
        bass_program = 33 # Electric Bass

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
    
    logging.info(f"User voice saved to {filepath}. Processing not yet implemented.")

    return jsonify({'success': True, 'path': filepath})

@app.route('/merge_audio', methods=['POST'])
def merge_audio_route():
    try:
        file1 = request.form['file1']
        file2 = request.form['file2']
        output_file = request.form['output_file']

        merge_audio(file1, file2, output_file)

        return jsonify({'success': True, 'output_path': output_file})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
