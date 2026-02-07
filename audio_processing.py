
from pydub import AudioSegment

def merge_audio(file1, file2, output_file):
    sound1 = AudioSegment.from_mp3(file1)
    sound2 = AudioSegment.from_mp3(file2)
    
    combined = sound1.overlay(sound2)
    
    combined.export(output_file, format='mp3')
