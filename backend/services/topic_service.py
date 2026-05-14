import os
import joblib
import pandas as pd
import base64
from io import BytesIO
from wordcloud import WordCloud

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

lda_negative = joblib.load(os.path.join(MODEL_DIR, "modeling_negative.pkl"))
lda_positive = joblib.load(os.path.join(MODEL_DIR, "modeling_positive.pkl"))
lda_neutral = joblib.load(os.path.join(MODEL_DIR, "modeling_neutral.pkl"))

LDA_MODELS = {
    "negatif": lda_negative,
    "netral": lda_neutral,
    "positif": lda_positive
}

sentiment_map = {
    "negatif": "negative",
    "netral": "neutral",
    "positif": "positive"
}

DISPLAY_TOPICS = {
    "positif": 4,
    "netral": None,
    "negatif": None
}

CACHE = {
    "positif": None,
    "netral": None,
    "negatif": None
}

def build_topic_cache(sentiment):
    return {
        "topics": get_topics(sentiment),
        "coherence_scores": get_coherence_data(sentiment),
        "best_k": get_best_k(sentiment),
        "wordcloud_per_topic": get_wordcloud(sentiment)
    }

def get_topics(sentiment, num_words=10):
    model = LDA_MODELS[sentiment]

    max_topics = DISPLAY_TOPICS.get(sentiment)
    total_topics = model.num_topics
    limit = max_topics if max_topics else total_topics

    topics = []
    for i, topic in model.print_topics(num_words=num_words):
        if i >= limit:
            break
        topics.append({
            "topic_id": i,
            "keywords": topic
        })

    return topics

def get_coherence_data(sentiment):
    key = sentiment_map[sentiment]
    path = os.path.join(DATA_DIR, f"coherence_{key}.csv")

    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)
    return df.values.tolist() 

def get_best_k(sentiment):
    if DISPLAY_TOPICS.get(sentiment) is not None:
        return DISPLAY_TOPICS[sentiment]

    data = get_coherence_data(sentiment)
    if not data:
        return 0

    best = max(data, key=lambda x: x[1])
    return best[0]


def get_wordcloud(sentiment, num_words=100):
    model = LDA_MODELS[sentiment]

    max_topics = DISPLAY_TOPICS.get(sentiment)
    total_topics = model.num_topics
    limit = max_topics if max_topics is not None else total_topics

    result = {}

    for i in range(min(limit, total_topics)):
        topic_words = model.show_topic(i, topn=num_words)
        freq = {word: prob for word, prob in topic_words}

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white"
        ).generate_from_frequencies(freq)

        buffer = BytesIO()
        wc.to_image().save(buffer, format="PNG")
        buffer.seek(0)

        result[i] = base64.b64encode(buffer.read()).decode()

    return result

