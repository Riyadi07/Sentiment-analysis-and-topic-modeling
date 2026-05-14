import joblib
from config import TFIDF_PATH, SVM_PATH, LE_PATH

tfidf = joblib.load(TFIDF_PATH)
svm = joblib.load(SVM_PATH)
le = joblib.load(LE_PATH)

def predict_sentiment(texts):
    X = tfidf.transform(texts)
    preds = svm.predict(X)
    return le.inverse_transform(preds)
