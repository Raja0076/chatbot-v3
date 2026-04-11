import os
import joblib

# Get backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Models directory
MODELS_DIR = os.path.join(BASE_DIR, "models")

VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
MODEL_PATH = os.path.join(MODELS_DIR, "naive_bayes.pkl")


# Load model and vectorizer
vectorizer = joblib.load(VECTORIZER_PATH)
model = joblib.load(MODEL_PATH)


def predict_intent(processed_text):
    """
    Predict intent without confidence
    """

    text_vector = vectorizer.transform([processed_text])

    predicted_intent = model.predict(text_vector)[0]

    return predicted_intent


def predict_intent_with_confidence(processed_text):
    """
    Predict intent with probability confidence
    """

    # Convert text to TF-IDF vector
    text_vector = vectorizer.transform([processed_text])

    # Predict intent
    predicted_intent = model.predict(text_vector)[0]

    # Get probabilities
    probabilities = model.predict_proba(text_vector)[0]

    # Get intent classes
    classes = model.classes_

    # Create dictionary of probabilities
    confidence_scores = {}

    for intent, prob in zip(classes, probabilities):
        confidence_scores[intent] = float(prob)

    # Highest confidence
    highest_confidence = max(confidence_scores.values())

    return predicted_intent, highest_confidence, confidence_scores