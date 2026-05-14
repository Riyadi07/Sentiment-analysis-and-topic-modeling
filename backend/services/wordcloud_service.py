from wordcloud import WordCloud
import base64
from io import BytesIO
import pandas as pd

def generate_wordcloud(texts, labels=None):
    """
    texts: pd.Series atau list berisi teks
    labels: pd.Series berisi label yang sesuai (optional)
    
    Jika labels diberikan, akan menghasilkan dict {label: base64_image}
    Jika tidak, menghasilkan base64 string gabungan semua teks
    """
    
    # Helper untuk convert ke string list
    def to_list_of_str(x):
        if isinstance(x, pd.Series):
            return x.astype(str).tolist()
        elif isinstance(x, list):
            return [str(t) for t in x]
        else:
            raise ValueError("texts harus list atau pd.Series")
    
    if labels is None:
        # Wordcloud gabungan semua teks
        text = ' '.join(to_list_of_str(texts))
        wc = WordCloud(width=800, height=400, background_color='white').generate(text)
        buffer = BytesIO()
        wc.to_image().save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()
    
    # Wordcloud per label
    result = {}
    labels_list = labels.tolist() if isinstance(labels, pd.Series) else labels
    for label in set(labels_list):
        texts_label = [texts[i] for i, l in enumerate(labels_list) if l == label]
        text = ' '.join(to_list_of_str(texts_label))
        wc = WordCloud(width=800, height=400, background_color='white').generate(text)
        buffer = BytesIO()
        wc.to_image().save(buffer, format='PNG')
        buffer.seek(0)
        result[label] = base64.b64encode(buffer.read()).decode()
    
    return result


def wordcloud_per_topic(model, num_words=100, max_topics=None):
    """
    Return:
    {
      0: "base64...",
      1: "base64...",
      ...
    }

    max_topics:
    - None  -> tampilkan semua topik
    - int   -> batasi jumlah topik (misal 4)
    """
    result = {}

    total_topics = model.num_topics
    limit = max_topics if max_topics is not None else total_topics

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

