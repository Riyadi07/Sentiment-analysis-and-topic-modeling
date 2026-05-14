from flask import Blueprint, jsonify
import pandas as pd
from config import DATA_PATH

preprocessing_bp = Blueprint('preprocessing', __name__)

def load_data():
    return pd.read_csv(DATA_PATH)

# 1️⃣ Case Folding
@preprocessing_bp.route('/case-folding', methods=['GET'])
def case_folding():
    df = load_data()
    return jsonify(
        df[['content', 'text']]
        .rename(columns={
            'content': 'sebelum',
            'text': 'sesudah'
        })
        .to_dict(orient='records')
    )

# 2️⃣ Cleaning
@preprocessing_bp.route('/cleaning', methods=['GET'])
def cleaning():
    df = load_data()
    return jsonify(
        df[['content', 'text']]
        .rename(columns={
            'content': 'sebelum',
            'text': 'sesudah'
        })
        .to_dict(orient='records')
    )

# 3️⃣ Normalization
@preprocessing_bp.route('/normalization', methods=['GET'])
def normalization():
    df = load_data()
    return jsonify(
        df[['text', 'content_normalized']]
        .rename(columns={
            'text': 'sebelum',
            'content_normalized': 'sesudah'
        })
        .to_dict(orient='records')
    )

# 4️⃣ Tokenizing
@preprocessing_bp.route('/tokenizing', methods=['GET'])
def tokenizing():
    df = load_data()
    return jsonify(
        df[['content_normalized', 'content_tokens']]
        .rename(columns={
            'content_normalized': 'sebelum',
            'content_tokens': 'sesudah'
        })
        .to_dict(orient='records')
    )

# 5️⃣ Filtering (Stopword Removal)
@preprocessing_bp.route('/filtering', methods=['GET'])
def filtering():
    df = load_data()
    return jsonify(
        df[['content_tokens', 'content_stopwords']]
        .rename(columns={
            'content_tokens': 'sebelum',
            'content_stopwords': 'sesudah'
        })
        .to_dict(orient='records')
    )

# 6️⃣ Stemming
@preprocessing_bp.route('/stemming', methods=['GET'])
def stemming():
    df = load_data()
    return jsonify(
        df[['content_stopwords', 'content_processed']]
        .rename(columns={
            'content_stopwords': 'sebelum',
            'content_processed': 'sesudah'
        })
        .to_dict(orient='records')
    )

# 7️⃣ Validation
@preprocessing_bp.route('/validation', methods=['GET'])
def validation():
    df = load_data()
    return jsonify(
        df[['content', 'content_processed']]
        .rename(columns={
            'content': 'sebelum',
            'content_processed': 'sesudah'
        })
        .to_dict(orient='records')
    )

