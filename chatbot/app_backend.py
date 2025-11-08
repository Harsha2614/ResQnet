import os
import io
import re
import numpy as np
import pandas as pd
import whisper
import librosa
import soundfile as sf
from pydub import AudioSegment
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from chatbot.utils import detect_lang, LANG_CODE_MAP
import session_config  # shared session setup

# ---------------- Paths ----------------
ART_DIR = "artifacts"
META_FILE = os.path.join(ART_DIR, "kb_meta.txt")
KB_SOURCE = os.path.join(os.path.dirname(__file__), "knowledge_base.csv")
KB_CSV = os.path.join(ART_DIR, "kb_rows.csv")
KB_EMB_EN = os.path.join(ART_DIR, "kb_embeddings_en.npy")
KB_EMB_TE = os.path.join(ART_DIR, "kb_embeddings_te.npy")

# ---------------- Flask App ----------------
app = Flask(
    __name__,
    static_url_path="/static",  # ✅ ensures static routes start with /chatbot/static/
    static_folder="static",             # ✅ points to chatbot/static/
    template_folder="templates"
)

from flask_cors import CORS

# Allow CORS from 8000 (combined app)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:8000"]}})

app.secret_key = "super_secret_key"
DEBUG_MODE = True

# ---------------- Load Models ----------------
print("🔹 Loading models... please wait")
embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
whisper_model = whisper.load_model("small")
print("✅ Models loaded successfully")

# ---------------- Instant Replies ----------------
INSTANT_REPLIES = {
    "hi": "Hello! 👋 I'm your safety assistant. How can I help you today?",
    "hello": "Hi there! 😊 I’m here to guide you about safety, disaster response, and nearby help centers.",
    "hey": "Hey! 👋 How can I assist you today?",
    "good morning": "Good morning ☀️! Stay safe and alert today.",
    "good evening": "Good evening 🌆! Hope you're safe and doing well.",
    "bye": "Goodbye 👋 Take care and stay safe.",
    "thanks": "You're welcome! 😊 Always here to help.",
    "thank you": "You're most welcome 🙏",
    "who are you": "I'm your offline emergency chatbot assistant designed to help the appliaction information and small tips."
}

# ---------------- Load Knowledge Base ----------------
def load_kb_into_instant_replies():
    """Merge KB questions into instant replies (English + Telugu)."""
    try:
        if not os.path.exists(KB_SOURCE):
            print(f"⚠️ Knowledge base '{KB_SOURCE}' not found — skipping merge.")
            return
        df = pd.read_csv(KB_SOURCE)
        count = 0
        for _, row in df.iterrows():
            q_en = str(row.get("question_en", "")).strip().lower()
            a_en = str(row.get("answer_en", "")).strip()
            q_te = str(row.get("question_te", "")).strip().lower()
            a_te = str(row.get("answer_te", "")).strip()
            if q_en and a_en:
                INSTANT_REPLIES[q_en] = a_en
                count += 1
            if q_te and a_te:
                INSTANT_REPLIES[q_te] = a_te
                count += 1
        print(f"✅ Integrated {count} KB entries into INSTANT_REPLIES.")
    except Exception as e:
        print(f"❌ KB merge error: {e}")

load_kb_into_instant_replies()

# ---------------- Helpers ----------------
def get_instant_reply(user_text):
    text_lower = user_text.lower()
    for key, value in INSTANT_REPLIES.items():
        if key in text_lower or text_lower in key:
            return value
    return None

def preprocess_query(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\u0C00-\u0C7F\s]", "", text)
    return text

def rebuild_kb():
    """Rebuild embeddings for English + Telugu KB."""
    try:
        os.makedirs(ART_DIR, exist_ok=True)
        df = pd.read_csv(KB_SOURCE)
        df["clean_question_en"] = df["question_en"].fillna("").apply(preprocess_query)
        df["clean_question_te"] = df["question_te"].fillna("").apply(preprocess_query)

        en_texts = df["clean_question_en"].tolist()
        te_texts = df["clean_question_te"].tolist()

        print("⚙️ Building embeddings...")
        emb_en = embedder.encode(en_texts, convert_to_numpy=True, normalize_embeddings=True)
        emb_te = embedder.encode(te_texts, convert_to_numpy=True, normalize_embeddings=True)

        np.save(KB_EMB_EN, emb_en)
        np.save(KB_EMB_TE, emb_te)
        df.to_csv(KB_CSV, index=False)
        print(f"✅ KB rebuilt successfully ({len(df)} entries).")
        return f"✅ KB rebuilt with {len(df)} entries", 200
    except Exception as e:
        return f"❌ Error rebuilding KB: {e}", 500

