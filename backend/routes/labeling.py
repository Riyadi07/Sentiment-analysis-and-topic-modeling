from flask import Blueprint, jsonify
import pandas as pd
from config import DATA_PATH

labeling_bp = Blueprint('labeling', __name__)

@labeling_bp.route('/', methods=['GET'])
def view_labeling():
    df = pd.read_csv(DATA_PATH)

    return jsonify({
        "manual": df['sentiment_label_manual'].value_counts().to_dict(),
        "score": df['sentiment_label'].value_counts().to_dict()
    })

@labeling_bp.route('/data', methods=['GET'])
def labeling_data():
    df = pd.read_csv(DATA_PATH)

    return jsonify(
        df[['content', 'sentiment_label', 'sentiment_label_manual']]
        .to_dict(orient='records')
    )
