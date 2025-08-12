import logging
import requests
from datetime import datetime

class SwarmConnector:
    def __init__(self, host: str, user: str, token: str):
        self.host = host
        self.user = user
        self.token = token
        if host.startswith(('http://', 'https://')):
            self.api_url = f"{host}/api/v9"
        else:
            self.api_url = f"https://{host}/api/v9"

    def collect_reviews(self, max_count=100) -> list[dict]:
        reviews_data = []
        if not self.host:
            logging.warning("Swarm host not provided. Skipping Swarm review collection.")
            return reviews_data

        try:
            last_seen = None
            while len(reviews_data) < max_count:
                params = {'max': min(100, max_count - len(reviews_data))}
                if last_seen:
                    params['after'] = last_seen

                # In a real scenario, you'd want to handle SSL verification properly.
                # Using verify=False is not recommended for production environments.
                response = requests.get(
                    f"{self.api_url}/reviews",
                    params=params,
                    auth=(self.user, self.token),
                    verify=False
                )
                response.raise_for_status()
                data = response.json()

                if not data.get('reviews'):
                    break

                for review in data.get('reviews', []):
                    created_date = datetime.fromtimestamp(review['created']) if 'created' in review else None

                    merged_date = None
                    if review.get('state') == 'committed' and 'updated' in review:
                        merged_date = datetime.fromtimestamp(review['updated'])

                    time_to_merge = None
                    if created_date and merged_date:
                        time_to_merge = (merged_date - created_date).total_seconds() / 60

                    reviews_data.append({
                        "id": f"swarm-{review['id']}",
                        "repo_name": ", ".join(review.get('projects', [])),
                        "pr_number": review['id'],
                        "title": review.get('description', '').split('\n')[0],
                        "author": review.get('author', ''),
                        "created_date": created_date,
                        "merged_date": merged_date,
                        "first_comment_date": None,
                        "time_to_first_review_minutes": None,
                        "time_to_merge_minutes": int(time_to_merge) if time_to_merge else None,
                        "comment_count": review.get('comments', {}).get('total', 0)
                    })

                if data.get('lastSeen') is None or len(reviews_data) >= max_count:
                    break
                last_seen = data['lastSeen']

            logging.info(f"Collected {len(reviews_data)} reviews from Swarm.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to collect Swarm reviews: {e}")

        return reviews_data
