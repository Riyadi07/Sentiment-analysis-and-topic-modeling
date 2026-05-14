import re
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# ===== LOAD SLANG DICTIONARY (SEKALI) =====
with open("combined_slang_words.txt", "r", encoding="utf-8") as f:
    slang_dict = json.loads(f.read())

# ===== INIT =====
stop_words = set(stopwords.words("indonesian"))
stop_words.discard("tidak")
stop_words.discard("baik")
stop_words.discard("bagus")
stop_words.add("nya")
stop_words.add("l")

stemmer = StemmerFactory().create_stemmer()

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # Case folding
    text = text.lower()

    # Cleaning (SESUAI COLAB)
    text = re.sub(r'([A-Za-z])([!?.,]+)([A-Za-z])', r'\1 \2 \3', text)
    text = re.sub(r"http\S+|@\w+|#\w+", " ", text)
    text = re.sub(r'[0-9]+', ' ', text)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Normalisasi slang
    words = text.split()
    words = [slang_dict.get(w, w) for w in words]

    # Tokenizing
    tokens = word_tokenize(" ".join(words))

    # Stopword removal
    tokens = [t for t in tokens if t not in stop_words]

    # Stemming
    tokens = [stemmer.stem(t) for t in tokens]

    return " ".join(tokens)
