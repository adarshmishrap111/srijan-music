
import numpy as np
import librosa
from midiutil import MIDIFile
from gtts import gTTS

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
    'motivational': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'classical': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B'],
}

DRUM_MAP = {
    'kick': 36,
    'snare': 38,
    'hihat_closed': 42,
    'hihat_open': 46,
    'dhol_kick': 36,
    'dhol_snare': 40,
}

def get_base_note(artist):
    if artist == 'male':
        return 60
    elif artist == 'female':
        return 72
    elif artist == 'kid':
        return 76
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
    
    y, sr = librosa.load("static/lyrics.mp3")
    onset_env = librosa.onset.onset_detect(y=y, sr=sr)
    melody = []
    for i in range(len(onset_env) - 1):
        start_time = librosa.frames_to_time(onset_env[i], sr=sr)
        end_time = librosa.frames_to_time(onset_env[i+1], sr=sr)
        duration = end_time - start_time
        
        note_length = int(round(duration * (tempo / 60)))
        
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
    else:
        for i in range(length):
            if i % 4 == 0: drums[i].append(DRUM_MAP['kick'])
            if i % 8 == 4: drums[i].append(DRUM_MAP['snare'])
            if i % 2 == 0: drums[i].append(DRUM_MAP['hihat_closed'])
    return drums

def get_instrument_program(language, artist):
    if language == 'hindi':
        return 105
    if language == 'bhojpuri':
        return 73
    if language == 'punjabi':
        return 81
    
    if artist == 'female':
        return 53
    return 73
