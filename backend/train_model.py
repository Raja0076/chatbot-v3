import os
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from chatbot.preprocess import preprocess_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "chat_data.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)


def main():
    df = pd.read_csv(DATA_PATH)

    if "question" not in df.columns or "intent" not in df.columns:
        raise ValueError("CSV must contain 'question' and 'intent' columns.")

    df = df.dropna(subset=["question", "intent"]).copy()

    df["processed_question"] = df["question"].astype(str).apply(preprocess_text)

    X = df["processed_question"]
    y = df["intent"].astype(str)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X_vectorized = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vectorized, y)

    vectorizer_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
    model_path = os.path.join(MODELS_DIR, "naive_bayes.pkl")

    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(model, model_path)

    print("Model training completed successfully.")
    print(f"Vectorizer saved to: {vectorizer_path}")
    print(f"Model saved to: {model_path}")
    print(f"Total training samples: {len(df)}")
    print("Intent counts:")
    print(df["intent"].value_counts())


if __name__ == "__main__":
    main()