from flask import Blueprint, jsonify
import pandas as pd
from config import DATA_PATH
from database.models import AnalysisItem

dashboard_bp = Blueprint("dashboard", __name__)

# ======================
# NORMALISASI LABEL SENTIMEN
# ======================
def normalize_label(label):
    if not label:
        return None

    label = label.lower()
    if label == "positif":
        return "Positif"
    if label == "negatif":
        return "Negatif"
    if label == "netral":
        return "Netral"
    return label


@dashboard_bp.route("/", methods=["GET"])
def dashboard():
    # ======================
    # DATA CSV (DATASET PENELITIAN)
    # ======================
    df = pd.read_csv(DATA_PATH)

    csv_counts_raw = df["sentiment_label_manual"].value_counts().to_dict()
    csv_counts = {}

    for k, v in csv_counts_raw.items():
        label = normalize_label(k)
        if label:
            csv_counts[label] = v

    csv_total = len(df)

    # ======================
    # DATA INPUT USER (DATABASE)
    # ======================
    db_items = AnalysisItem.query.all()
    db_counts = {}

    for item in db_items:
        label = normalize_label(item.sentiment)
        if label:
            db_counts[label] = db_counts.get(label, 0) + 1

    db_total = len(db_items)

    # ======================
    # GABUNG DISTRIBUSI
    # ======================
    all_labels = set(csv_counts.keys()) | set(db_counts.keys())

    combined_distribution = {
        label: csv_counts.get(label, 0) + db_counts.get(label, 0)
        for label in all_labels
    }

    # ======================
    # RESPONSE
    # ======================
    return jsonify({
        "total_data": csv_total + db_total,

        "distribution": combined_distribution,

        "csv_only": {
            "total": csv_total,
            "distribution": csv_counts
        },

        "input_only": {
            "total": db_total,
            "distribution": db_counts
        }
    })
