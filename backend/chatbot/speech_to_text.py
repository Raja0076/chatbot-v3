import speech_recognition as sr


def tamil_speech_to_text(wav_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    tamil_text = recognizer.recognize_google(audio_data, language="ta-IN")
    return tamil_text