
import random

def get_indian_classical_suggestion(prompt):
    instruments = ["Sitar", "Tabla", "Sarod", "Bansuri (flute)", "Tanpura"]
    ragas = ["Yaman (calm, evening)", "Bhairav (devotional, morning)", "Malkauns (contemplative, night)", "Megh Malhar (associated with rain)"]
    return f"""**Genre:** Indian Classical (Hindustani)\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** Based on a specific Raga ({random.choice(ragas)}) with a slow alap (introduction) followed by a gat (composition).\n**Prompt:** '{prompt}'"""

def get_punjabi_suggestion(prompt):
    instruments = ["Dhol", "Tumbi", "Algoza", "Chimta", "Modern Synths"]
    themes = ["High-energy bhangra for celebration", "A romantic ballad with folk influence", "A powerful track about pride and heritage"]
    return f"""**Genre:** Punjabi\n**Instrumentation:** {', '.join(random.sample(instruments, 4))}\n**Key Feature:** A powerful, catchy beat driven by the Dhol. Modern Punjabi music often fuses folk instruments with hip-hop or pop production.\n**Theme:** {random.choice(themes)}\n**Prompt:** '{prompt}'"""

def get_bhojpuri_suggestion(prompt):
    instruments = ["Dholak", "Harmonium", "Jhal", "Accordion", "Shehnai"]
    themes = ["A playful song for a wedding or festival", "A devotional song (bhajan)", "A story about village life"]
    return f"""**Genre:** Bhojpuri\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** Raw, earthy vocals with a focus on rhythmic patterns. Often tells a story.\n**Theme:** {random.choice(themes)}\n**Prompt:** '{prompt}'"""


def get_hindi_suggestion(prompt):
    styles = ["A modern Arijit Singh-style romantic ballad with piano and strings", "A 90s-style Kumar Sanu melody with classic drum machines", "A vibrant party number with synths and a strong bassline like Badshah"]
    return f"""**Genre:** Hindi (Bollywood)\n**Key Feature:** Highly melodic and follows a structured verse-chorus pattern. The style can vary greatly.\n**Style Idea:** {random.choice(styles)}\n**Prompt:** '{prompt}'"""

def get_ghazal_suggestion(prompt):
    instruments = ["Harmonium", "Tabla", "Santoor", "Acoustic Guitar", "Sarangi"]
    moods = ["Melancholy and longing (judai)", "The beauty of the beloved", "Philosophical reflections on life and love"]
    return f"""**Genre:** Ghazal\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** Poetic, lyrical vocals with a gentle and sophisticated musical arrangement.\n**Mood:** {random.choice(moods)}\n**Prompt:** '{prompt}'"""

def get_carnatic_suggestion(prompt):
    instruments = ["Violin", "Mridangam", "Ghatam", "Veena", "Flute"]
    kritis = ["Vatapi Ganapatim Bhajeham", "Endaro Mahanubhavulu", "Jagadodharana"]
    return f"""**Genre:** Carnatic Classical\n**Instrumentation:** {', '.join(random.sample(instruments, 3))}\n**Key Feature:** Focus on vocal performance, intricate rhythmic patterns (tala) and melodic structures (raga). Often a composition (kriti) like '{random.choice(kritis)}'.\n**Prompt:** '{prompt}'"""

def get_sufi_suggestion(prompt):
    instruments = ["Harmonium", "Tabla", Dholak", "Bulbul Tarang", "Sarangi", "Acoustic Guitar"]
    moods = ["Spiritual and devotional", "Mystical and hypnotic", "Emotional and longing (ishq)", "Celebratory and ecstatic (qawwali)"]
    return f"""**Genre:** Sufi Music (Qawwali/Kalam)\n**Instrumentation:** {', '.join(random.sample(instruments, random.randint(3, 5)))}\n**Key Feature:** Repetitive melodic cycles to create a trance-like state. Often builds in intensity.\n**Mood:** {random.choice(moods)}\n**Prompt:** '{prompt}'"""

def get_rajasthani_folk_suggestion(prompt):
    instruments = ["Ravanahatha", "Kamaicha", "Morchang", "Dholak", "Khartal", "Algoza"]
    themes = ["Tales of legendary heroes", "Desert landscapes", "Joyful festival celebrations", "Romantic ballads"]
    return f"""**Genre:** Rajasthani Folk\n**Instrumentation:** {', '.join(random.sample(instruments, random.randint(3, 4)))}\n**Key Feature:** Use of unique regional instruments and powerful, high-pitched vocals.\n**Theme:** {random.choice(themes)}\n**Prompt:** '{prompt}'"""
