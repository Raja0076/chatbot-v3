from deep_translator import GoogleTranslator


def translate_tamil_to_english(tamil_text):
    try:
        return GoogleTranslator(source='tamil', target='english').translate(tamil_text)
    except Exception:
        return tamil_text


def translate_english_to_tamil(english_text):
    try:
        return GoogleTranslator(source='english', target='tamil').translate(english_text)
    except Exception:
        return english_text