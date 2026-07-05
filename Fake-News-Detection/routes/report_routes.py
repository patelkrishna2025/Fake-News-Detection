"""
routes/report_routes.py
-------------------------
Generates a PDF report for a given prediction using ReportLab
(fully offline, no external services).
"""

import io
import json

from flask import Blueprint, send_file, abort
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle)
from reportlab.lib import colors

from utils.db import get_conn

report_bp = Blueprint("report", __name__)


@report_bp.route("/report/<int:pred_id>")
def generate_report(pred_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,)).fetchone()
    conn.close()

    if row is None:
        abort(404)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI Fake News Detection - Prediction Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph(f"<b>Title:</b> {row['title'] or 'N/A'}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {row['created_at']}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))

    color = colors.red if row["prediction"] == "Fake" else colors.green
    elements.append(Paragraph(
        f"<b>Prediction:</b> <font color='{color}'>{row['prediction']}</font>", styles["Heading2"]))
    elements.append(Paragraph(f"<b>Confidence:</b> {row['confidence']}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Processing Time:</b> {row['processing_time_ms']} ms", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))

    data = [["Class", "Probability"],
            ["Real", f"{row['real_probability']}%"],
            ["Fake", f"{row['fake_probability']}%"]]
    table = Table(data, colWidths=[6 * cm, 6 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.4 * cm))

    try:
        keywords = json.loads(row["top_keywords"]) if row["top_keywords"] else []
    except Exception:
        keywords = []

    if keywords:
        elements.append(Paragraph("<b>Influential Keywords:</b>", styles["Heading3"]))
        kw_data = [["Word", "Weight", "Leans"]] + [
            [k["word"], str(k["weight"]), k["leans"]] for k in keywords
        ]
        kw_table = Table(kw_data, colWidths=[5 * cm, 4 * cm, 4 * cm])
        kw_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(kw_table)
        elements.append(Spacer(1, 0.4 * cm))

    elements.append(Paragraph("<b>Article Text:</b>", styles["Heading3"]))
    elements.append(Paragraph(row["article_text"][:3000], styles["Normal"]))

    doc.build(elements)
    buf.seek(0)

    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                      download_name=f"report_{pred_id}.pdf")
