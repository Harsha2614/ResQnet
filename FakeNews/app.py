# -*- coding: utf-8 -*-
"""
Fake News Detection Flask App (Port 7000)
Compatible with combined.py integration
"""

from flask import Flask, render_template, request
import joblib
import re
import os

# ---------------- Flask Setup ----------------
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# ---------------- Model Paths ----------------
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "model")   # ✅ Correct folder name
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
RFC_PATH = os.path.join(MODEL_DIR, "randomforest.pkl")

# ---------------- Load Models ----------------
try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    RFC = joblib.load(RFC_PATH)
    print("✅ Fake News Model and Vectorizer loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model/vectorizer: {e}")

# ---------------- Helper Functions ----------------
def clean_text(text):
    """Clean and normalize input text."""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def output_label(n):
    """Return readable label from numeric prediction."""
    return "❌ Fake News" if n == 0 else "✅ Not Fake News"

# ---------------- Routes ----------------
@app.route("/", methods=["GET"])
def home():
    """Home page"""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """Handle prediction request from form."""
    if request.method == "POST":
        news = request.form["news"]
        cleaned = clean_text(news)
        vector_input = vectorizer.transform([cleaned])

        # You can re-enable these if models exist
        # pred_lr = LR.predict(vector_input)[0]
        # pred_dt = DT.predict(vector_input)[0]
        # pred_gbc = GBC.predict(vector_input)[0]
        pred_rfc = RFC.predict(vector_input)[0]

        return render_template(
            "index.html",
            news=news,
            pred_lr="Model not loaded",
            pred_dt="Model not loaded",
            pred_gbc="Model not loaded",
            pred_rfc=output_label(pred_rfc)
        )

# ---------------- Run App ----------------
if __name__ == "__main__":
    print("📰 Fake News backend running on http://127.0.0.1:7000")
    app.run(host="0.0.0.0", port=7000, debug=True, use_reloader=False)
