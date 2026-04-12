
import random

def get_pop_suggestion(prompt):
    instruments = ["Synth Bass", "Drum Machine (808s)", "Clean Electric Guitar", "Piano", "String Pads"]
    styles = ["An upbeat, major-key chorus like Taylor Swift", "A retro 80s synth-pop vibe like The Weeknd", "A minimalist, emotional ballad with piano and vocals like Adele"]
    return f"""**Genre:** Pop\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** Strong, memorable melody, a clear verse-chorus structure, and polished production.\n**Style Idea:** {random.choice(styles)}\n**Prompt:** '{prompt}'"""

def get_rock_suggestion(prompt):
    instruments = ["Distorted Electric Guitar", "Acoustic Drum Kit", "Driving Bassline", "Power Chords", "Guitar Solo"]
    styles = ["A classic 70s rock anthem with a big guitar riff", "A 90s alternative grunge sound with quiet verses and loud choruses", "A modern indie rock feel with clean guitars and a steady beat"]
    return f"""**Genre:** Rock\n**Instrumentation:** {', '.join(random.sample(instruments, 4))}\n**Key Feature:** Centered around the electric guitar, often with a powerful and energetic feel.\n**Style Idea:** {random.choice(styles)}\n**Prompt:** '{prompt}'"""

def get_jazz_suggestion(prompt):
    instruments = ["Upright Bass", "Swing Drum Pattern", "Piano (with chords and improv)", "Saxophone", "Trumpet"]
    styles = ["A cool, relaxed bebop piece with improvisation", "A smooth, slow ballad for a smoky lounge", "A fast-paced swing track that makes you want to dance"]
    return f"""**Genre:** Jazz\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** Emphasis on improvisation, complex harmonies (chords), and syncopated rhythms (swing).\n**Style Idea:** {random.choice(styles)}\n**Prompt:** '{prompt}'"""

def get_hiphop_suggestion(prompt):
    instruments = ["TR-808 Drum Machine", "Deep Sub-Bass", "Sampled Melodies", "Synth Leads", "Record Scratches"]
    styles = ["An old-school 90s boom-bap beat with a sampled soul melody", "A modern trap beat with fast hi-hats and heavy 808s", "A lo-fi, chillhop track with a relaxed piano loop"]
    return f"""**Genre:** Hip-Hop\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** A strong, rhythmic beat is the foundation. The music is often loop-based or built around samples.\n**Style Idea:** {random.choice(styles)}\n**Prompt:** '{prompt}'"""
