from flask import Blueprint, request, jsonify, send_file
from database.db import db
from database.models import ScrapingInput, ScrapingReview
from services.playstore_scraper import scrape_playstore
import pandas as pd
import re
import os

scraping_bp = Blueprint("scraping", __name__)

def extract_app_id(url):
    match = re.search(r"id=([A-Za-z0-9._]+)", url)
    return match.group(1) if match else None


@scraping_bp.route("/playstore", methods=["POST"])
def scrape_playstore_route():
    data = request.json
    url = data.get("url")
    limit = int(data.get("limit", 200))

    app_id = extract_app_id(url)
    if not app_id:
        return jsonify({"error": "Link Play Store tidak valid"}), 400

    reviews = scrape_playstore(app_id, limit)

    parent = ScrapingInput(
        app_id=app_id,
        total_requested=limit,
        total_scraped=len(reviews)
    )
    db.session.add(parent)
    db.session.flush()

    for r in reviews:
        item = ScrapingReview(
            scraping_id=parent.id,
            review_id=r.get("reviewId"),
            user_name=r.get("userName"),
            user_image=r.get("userImage"),
            content=r.get("content"),
            score=r.get("score"),
            at=r.get("at"),
            app_version=r.get("appVersion")
        )
        db.session.add(item)

    db.session.commit()

    return jsonify({
        "scraping_id": parent.id,
        "app_id": app_id,
        "total_scraped": len(reviews)
    })


@scraping_bp.route("/download/<int:scraping_id>", methods=["GET"])
def download(scraping_id):
    filetype = request.args.get("type", "csv")

    rows = ScrapingReview.query.filter_by(scraping_id=scraping_id).all()

    df = pd.DataFrame([{
        "reviewId": r.review_id,
        "userName": r.user_name,
        "userImage": r.user_image,
        "content": r.content,
        "score": r.score,
        "at": r.at,
        "appVersion": r.app_version,
    } for r in rows])

    os.makedirs("uploads", exist_ok=True)

    if filetype == "xlsx":
        path = f"uploads/scraping_{scraping_id}.xlsx"
        df.to_excel(path, index=False)
    else:
        path = f"uploads/scraping_{scraping_id}.csv"
        df.to_csv(path, index=False)

    return send_file(path, as_attachment=True)

@scraping_bp.route("/preview/<int:scraping_id>", methods=["GET"])
def preview(scraping_id):
    rows = (
        ScrapingReview.query
        .filter_by(scraping_id=scraping_id)
        .limit(10)
        .all()
    )

    return jsonify([
        {
            "user_name": r.user_name,
            "content": r.content,
            "score": r.score,
            "at": r.at,
        }
        for r in rows
    ])
