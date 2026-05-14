from database.db import db
from datetime import datetime

class AnalysisInput(db.Model):
    __tablename__ = "analysis_input"

    id = db.Column(db.Integer, primary_key=True)
    input_type = db.Column(db.String(20), nullable=False)   # text / file
    source = db.Column(db.String(255), nullable=False)      # manual / filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "AnalysisItem",
        backref="input",
        cascade="all, delete",
        lazy=True
    )


class AnalysisItem(db.Model):
    __tablename__ = "analysis_item"

    id = db.Column(db.Integer, primary_key=True)
    input_id = db.Column(
        db.Integer,
        db.ForeignKey("analysis_input.id"),
        nullable=False
    )

    original_text = db.Column(db.Text, nullable=False)
    processed_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScrapingInput(db.Model):
    __tablename__ = "scraping_input"

    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.String(150), nullable=False)
    app_name = db.Column(db.String(255))
    total_requested = db.Column(db.Integer)
    total_scraped = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship(
        "ScrapingReview",
        backref="scraping",
        cascade="all, delete",
        lazy=True
    )

class ScrapingReview(db.Model):
    __tablename__ = "scraping_review"

    id = db.Column(db.Integer, primary_key=True)
    scraping_id = db.Column(
        db.Integer,
        db.ForeignKey("scraping_input.id"),
        nullable=False
    )

    review_id = db.Column(db.String(100))
    user_name = db.Column(db.String(200))
    user_image = db.Column(db.Text)
    content = db.Column(db.Text)
    score = db.Column(db.Integer)
    at = db.Column(db.DateTime)
    app_version = db.Column(db.String(50))
