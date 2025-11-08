# utils.py
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # deterministic results

LANG_CODE_MAP = {
    "en": "eng_Latn",
    "te": "tel_Telu"
}

def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"
