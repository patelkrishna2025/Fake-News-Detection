"""
routes/dashboard_routes.py
----------------------------
Dashboard, history, analytics, search, admin, and report routes.
"""

import json
from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, send_file

from utils.db import get_conn, log_event
from utils.inference import METADATA

dash_bp = Blueprint("dashboard", __name__)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@dash_bp.route("/dashboard")
def dashboard():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) AS c FROM predictions").fetchone()["c"]
    fake = conn.execute("SELECT COUNT(*) AS c FROM predictions WHERE prediction='Fake'").fetchone()["c"]
    real = conn.execute("SELECT COUNT(*) AS c FROM predictions WHERE prediction='Real'").fetchone()["c"]
    today = conn.execute(
        "SELECT COUNT(*) AS c FROM predictions WHERE date(created_at) = date('now')"
    ).fetchone()["c"]
    recent = conn.execute(
        "SELECT * FROM predictions ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    conn.close()

    stats = {
        "total": total, "fake": fake, "real": real, "today": today,
        "model_name": METADATA.get("best_model", "Unknown"),
        "model_accuracy": METADATA["metrics"][METADATA["best_model"]]["accuracy"] * 100
        if METADATA.get("best_model") else 0,
    }
    return render_template("dashboard.html", stats=stats, recent=recent)


# ---------------------------------------------------------------------------
# History + Search
# ---------------------------------------------------------------------------
@dash_bp.route("/history")
def history():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 200").fetchall()
    conn.close()
    return render_template("history.html", rows=rows)


@dash_bp.route("/api/history")
def api_history():
    keyword = request.args.get("keyword", "").strip()
    date = request.args.get("date", "").strip()
    pred_type = request.args.get("type", "").strip()

    query = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title LIKE ? OR article_text LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    if date:
        query += " AND date(created_at) = ?"
        params.append(date)
    if pred_type in ("Fake", "Real"):
        query += " AND prediction = ?"
        params.append(pred_type)

    query += " ORDER BY created_at DESC LIMIT 200"

    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
@dash_bp.route("/analytics")
def analytics():
    return render_template("analytics.html")


@dash_bp.route("/api/stats")
def api_stats():
    conn = get_conn()
    rows = conn.execute("SELECT prediction, top_keywords, created_at FROM predictions").fetchall()
    conn.close()

    fake_count = sum(1 for r in rows if r["prediction"] == "Fake")
    real_count = sum(1 for r in rows if r["prediction"] == "Real")

    fake_words, real_words = Counter(), Counter()
    daily_counts = Counter()

    for r in rows:
        day = r["created_at"][:10] if r["created_at"] else "unknown"
        daily_counts[day] += 1
        try:
            kws = json.loads(r["top_keywords"]) if r["top_keywords"] else []
        except Exception:
            kws = []
        for kw in kws:
            if r["prediction"] == "Fake":
                fake_words[kw["word"]] += 1
            else:
                real_words[kw["word"]] += 1

    last_7_days = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        last_7_days.append({"date": day, "count": daily_counts.get(day, 0)})

    return jsonify({
        "fake_count": fake_count,
        "real_count": real_count,
        "top_fake_words": fake_words.most_common(10),
        "top_real_words": real_words.most_common(10),
        "weekly_trend": last_7_days,
        "model_metrics": METADATA["metrics"].get(METADATA.get("best_model"), {}),
    })


# ---------------------------------------------------------------------------
# Admin Panel
# ---------------------------------------------------------------------------
@dash_bp.route("/admin")
def admin():
    conn = get_conn()
    predictions = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 100").fetchall()
    logs = conn.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return render_template("admin.html", predictions=predictions, logs=logs, metadata=METADATA)


@dash_bp.route("/admin/delete/<int:pred_id>", methods=["POST"])
def admin_delete(pred_id):
    conn = get_conn()
    conn.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
    conn.commit()
    conn.close()
    log_event("WARNING", f"Admin deleted prediction #{pred_id}")
    return jsonify({"status": "deleted", "id": pred_id})


@dash_bp.route("/admin/export")
def admin_export():
    import csv
    import io

    conn = get_conn()
    rows = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    if rows:
        writer.writerow(rows[0].keys())
        for r in rows:
            writer.writerow(list(r))

    output.seek(0)
    buf = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(buf, mimetype="text/csv", as_attachment=True,
                      download_name="predictions_export.csv")
