import os
from gtts import gTTS


def tamil_text_to_speech(text, output_path):
    tts = gTTS(text=text, lang="ta")
    tts.save(output_path)