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
    Adds a 'video_url' column for direct TikTok access.
    """
    import os
    import pandas as pd
    import json

    dataframes = []
    for file in os.listdir(video_data_path):
        if file.endswith(".json"):
            file_path = os.path.join(video_data_path, file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                df = pd.DataFrame(data)

                # Add account from filename
                df["account"] = os.path.splitext(file)[0].split("_")[0]

                if "id" in df.columns:
                    df["id"] = df["id"].astype(str)
                # Add video URL if username and id exist
                if "username" in df.columns and "id" in df.columns:
                    df["video_url"] = (
                        "https://www.tiktok.com/@" + df["username"] + "/video/" + df["id"]
                    )

                dataframes.append(df)
            except Exception as e:
                print(f"Error processing {file}: {e}")

    if dataframes:
        result = pd.concat(dataframes, ignore_index=True)
        result["create_datetime"] = pd.to_datetime(result["create_time"], unit="s", utc=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        result.to_csv(output_file, index=False)
        print(f"Video CSV saved to {output_file} with {len(result)} rows and video_url column.")
    else:
        print("No video JSON files found.")


def comments_data_to_csv(
    comments_data_path,
    video_data_path,
    output_file="TikTok_Data/comments_data.csv"
):
    """
    Combine all comment data JSON files into one CSV.
    Joins with video metadata to add 'username' and full 'video_url'.
    """
    import os
    import pandas as pd
    import json

    #  Load video metadata
    video_dataframes = []
    for file in os.listdir(video_data_path):
        if file.endswith(".json"):
            file_path = os.path.join(video_data_path, file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                df_videos = pd.DataFrame(data)
                if "id" in df_videos.columns:
                    df_videos["id"] = df_videos["id"].astype(str)
                video_dataframes.append(df_videos[["id", "username"]])
            except Exception as e:
                print(f"Error processing video file {file}: {e}")

    if not video_dataframes:
        print("No video JSON files found. Cannot join usernames.")
        return

    video_df = pd.concat(video_dataframes, ignore_index=True).drop_duplicates("id")
    video_df.rename(columns={"id": "video_id"}, inplace=True)

    # Load comment JSONs

    comment_dataframes = []
    for file in os.listdir(comments_data_path):
        if file.endswith(".json"):
            file_path = os.path.join(comments_data_path, file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                df_comments = pd.DataFrame(data)

                # Extract video_id from filename
                video_id = os.path.splitext(file)[0].split("_")[0]
                df_comments["video_id"] = str(video_id)

                comment_dataframes.append(df_comments)
            except Exception as e:
                print(f"Error processing comment file {file}: {e}")

    if not comment_dataframes:
        print("No comment JSON files found.")
        return

    comments_df = pd.concat(comment_dataframes, ignore_index=True)

    # Merge with video metadata to get username
    merged_df = comments_df.merge(video_df, on="video_id", how="left")


    merged_df["video_url"] = (
        "https://www.tiktok.com/@" + merged_df["username"].astype(str) + "/video/" + merged_df["video_id"]
    )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    merged_df.to_csv(output_file, index=False)
    print(f"Comments CSV saved to {output_file} with {len(merged_df)} rows and video_url column.")