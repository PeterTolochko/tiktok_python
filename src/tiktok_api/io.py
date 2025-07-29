import os
import json
import pandas as pd


def get_video_ids(video_data_path):
    """
    Extract video IDs from JSON files in a directory.
    """
    video_ids = []
    for file in os.listdir(video_data_path):
        if file.endswith(".json"):
            with open(os.path.join(video_data_path, file), "r") as f:
                try:
                    data = json.load(f)
                    video_ids.extend([video["id"] for video in data])
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
    return video_ids


def get_usernames(video_data_path):
    """
    Extract usernames from video JSON files.
    """
    usernames = []
    for file in os.listdir(video_data_path):
        if file.endswith(".json"):
            with open(os.path.join(video_data_path, file), "r") as f:
                try:
                    data = json.load(f)
                    usernames.extend([video["username"] for video in data])
                except Exception as e:
                    print(f"Error reading file {file}: {e}")
    return list(set(usernames))


def video_data_to_csv(video_data_path, output_file="TikTok_Data/video_data.csv"):
    """
    Combine all video data JSON files into one CSV.
    """
    dataframes = []
    for file in os.listdir(video_data_path):
        if file.endswith(".json"):
            try:
                df = pd.read_json(os.path.join(video_data_path, file))
                df["account"] = os.path.splitext(file)[0].split("_")[0]
                dataframes.append(df)
            except Exception as e:
                print(f"Error processing {file}: {e}")
    if dataframes:
        result = pd.concat(dataframes, ignore_index=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        result.to_csv(output_file, index=False)


def comments_data_to_csv(comments_data_path, output_file="TikTok_Data/comments_data.csv"):
    """
    Combine all comment data JSON files into one CSV.
    """
    dataframes = []
    for file in os.listdir(comments_data_path):
        if file.endswith(".json"):
            try:
                df = pd.read_json(os.path.join(comments_data_path, file))
                dataframes.append(df)
            except Exception as e:
                print(f"Error processing {file}: {e}")
    if dataframes:
        result = pd.concat(dataframes, ignore_index=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        result.to_csv(output_file, index=False)