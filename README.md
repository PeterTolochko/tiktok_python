# TikTok Data Fetcher

Two main functions, `fetch_tiktok_video_data` and `fetch_tiktok_comments_data`, which allow you to download video metadata and comments from TikTok using the official TikTok Research API.

## Features

- Fetch video metadata for a given TikTok account within a specified timeframe
- Fetch comments for a list of video IDs
- Save the fetched video metadata and comments data as CSV files
- Helper functions to retrieve video IDs from the fetched video data and convert the data to CSV format

## Prerequisites

Before using this project, make sure you have the following:

- Python 3.x installed
- Required Python packages installed (you can install them using `pip install -r requirements.txt`)
- Access to the TikTok Research API (you need to obtain API credentials)
- `key` and `secret` from TikTok API stored as environment variables

## Usage

1. Clone the repository or download the project files.

2. Install the required Python packages by running the following command:
   ```
   pip install -r requirements.txt
   ```

3. Update the `accounts` list in the code with the TikTok account usernames you want to fetch data for.

4. Modify the `timeframe` list to specify the start and end dates for each month you want to fetch data for. The dates should be in the format "YYYYMMDD".

5. Run the script to fetch the video metadata and comments data:
   ```python

    key = os.environ['tiktok_key']
    secret = os.environ['tiktok_secret']

    access_token = generate_access_token(key, secret)["access_token"]

    # create start and end dates for each month in 2023
    timeframe = [("20230101", "20230131"), ("20230201", "20230228")]
    accounts = ['nasa_0fficial', 'nytimes']

    for account in accounts:
        for start_date, end_date in timeframe:
            fetch_tiktok_video_data(account, start_date, end_date, mode="username")

    video_ids = get_video_ids('TikTok_Data/video_data')
    for video_id in video_ids:
        fetch_tiktok_comments_data(video_id)

    comments_data_to_csv('TikTok_Data/comments_data/')
    video_data_to_csv('TikTok_Data/video_data/')
   ```
6. The fetched video and comments metadata will be saved as JSON files in the `TikTok_Data/video_data/` and `TikTok_Data/comments_data/` directories, respectively.

7. You can convert the fetched data to CSV format using the helper functions `comments_data_to_csv` and `video_data_to_csv`.

## Functions

### `fetch_tiktok_video_data(account, start_date, end_date, mode="username")`

This function fetches video metadata for a given TikTok account within a specified timeframe.

- `account`: The TikTok account username or user ID.
- `start_date`: The start date of the timeframe in the format "YYYYMMDD".
- `end_date`: The end date of the timeframe in the format "YYYYMMDD".
- `mode`: The mode of the `account` parameter. It can be either "username" (default) or "hashtag_name", depending on whether you want to collect data for a specific account or hashtag.
- `filter_hashtags`: A list of hashtags to filter the fetched videos by (only when `mode` is "username"). The default is an empty list.
- `return_data`: A boolean value indicating whether to return the fetched data as a dictionary. The default is `False`.
- `n_videos`: The number of videos to fetch. The default is `None`, which does not introduce any restrictions on the count.


### `fetch_tiktok_comments_data(video_id)`

This function fetches comments data for a given TikTok video ID.

- `video_id`: The ID of the TikTok video.
- `return_data`: A boolean value indicating whether to return the fetched data as a dictionary. The default is `False`.

### Helper Functions

- `get_video_ids(directory)`: Retrieves the video IDs from the fetched JSON files in the specified directory.
- `comments_data_to_csv(directory)`: Converts the fetched comments data to CSV format and saves it in the specified directory.
- `video_data_to_csv(directory)`: Converts the fetched video metadata to CSV format and saves it in the specified directory.

## License

This project is licensed under the [MIT License](LICENSE).
