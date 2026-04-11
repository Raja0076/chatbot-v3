import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from chatbot.preprocess import preprocess_text

# Load dataset
df = pd.read_csv("data/chat_data.csv")

# Preprocess
df["processed"] = df["question"].apply(preprocess_text)

X = df["processed"]
y = df["intent"]   # or "label" if you renamed it

# Proper split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Fit only on training
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)

# Transform test using same training vocabulary/IDF
X_test_vec = vectorizer.transform(X_test)

# Train model only on training split
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Predict on unseen test split
y_pred = model.predict(X_test_vec)

# Accuracy
acc = accuracy_score(y_test, y_pred)
print("Model Accuracy:", round(acc * 100, 2), "%")
print("\nDetailed Report:\n")
print(classification_report(y_test, y_pred))