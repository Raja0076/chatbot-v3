from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
import platform

from chatbot.audio_processor import convert_webm_to_wav
from chatbot.speech_to_text import tamil_speech_to_text
from chatbot.translator import translate_tamil_to_english, translate_english_to_tamil
from chatbot.preprocess import preprocess_text
from chatbot.intent_predictor import predict_intent_with_confidence
from chatbot.response_handler import get_response
from chatbot.llama_fallback import get_llama_response
from chatbot.text_to_speech import tamil_text_to_speech
from data.responses import responses

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ── Fallback decision constants ───────────────────────────────────────────────
HARD_MIN   = 0.05   # below this → always fallback
SOFT_HIGH  = 0.07   # above this → always trust trained model
MIN_MARGIN = 0.01   # middle zone margin check

USE_SIGNAL_TIMEOUT = platform.system() != "Windows"
if USE_SIGNAL_TIMEOUT:
    import signal

    def _timeout_handler(signum, frame):
        raise TimeoutError("Model generation timed out")


def should_use_fallback(
    intent: str,
    confidence: float,
    confidence_scores: dict,
    has_chat_history: bool = False
) -> bool:
    # Rule 1 — hard floor
    if confidence < HARD_MIN:
        return True

    # Rule 2 — ceiling, always trust trained model
    if confidence >= SOFT_HIGH:
        return False

    # Rule 3 — middle zone margin check
    if confidence_scores:
        sorted_scores = sorted(confidence_scores.values(), reverse=True)
        top    = sorted_scores[0]
        second = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
        margin = top - second

        # Be more lenient mid-conversation — STT gives short outputs
        effective_margin = MIN_MARGIN * (0.5 if has_chat_history else 1.0)

        if margin < effective_margin:
            return True

    # Rule 4 — explicit default intent
    if intent == "default":
        return True

    return False


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Tamil Voice Enabled Student Chatbot backend is running"})


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)


@app.route("/voice-chat", methods=["POST"])
def voice_chat():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file received"}), 400

    audio_file = request.files["audio"]

    webm_path = os.path.join(UPLOADS_DIR, "audio_recording.webm")
    wav_path  = os.path.join(UPLOADS_DIR, "audio_recording.wav")

    reply_audio_filename = f"bot_reply_{uuid.uuid4().hex}.mp3"
    reply_audio_path     = os.path.join(UPLOADS_DIR, reply_audio_filename)

    audio_file.save(webm_path)

    if USE_SIGNAL_TIMEOUT:
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(100)

    try:
        convert_webm_to_wav(webm_path, wav_path)

        tamil_text     = tamil_speech_to_text(wav_path)
        english_text   = translate_tamil_to_english(tamil_text)
        processed_text = preprocess_text(english_text)

        # ── Parse chat history ────────────────────────────────────────────────
        chat_history = []
        if "chat_history" in request.form:
            try:
                chat_history = json.loads(request.form.get("chat_history"))
                print(f"[Route] Chat history received: {len(chat_history)} turns")
            except Exception:
                chat_history = []

        # ── Read last successful intent from frontend ─────────────────────────
        last_intent = None
        if "last_intent" in request.form:
            last_intent = request.form.get("last_intent")
            print(f"[Route] Last known intent from frontend: {last_intent}")

        # ── Intent prediction ─────────────────────────────────────────────────
        intent, confidence, confidence_scores = predict_intent_with_confidence(processed_text)
        print(f"[Intent] Predicted: {intent}  Confidence: {confidence:.4f}")

        if confidence < HARD_MIN:
            intent = "default"

        # ── Step 1: Get trained model response ───────────────────────────────
        english_reply   = get_response(intent)
        fallback_needed = should_use_fallback(
            intent,
            confidence,
            confidence_scores,
            has_chat_history=len(chat_history) > 0
        )

        if not fallback_needed and english_reply == responses.get("default"):
            fallback_needed = True

        # ── Context recovery ──────────────────────────────────────────────────────
        used_context_recovery = False
        if fallback_needed and last_intent and last_intent != "default":

            # If confidence is so low that intent was forced to "default",
            # it means the model has no idea — skip recovery, let Groq handle it
            if intent == "default":
                print(
                    f"[Context Recovery] Intent forced to 'default' (confidence={confidence:.4f}) "
                    f"— skipping recovery, Groq will handle with full chat history"
                )

            else:
                # Detect if user changed topic
                topic_changed = (
                    intent != last_intent and
                    confidence >= HARD_MIN
                )

                if topic_changed:
                    print(
                        f"[Context Recovery] Topic changed from '{last_intent}' to "
                        f"'{intent}' — skipping recovery, sending to Groq"
                    )
                else:
                    context_response = get_response(last_intent)
                    if context_response and context_response != responses.get("default"):
                        print(
                            f"[Context Recovery] Low confidence ({confidence:.4f}) on "
                            f"'{intent}' — prior intent '{last_intent}' is valid, "
                            f"using trained model"
                        )
                        intent                = last_intent
                        english_reply         = context_response
                        fallback_needed       = False
                        used_context_recovery = True
        # ── Step 2: Use trained model or Groq fallback ────────────────────────
        if not fallback_needed:
            print(
                f"[Own Model] Using trained model. intent={intent}  "
                f"confidence={confidence:.4f}"
                f"{'  [context recovery]' if used_context_recovery else ''}"
            )
        else:
            print(
                f"[Fallback] Triggering Groq fallback. "
                f"intent={intent}  confidence={confidence:.4f} "
                f"— reason: {'low confidence' if confidence < HARD_MIN else 'topic change or default'}"
            )
            try:
                groq_text = get_llama_response(english_text, chat_history)
                if groq_text:
                    print("[Fallback] Groq returned:", groq_text[:120])
                    english_reply = groq_text
                else:
                    print("[Fallback] Groq returned no text; keeping trained model response")
            except Exception as exc:
                print("[Fallback] Groq failed:", type(exc).__name__, exc)
                print("[Fallback] Keeping trained model response:", english_reply)

        # ── Step 3: Translate and TTS ─────────────────────────────────────────
        tamil_reply = translate_english_to_tamil(english_reply)
        tamil_text_to_speech(tamil_reply, reply_audio_path)

        return jsonify({
            "tamil_question":        tamil_text,
            "english_question":      english_text,
            "processed_text":        processed_text,
            "intent":                intent,
            "confidence":            confidence,
            "confidence_scores":     confidence_scores,
            "english_reply":         english_reply,
            "tamil_reply":           tamil_reply,
            "audio_url":             f"http://127.0.0.1:5000/uploads/{reply_audio_filename}",
            "chat_history":          chat_history,
            "used_fallback":         fallback_needed,
            "used_context_recovery": used_context_recovery,
        })

    except TimeoutError:
        return jsonify({"error": "Response took too long. Please try again."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if USE_SIGNAL_TIMEOUT:
            signal.alarm(0)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)