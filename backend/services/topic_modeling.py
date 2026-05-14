from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from services.wordcloud_service import generate_wordcloud
from wordcloud import WordCloud
import base64
from io import BytesIO


def find_best_k(texts, start=2, limit=10):
    tokenized = [t.split() for t in texts if isinstance(t, str)]

    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=5, no_above=0.5)

    corpus = [dictionary.doc2bow(text) for text in tokenized]

    best_k = start
    best_score = -1
    scores = []

    for k in range(start, limit + 1):
        lda = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=k,
            random_state=42,
            passes=10,
            alpha='auto'
        )

        cm = CoherenceModel(
            model=lda,
            texts=tokenized,
            dictionary=dictionary,
            coherence='c_v'
        )

        score = cm.get_coherence()
        scores.append((k, score))

        if score > best_score:
            best_score = score
            best_k = k

    return best_k, scores


def run_lda(texts, num_words=10):
    tokenized = [t.split() for t in texts if isinstance(t, str)]

    # 1️⃣ cari k terbaik
    best_k, coherence_scores = find_best_k(texts)

    # 2️⃣ LDA FINAL
    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=5, no_above=0.5)

    corpus = [dictionary.doc2bow(text) for text in tokenized]

    lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=best_k,
        random_state=42,
        passes=10,
        alpha='auto'
    )

    topics = []
    for i, topic in lda.print_topics(num_words=num_words):
        topics.append({
            "topic_id": i,
            "keywords": topic
        })

    wc = generate_wordcloud(texts)

    return {
        "best_k": best_k,
        "coherence_scores": coherence_scores,
        "topics": topics,
        "wordcloud": wc
    }


def run_lda_input(texts, num_words=10):
    # print("=== RUN LDA INPUT ===")
    # print("Total texts:", len(texts))

    tokenized = [
        t.split() for t in texts
        if isinstance(t, str) and len(t.split()) >= 2
    ]

    # print("Tokenized docs:", len(tokenized))

    if len(tokenized) < 5:
        return {
            "best_k": None,
            "coherence_scores": [],
            "topics": [],
            "wordcloud": None,
            "wordcloud_per_topic": {},  # 🔥 tambahan
            "message": "Data tidak cukup untuk topic modeling"
        }

    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=2, no_above=0.9)

    if len(dictionary) < 5:
        return {
            "best_k": None,
            "coherence_scores": [],
            "topics": [],
            "wordcloud": None,
            "wordcloud_per_topic": {}, #tamabhan
            "message": "Kosakata tidak cukup"
        }

    corpus = [dictionary.doc2bow(t) for t in tokenized]

    # ===== MENCARI BEST K =====
    coherence_scores = []
    best_k = 2
    best_score = -1

    max_k = min(4, len(dictionary))

    for k in range(2, max_k + 1):
        lda_tmp = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=k,
            random_state=42,
            passes=10
        )

        cm = CoherenceModel(
            model=lda_tmp,
            texts=tokenized,
            dictionary=dictionary,
            coherence="c_v"
        )

        score = cm.get_coherence()
        coherence_scores.append((k, score))

        if score > best_score:
            best_score = score
            best_k = k

    # print("Best K:", best_k)

    # ===== LDA FINAL =====
    lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=best_k,
        random_state=42,
        passes=8
    )

    topics = [
        {"topic_id": i, "keywords": topic}
        for i, topic in lda.print_topics(num_words=num_words)
    ]

      # ===== WORDCLOUD GLOBAL (TETAP ADA) =====
    wc_global = generate_wordcloud(texts)

    # ===== 🔥 WORDCLOUD PER TOPIC =====
    wordcloud_per_topic = {}

    for i in range(best_k):
        topic_words = lda.show_topic(i, topn=100)
        freq = {word: prob for word, prob in topic_words}

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white"
        ).generate_from_frequencies(freq)

        buffer = BytesIO()
        wc.to_image().save(buffer, format="PNG")
        buffer.seek(0)

        wordcloud_per_topic[i] = base64.b64encode(buffer.read()).decode()

    # ===== RETURN FINAL =====
    return {
        "best_k": best_k,
        "coherence_scores": coherence_scores,
        "topics": topics,
        "wordcloud": wc_global,
        "wordcloud_per_topic": wordcloud_per_topic
    }