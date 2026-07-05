"""
utils/inference.py
-------------------
Loads the saved model + vectorizer once at app startup, and exposes a
predict() function that returns prediction, confidence, probabilities,
and explainable-AI keyword evidence.
"""

import json
import os
import time

import joblib
import numpy as np

from utils.preprocess import clean_text

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_model")

_model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
_vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))

with open(os.path.join(MODEL_DIR, "metadata.json")) as f:
    METADATA = json.load(f)

_feature_names = np.array(_vectorizer.get_feature_names_out())

# Try to get per-feature weights for explainability (works for linear models)
_coef = None
if hasattr(_model, "coef_"):
    _coef = _model.coef_.ravel()


def _get_probabilities(vec):
    """Return (real_prob, fake_prob) as percentages, robust across model types
    and scikit-learn versions (falls back gracefully if an attribute API
    changes between versions)."""
    try:
        if hasattr(_model, "predict_proba"):
            proba = _model.predict_proba(vec)[0]
            real_p, fake_p = proba[0], proba[1]
            return float(real_p) * 100, float(fake_p) * 100
    except Exception:
        pass

    try:
        if hasattr(_model, "decision_function"):
            score = _model.decision_function(vec)[0]
            fake_p = 1 / (1 + np.exp(-score))
            real_p = 1 - fake_p
            return float(real_p) * 100, float(fake_p) * 100
    except Exception:
        pass

    pred = _model.predict(vec)[0]
    fake_p, real_p = (1.0, 0.0) if pred == 1 else (0.0, 1.0)
    return real_p * 100, fake_p * 100


def _top_keywords(vec, prediction_label, top_n=8):
    """
    Explainable AI: find which words in THIS article contributed most
    to the prediction, using TF-IDF weight * model coefficient (if linear),
    otherwise just the highest TF-IDF terms present.
    """
    row = vec.toarray()[0]
    nonzero_idx = np.nonzero(row)[0]
    if len(nonzero_idx) == 0:
        return []

    if _coef is not None:
        contributions = row[nonzero_idx] * _coef[nonzero_idx]
    else:
        contributions = row[nonzero_idx]

    order = np.argsort(-np.abs(contributions))[:top_n]
    keywords = []
    for i in order:
        idx = nonzero_idx[i]
        word = _feature_names[idx]
        weight = float(contributions[i])
        leans_fake = weight > 0 if _coef is not None else (prediction_label == "Fake")
        keywords.append({
            "word": word,
            "weight": round(abs(weight), 4),
            "leans": "Fake" if leans_fake else "Real",
        })
    return keywords


def predict(title: str, article_text: str):
    start = time.time()

    full_text = f"{title or ''} {article_text or ''}"
    cleaned = clean_text(full_text)
    vec = _vectorizer.transform([cleaned])

    pred_class = _model.predict(vec)[0]
    real_prob, fake_prob = _get_probabilities(vec)

    prediction = "Fake" if pred_class == 1 else "Real"
    confidence = fake_prob if prediction == "Fake" else real_prob

    keywords = _top_keywords(vec, prediction)

    elapsed_ms = round((time.time() - start) * 1000, 2)

    return {
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "fake_probability": round(fake_prob, 2),
        "real_probability": round(real_prob, 2),
        "keywords": keywords,
        "processing_time_ms": elapsed_ms,
        "model_used": METADATA.get("best_model", "Unknown"),
    }
