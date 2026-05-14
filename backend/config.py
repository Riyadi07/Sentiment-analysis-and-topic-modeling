import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, 'data', 'base_data.csv')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

TFIDF_PATH = os.path.join(BASE_DIR, 'models', 'tfidf_vectorizer.pkl')
SVM_PATH = os.path.join(BASE_DIR, 'models', 'svm_model.pkl')
LE_PATH = os.path.join(BASE_DIR, 'models', 'label_encoder.pkl')

SQLALCHEMY_DATABASE_URI = 'sqlite:///analysis.db'
