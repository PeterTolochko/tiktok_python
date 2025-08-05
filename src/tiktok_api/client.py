import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Union

# Setup default logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TikTokAPIClient:
    BASE_VIDEO_URL = "https://open.tiktokapis.com/v2/research/video/query/"
    BASE_COMMENT_URL = "https://open.tiktokapis.com/v2/research/video/comment/list/"
    VIDEO_FIELDS = "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"
    COMMENT_FIELDS = "id,video_id,text,like_count,reply_count,parent_comment_id,create_time"

    def __init__(self, client_key: str, client_secret: str):
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None
        self._refresh_token()

    def _refresh_token(self):
        logger.info("Refreshing TikTok API token...")
        url = 'https://open.tiktokapis.com/v2/oauth/token/'
        data = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            json_data = response.json()
            self.access_token = json_data['access_token']
            self.token_expiry = datetime.now() + timedelta(hours=1)
            logger.info("Token successfully refreshed.")
        except requests.RequestException as e:
            logger.error(f"Failed to get access token: {e}")
            raise RuntimeError("Could not authenticate with TikTok API.")

    def _ensure_token_valid(self):
        if not self.access_token or datetime.now() >= self.token_expiry:
            self._refresh_token()

    def _request_with_retries(self, url, headers, json_data, retries=10):
        for attempt in range(retries):
            try:
                response = requests.post(url, headers=headers, json=json_data)
                if response.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited (429). Retrying in {wait} seconds...")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                wait = 2 ** attempt
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}. Retrying in {wait} seconds...")
                time.sleep(wait)

        logger.error("Max retries exceeded.")
        raise RuntimeError("Request failed after multiple retries.")

    def _fetch_paginated_data(self, url, query, fields, result_key, output_path=None, n_limit=None):
        self._ensure_token_valid()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        all_data = []
        has_more = True
        total = 0

        while has_more:
            response = self._request_with_retries(f"{url}?fields={fields}", headers, query)
            try:
                data = response.json()

                if "data" not in data or result_key not in data["data"]:
                    logger.warning(f"Unexpected {result_key} response: {data}")
                    break

                items = data["data"].get(result_key, [])
                all_data.extend(items)
                total += len(items)
                logger.info(f"Fetched {total} {result_key}")

                has_more = data["data"].get("has_more", False)
                query["cursor"] = data["data"].get("cursor", 0)
                query["search_id"] = data["data"].get("search_id", '')

                if n_limit and total >= n_limit:
                    break

            except Exception as e:
                logger.error(f"Error parsing {result_key} response: {e}")
                break

        if not all_data:
            logger.warning(f"No {result_key} retrieved.")
            return []

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(all_data, f)
            logger.info(f"Saved {total} {result_key} to {output_path}")

        return all_data

    def fetch_video_data(self,
                         entities: Union[str, List[str]],
                         start_date: str,
                         end_date: str,
                         mode: str = "username",
                         filter_hashtags: List[str] = [],
                         regions: List[str] = None,
                         output_dir: str = "TikTok_Data/video_data",
                         return_data: bool = False,
                         n_videos: int = None):
        """
        Fetch TikTok videos for a username or hashtag.
        """
        query = {
            "query": {"and": []},
            "max_count": 100,
            "cursor": 0,
            "start_date": start_date,
            "end_date": end_date,
            "search_id": ''
        }

        if mode == "username":
            query["query"]["and"].append({
                "operation": "IN", "field_name": "username", "field_values": [entities]
            })
            if filter_hashtags:
                query["query"]["and"].append({
                    "operation": "IN", "field_name": "hashtag_name", "field_values": filter_hashtags
                })
        elif mode == "hashtag_name":
            query["query"]["and"].append({
                "operation": "IN", "field_name": "hashtag_name", "field_values": entities
            })

        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        if regions:
            query["query"]["and"].append({
                "operation": "IN", "field_name": "region_code", "field_values": regions
            })

        safe_name = str(entities).replace("/", "_").replace(" ", "_")
        filename = f"{safe_name}_{start_date}_{end_date}_videos.json"
        output_path = os.path.join(output_dir, filename)

        results = self._fetch_paginated_data(
            url=self.BASE_VIDEO_URL,
            query=query,
            fields=self.VIDEO_FIELDS,
            result_key="videos",
            output_path=output_path,
            n_limit=n_videos
        )

        return results if return_data else None

    def fetch_comments_data(self,
                            video_id: str,
                            output_dir: str = "TikTok_Data/comments_data",
                            return_data: bool = False):
        """
        Fetch comments for a specific video ID.
        """
        query = {
            "video_id": video_id,
            "max_count": 100,
            "cursor": 0,
            "search_id": ''
        }

        filename = f"{video_id}_comments.json"
        output_path = os.path.join(output_dir, filename)

        results = self._fetch_paginated_data(
            url=self.BASE_COMMENT_URL,
            query=query,
            fields=self.COMMENT_FIELDS,
            result_key="comments",
            output_path=output_path
        )

        return results if return_data else None