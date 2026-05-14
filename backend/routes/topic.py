# routes/topic.py
from flask import Blueprint, jsonify, request
import pandas as pd
from config import DATA_PATH
from services.topic_modeling import run_lda

topic_bp = Blueprint('topic', __name__)

@topic_bp.route('/', methods=['GET'])
def topics_all():
    df = pd.read_csv(DATA_PATH)

    texts_pos = df[df['sentiment_label_manual'] == 'Positif']['content_processed'].dropna().tolist()
    texts_neg = df[df['sentiment_label_manual'] == 'Negatif']['content_processed'].dropna().tolist()

    pos_result = run_lda(texts_pos)
    neg_result = run_lda(texts_neg)

    return jsonify({
        "positive": pos_result,
        "negative": neg_result
    })

