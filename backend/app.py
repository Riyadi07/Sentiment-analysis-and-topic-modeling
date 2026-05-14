from flask import Flask
from flask_cors import CORS
from database.db import db
from config import SQLALCHEMY_DATABASE_URI

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # 🔥 PENTING: IMPORT MODEL DI SINI
    from database import models   # <--- INI WAJIB

    with app.app_context():
        db.create_all()

    from routes.dashboard import dashboard_bp
    from routes.preprocessing import preprocessing_bp
    from routes.labeling import labeling_bp
    from routes.sentiment import sentiment_bp
    from routes.topic import topic_bp
    from routes.input_analysis import input_analysis_bp
    from routes.scraping import scraping_bp
    from routes.topic_data import topic_data

    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(preprocessing_bp, url_prefix='/api/preprocessing')
    app.register_blueprint(labeling_bp, url_prefix='/api/labeling')
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(topic_bp, url_prefix='/api/topic')
    app.register_blueprint(input_analysis_bp, url_prefix='/api/input')
    app.register_blueprint(scraping_bp, url_prefix="/api/scraping")
    app.register_blueprint(topic_data, url_prefix='/api/topic_data')


    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