def cosine_search(query: str, lang_code: str = "en"):
    """Search KB using cosine similarity."""
    if not (os.path.exists(KB_CSV) and os.path.exists(KB_EMB_EN) and os.path.exists(KB_EMB_TE)):
        rebuild_kb()

    df = pd.read_csv(KB_CSV)
    q_emb = embedder.encode([preprocess_query(query)], convert_to_numpy=True, normalize_embeddings=True)
    kb_path = KB_EMB_TE if lang_code == "te" else KB_EMB_EN
    kb_embeddings = np.load(kb_path)

    if kb_embeddings.shape[1] != q_emb.shape[1]:
        print("⚠️ Dimension mismatch detected — rebuilding KB...")
        rebuild_kb()
        kb_embeddings = np.load(kb_path)

    sims = np.dot(kb_embeddings, q_emb.T).flatten()
    best_idx = int(np.argmax(sims))
    score = float(sims[best_idx])

    if score < 0.60:
        return None

    row = df.iloc[best_idx]
    return {"answer_en": row["answer_en"], "answer_te": row["answer_te"], "score": score}

def transcribe_audio_bytes(file_bytes: bytes):
    """Convert audio → text."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="webm")
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        buffer.seek(0)
        data, samplerate = sf.read(buffer, dtype="float32")
    except Exception as e:
        print("❌ Audio error:", e)
        raise ValueError("Invalid audio")

    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if samplerate != 16000:
        data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)

    result = whisper_model.transcribe(data, fp16=False, language=None)
    lang = result.get("language", "unknown")
    text = result.get("text", "").strip()
    print(f"🎧 Detected ({lang}): {text}")
    return lang, text

# ---------------- Routes (Now prefixed under /chatbot/) ----------------
@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.form.get("message", "").strip()
    if not user_text:
        return jsonify({"response": "Please enter a message"}), 400

    reply = get_instant_reply(user_text)
    if reply:
        return jsonify({"response": reply})

    lang_code = detect_lang(user_text)
    if lang_code not in ["te", "en"]:
        lang_code = "en"

    kb_result = cosine_search(user_text, lang_code)
    if kb_result:
        answer = kb_result["answer_te"] if lang_code == "te" else kb_result["answer_en"]
        return jsonify({"response": answer, "confidence": kb_result["score"]})

    fallback = (
        "😕 Sorry, I couldn't find this information.\n"
        "Try asking about:\n"
        "• Safe navigation\n• Emergency help\n• Safety kit\n• Fake news check"
    )
    return jsonify({"response": fallback})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file_bytes = request.files["file"].read()
    lang, text = transcribe_audio_bytes(file_bytes)
    lang_code = "te" if lang.startswith("te") else "en"

    kb_result = cosine_search(text, lang_code)
    if kb_result:
        answer = kb_result["answer_te"] if lang_code == "te" else kb_result["answer_en"]
    else:
        answer = (
            "😕 క్షమించండి, ఈ సమాచారాన్ని కనుగొనలేకపోయాను."
            if lang_code == "te"
            else "😕 Sorry, I couldn't find this information."
        )

    return jsonify({"language": lang_code, "question": text, "response": answer})

@app.route("/rebuild_kb", methods=["POST"])
def rebuild():
    msg, code = rebuild_kb()
    return jsonify({"status": msg}), code

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- Startup ----------------
if not os.path.exists(ART_DIR):
    os.makedirs(ART_DIR, exist_ok=True)

if not os.path.exists(KB_EMB_EN) or not os.path.exists(KB_EMB_TE):
    print("⚙️ No embeddings found — rebuilding...")
    msg, code = rebuild_kb()
    print(msg)
else:
    print("✅ Embeddings found — skipping rebuild.")
if __name__ == "__main__":
    print("🤖 Chatbot backend running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True,use_reloader=False)