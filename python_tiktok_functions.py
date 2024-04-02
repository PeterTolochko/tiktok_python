import requests
import os
import json
import pandas as pd

def generate_access_token(key, secret):
    """
    Generate an access token using the provided client key and secret.
    Args:
        key (str): The client key.
        secret (str): The client secret.
    Returns:
        dict: The response JSON containing the access token if successful, None otherwise.
    """
    url = 'https://open.tiktokapis.com/v2/oauth/token/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    data = {
        'client_key': key,
        'client_secret': secret,
        'grant_type': 'client_credentials',
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error generating access token: {e}")
        return None


def fetch_tiktok_video_data(entities, start_date, end_date, mode="username", filter_hashtags=[], return_data=False, n_videos=None):
    """
    Fetches video data from the TikTok API based on the provided parameters.

    Args:
        entities (list if hashtags or str if account name): Entities to retrieve from the API.
        start_date (str): Start date of the date range.
        end_date (str): End date of the date range.
        mode (str): Mode of the API request. Can be "username" or "hashtag_name".
        filter_hashtags (list): List of hashtags to filter the videos (optional).

    Returns:
        list: List of video data dictionaries.
    """

    print(f"Getting video data for {entities} from {start_date} to {end_date}")

    API_URL = 'https://open.tiktokapis.com/v2/research/video/query/?fields=id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    if mode == "username":
        if filter_hashtags:
            data = {
                "query": {
                    "and": [
                        {
                            "operation": "IN",
                            "field_name": "username",
                            "field_values": [entities]
                        },
                        {
                            "operation": "IN",
                            "field_name": "hashtag_name",
                            "field_values": filter_hashtags
                        }
                    ],
                },
                "max_count": 100,
                "cursor": 0,
                "start_date": start_date,
                "end_date": end_date
            }
        else:
            data = {
                "query": {
                    "and": [
                        {
                            "operation": "IN",
                            "field_name": "username",
                            "field_values": [entities]
                        }
                    ]
                },
                "max_count": 100,
                "cursor": 0,
                "start_date": start_date,
                "end_date": end_date
            }
    elif mode == "hashtag_name":
        data = {
            "query": {
                "and": [
                    {
                        "operation": "IN",
                        "field_name": "hashtag_name",
                        "field_values": entities
                    }
                ]
            },
            "max_count": 100,
            "cursor": 0,
            "start_date": start_date,
            "end_date": end_date
        }
    else:
        raise ValueError(f"Invalid mode: {mode}")

    all_video_data = []
    has_more = True
    cursor = 0
    search_id = ''

    videos_count = 0

    while has_more:
        data["cursor"] = cursor
        data["search_id"] = search_id

        response = requests.post(API_URL, headers=headers, json=data, allow_redirects=True)

        try:
            response_data = response.json()
            if response_data["data"]["videos"]:
                all_video_data.append(response_data["data"])
                has_more = response_data["data"].get("has_more", False)
                cursor = response_data["data"].get("cursor", 0)
                search_id = response_data["data"].get("search_id", '')
                print(f"Getting {len(response_data['data']['videos'])} videos")
                videos_count += len(response_data['data']['videos'])
                print(f"Total videos so far: {videos_count}")
            else:
                has_more = False

            if n_videos and videos_count >= n_videos:
                print(f"Got {n_videos} videos")
                break

        except Exception as e:
            print(f"Error fetching comments for {entities}: {e}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            # log the entities that caused the error
            with open('TikTok_Data/error_log_entities.txt', 'a') as f:
                f.write(f"{entities}\n")
            break

    if not all_video_data:
        print(f"No videos found for {entities} from {start_date} to {end_date}")
        return []

    # Collapse the list of videos into a single list
    all_video_data_out = [video for data in all_video_data for video in data['videos']]
    print(f"{len(all_video_data_out)} videos collected")

    # Write to file
    output_dir = 'TikTok_Data/video_data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{entities}_{start_date}_{end_date}_videos.json")
    with open(output_file, 'w') as file:
        json.dump(all_video_data_out, file)

    if return_data:
        return all_video_data_out


def fetch_tiktok_comments_data(video_id,  return_data=False):
    """
    Fetches comments data for a given video ID from the TikTok API.

    Args:
        video_id (str): The ID of the video to fetch comments for.
        max_comments (int): The maximum number of comments to fetch (default: 1000).

    Returns:
        list: List of comment data dictionaries.
    """
    print(f"Getting comments for {video_id}")

    API_URL =  'https://open.tiktokapis.com/v2/research/video/comment/list/?fields=id,video_id,text,like_count,reply_count,parent_comment_id,create_time,parent_comment_id'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "video_id": f"{video_id}",
        "max_count": 100,
    }

    all_comments_data = []
    has_more = True
    cursor = 0
    search_id = ''

    while has_more and cursor < 1000: # 1000 is the API limit
        data["cursor"] = cursor
        data["search_id"] = search_id

        response = requests.post(API_URL, headers=headers, json=data, allow_redirects=True)
        try:
            response_data = response.json()

            if response_data["data"]["comments"]:
                all_comments_data.append(response_data["data"])
                has_more = response_data["data"].get("has_more", False)
                cursor = response_data["data"].get("cursor", 0)
                search_id = response_data["data"].get("search_id", '')
            else:
                break
        except Exception as e:
            print(f"Error fetching comments for {video_id}: {e}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
                        # log the entities that caused the error
            with open('TikTok_Data/error_log_comments.txt', 'a') as f:
                f.write(f"{video_id}")
            break

    if not all_comments_data:
        print(f"No comments found for {video_id}")
        return []

    # Collapse the list of comments into a single list
    all_comments_data_out = [comment for data in all_comments_data for comment in data['comments']]
    print(f"Got {len(all_comments_data_out)} comments for {video_id}")

    # Write to file
    output_dir = 'TikTok_Data/comments_data'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{video_id}_comments.json")
    with open(output_file, 'w') as file:
        json.dump(all_comments_data_out, file)

    if return_data:
        return all_comments_data_out


def get_video_ids(video_data_file):
    """
    Retrieves video IDs from JSON files in the specified directory.
    Args:
        video_data_file (str): Path to the directory containing JSON files with video data.
    Returns:
        list: A list of video IDs extracted from the JSON files.
    """
    video_ids = []
    for file in os.listdir(video_data_file):
        # remove .DS_Store file 
        if file == '.DS_Store':
            continue
        file_path = os.path.join(video_data_file, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            video_ids.extend([video['id'] for video in data])
    return video_ids

# get twitter users from the video data
def get_users(data_path):
    """
    Retrieves usernames from JSON files in the specified directory.
    Args:
        video_data_file (str): Path to the directory containing JSON files with video data.
    Returns:
        list: A list of usernames extracted from the JSON files.
    """
    users = []
    for file in os.listdir(data_path):
        # remove .DS_Store file
        if file == ".DS_Store":
            continue
        with open(f"{data_path}/{file}", "r") as f:
            data = json.load(f)
            for video in data:
                users.append(video["username"])
    return list(users)



def video_data_to_csv(video_data_path):
    """
    Converts video data from JSON files to a CSV file.
    Args:
        video_data_path (str): Path to the directory containing JSON files with video data.
    Returns:
        None
    """
    video_data_list = []
    for file in os.listdir(video_data_path):
        # remove .DS_Store file
        if file == '.DS_Store':
            continue
        file_path = os.path.join(video_data_path, file)
        account_name = os.path.splitext(os.path.basename(file))[0].split("_")[0]
        current_data = pd.read_json(file_path)
        current_data['account'] = account_name
        video_data_list.append(current_data)
    video_data = pd.concat(video_data_list, ignore_index=True)
    output_path = os.path.join('TikTok_Data', 'video_data.csv')
    video_data.to_csv(output_path, index=False)


def comments_data_to_csv(comments_data_path):
    """
    Converts comments data from JSON files to a CSV file.
    Args:
        comments_data_path (str): Path to the directory containing JSON files with comments data.
    Returns:
        None
    """
    comments_data_list = []
    for file in os.listdir(comments_data_path):
        # remove .DS_Store file
        if file == '.DS_Store':
            continue
        file_path = os.path.join(comments_data_path, file)
        current_data = pd.read_json(file_path)
        comments_data_list.append(current_data)
    comments_data = pd.concat(comments_data_list, ignore_index=True)
    output_path = os.path.join('TikTok_Data', 'comments_data.csv')
    comments_data.to_csv(output_path, index=False)