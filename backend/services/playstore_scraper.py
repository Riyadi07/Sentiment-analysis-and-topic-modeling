from google_play_scraper import reviews, Sort
import time

def scrape_playstore(app_id, limit=200):
    all_reviews = []
    continuation_token = None

    while len(all_reviews) < limit:
        remaining = limit - len(all_reviews)

        result, continuation_token = reviews(
            app_id,
            lang="id",
            country="id",
            sort=Sort.NEWEST,
            count=min(200, remaining),
            continuation_token=continuation_token
        )

        if not result:
            break

        all_reviews.extend(result)

        if continuation_token is None:
            break

        time.sleep(3)

    return all_reviews[:limit]
