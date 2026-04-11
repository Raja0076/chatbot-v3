from chatbot.intent_predictor import predict_intent_with_confidence
from chatbot.preprocess import preprocess_text

test_questions = [
    "internship tips for students",
    "How can I improve coding skills",
    "what stream should i choose if i like business"
]

print("------ Intent Prediction Unit Testing ------\n")

for question in test_questions:
    processed = preprocess_text(question)

    intent, confidence, scores = predict_intent_with_confidence(processed)

    print("Input Question:", question)
    print("Processed Text:", processed)
    print("Predicted Intent:", intent)
    print("Confidence Score:", confidence)
    print("-" * 50)