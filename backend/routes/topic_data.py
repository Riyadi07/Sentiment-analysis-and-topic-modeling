from flask import Blueprint, jsonify
from services.topic_service import (
    CACHE,
    build_topic_cache
)

topic_data = Blueprint("topic_data", __name__)

@topic_data.route("/", methods=["GET"])
def topic_dashboard():
    for sentiment in ["positif", "netral", "negatif"]:
        if CACHE[sentiment] is None:
            CACHE[sentiment] = build_topic_cache(sentiment)

    return jsonify({
        "positive": CACHE["positif"],
        "neutral": CACHE["netral"],
        "negative": CACHE["negatif"]
    })