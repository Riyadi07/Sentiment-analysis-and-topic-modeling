from flask import Blueprint, request, jsonify
import pandas as pd
import os

from database.db import db
from database.models import AnalysisInput, AnalysisItem
from services.preprocessing import preprocess_text
from services.sentiment_analysis import predict_sentiment
from services.topic_modeling import run_lda_input
from config import UPLOAD_FOLDER

input_analysis_bp = Blueprint("input_analysis", __name__)

# 🔥 TAMBAHAN: SAFE LDA FUNCTION (biar tidak error kalau data sedikit)
def safe_lda(texts):
    if not texts or len(texts) < 2:
        return {
            "topics": [],
            "wordcloud": None,
            "message": "Data tidak cukup untuk topic modeling"
        }
    return run_lda_input(texts)


@input_analysis_bp.route("/text", methods=["POST"])
def analyze_text():
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "Text required"}), 400

    # parent
    parent = AnalysisInput(
        input_type="text",
        source="manual text"
    )
    db.session.add(parent)
    db.session.flush()

    # pipeline
    processed = preprocess_text(text)
    sentiment = predict_sentiment([processed])[0]

    item = AnalysisItem(
        input_id=parent.id,
        original_text=text,
        processed_text=processed,
        sentiment=sentiment
    )
    db.session.add(item)
    db.session.commit()

    # ⚠️ LDA tetap tidak dilakukan untuk 1 data (tidak diubah)
    topics = {
        "best_k": None,
        "topics": [],
        "coherence_scores": [],
        "wordcloud": None,
        "message": "Topic modeling tidak dilakukan karena data hanya satu"
    }

    return jsonify({
        "input_id": parent.id,
        "input_type": "text",

        "sentiment": sentiment,
        "sentiment_distribution": None,

        "topics": topics
    })


@input_analysis_bp.route("/upload", methods=["POST"])
def analyze_file():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "Invalid file"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    if file.filename.endswith(".csv"):
        df = pd.read_csv(path)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(path)
    else:
        return jsonify({"error": "CSV/XLSX only"}), 400

    if "content" not in df.columns:
        return jsonify({"error": "Column 'content' not found"}), 400

    parent = AnalysisInput(
        input_type="file",
        source=file.filename
    )
    db.session.add(parent)
    db.session.flush()

    df["processed"] = df["content"].astype(str).apply(preprocess_text)
    sentiments = predict_sentiment(df["processed"].tolist())

    # tetap pakai lowercase (tidak diubah)
    df["sentiment"] = pd.Series(sentiments).str.lower()

    for _, r in df.iterrows():
        db.session.add(
            AnalysisItem(
                input_id=parent.id,
                original_text=r["content"],
                processed_text=r["processed"],
                sentiment=r["sentiment"]
            )
        )

    db.session.commit()

    sentiment_dist = df["sentiment"].value_counts().to_dict()

    # 🔥 TAMBAHAN NETRAL
    texts_pos = df[df["sentiment"] == "positif"]["processed"].tolist()
    texts_neu = df[df["sentiment"] == "netral"]["processed"].tolist()
    texts_neg = df[df["sentiment"] == "negatif"]["processed"].tolist()

    # 🔥 UPDATE TOPICS (sekarang 3 kelas)
    topics = {
        "positive": safe_lda(texts_pos),
        "neutral": safe_lda(texts_neu),
        "negative": safe_lda(texts_neg)
    }

    return jsonify({
        "input_id": parent.id,
        "input_type": "file",
        "sentiment_distribution": sentiment_dist,
        "topics": topics
    })


@input_analysis_bp.route("/history", methods=["GET"])
def history():
    rows = AnalysisInput.query.order_by(
        AnalysisInput.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": r.id,
            "input_type": r.input_type,
            "source": r.source,
            "total_items": len(r.items),
            "created_at": r.created_at.isoformat()
        }
        for r in rows
    ])


@input_analysis_bp.route("/<int:input_id>", methods=["GET"])
def detail(input_id):
    row = AnalysisInput.query.get_or_404(input_id)

    return jsonify({
        "id": row.id,
        "input_type": row.input_type,
        "source": row.source,
        "created_at": row.created_at.isoformat(),
        "items": [
            {
                "id": i.id,
                "text": i.original_text,
                "sentiment": i.sentiment
            }
            for i in row.items
        ]
    })