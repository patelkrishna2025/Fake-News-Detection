"""
routes/main_routes.py
----------------------
Core user-facing routes: home/predict page, about, settings.
"""

import json

from flask import Blueprint, render_template, request, jsonify

from utils.inference import predict as run_prediction
from utils.db import save_prediction, log_event

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/predict", methods=["POST"])
def predict_route():
    title = request.form.get("title", "").strip()
    article = request.form.get("article", "").strip()

    if not article:
        return jsonify({"error": "Article text is required."}), 400

    result = run_prediction(title, article)

    pred_id = save_prediction(
        title=title,
        article_text=article,
        prediction=result["prediction"],
        confidence=result["confidence"],
        fake_probability=result["fake_probability"],
        real_probability=result["real_probability"],
        top_keywords_json=json.dumps(result["keywords"]),
        processing_time_ms=result["processing_time_ms"],
    )
    log_event("INFO", f"Prediction #{pred_id} -> {result['prediction']} "
                       f"({result['confidence']}% confidence)")

    result["id"] = pred_id
    return jsonify(result)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/settings")
def settings():
    return render_template("settings.html")
