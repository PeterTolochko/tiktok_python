# TikTok API Client

A Python package for collecting video and comment data from the **TikTok Research API**.  
---

## Features

- Fetch video metadata for TikTok accounts or hashtags
- Fetch comments for TikTok videos
- Automatically handles:
  - Token authentication and refresh
  - API rate limiting and retry logic
  - Paginated responses
- Save fetched data to JSON (with optional CSV export)
- Includes helper utilities for:
  - Extracting video IDs
  - Converting JSON to CSV
  - Getting unique usernames from video data


## Installation

```bash
git clone https://github.com/PeterTolochko/tiktok_python.git
cd tiktok-api-client
pip install -e .
```



## Prerequisites

Before using this project, make sure you have the following:

- Python 3.8+
- Access to the TikTok Research API (you need to obtain API credentials)
- `key` and `secret` from TikTok API stored as environment variables

```bash
export TIKTOK_KEY="your_key"
export TIKTOK_SECRET="your_secret"
```

## Usage


```python

from tiktok_api import TikTokAPIClient
from tiktok_api.io import get_video_ids, video_data_to_csv, comments_data_to_csv
import os

# Authenticate
client = TikTokAPIClient(
    client_key=os.environ["tiktok_key"],
    client_secret=os.environ["tiktok_secret"]
)

# Define date range
start_date = "20230101"
end_date = "20230131"

# Fetch video data
client.fetch_video_data("nytimes", start_date, end_date, mode="username")

# Convert video JSONs to CSV
video_data_to_csv("TikTok_Data/video_data")

# Fetch comments for each video
video_ids = get_video_ids("TikTok_Data/video_data")
for vid in video_ids:
    client.fetch_comments_data(vid)

# Convert comments JSONs to CSV
comments_data_to_csv("TikTok_Data/comments_data")

```



## Main Class

### `TikTokAPIClient`

#### `fetch_video_data(entities, start_date, end_date, mode='username', ...)`

Fetch video metadata for a user or hashtag.

| Argument         | Description                                               |
|------------------|-----------------------------------------------------------|
| `entities`       | Username (str) or list of hashtags (if mode = "hashtag")  |
| `start_date`     | Start date in `"YYYYMMDD"` format                         |
| `end_date`       | End date in `"YYYYMMDD"` format                           |
| `mode`           | `"username"` (default) or `"hashtag_name"`                |
| `filter_hashtags`| List of hashtags to filter (optional)                     |
| `return_data`    | If `True`, return list of dicts                           |
| `n_videos`       | Max number of videos to fetch                             |

---

#### `fetch_comments_data(video_id, return_data=False)`

Fetch all comments for a given video ID.

| Argument       | Description                                  |
|----------------|----------------------------------------------|
| `video_id`     | TikTok video ID (str)                        |
| `return_data`  | If `True`, returns comments as list of dicts |


## Utilities

### `tiktok_api.io` Module

Helper functions for working with your saved video and comment data.

#### `get_video_ids(directory)`

Extracts all video IDs from `.json` files in the specified directory.

| Argument     | Description                                  |
|--------------|----------------------------------------------|
| `directory`  | Path to folder with video JSON files         |
| **Returns**  | List of video IDs (`List[str]`)              |

---

#### `get_usernames(directory)`

Extracts usernames from video metadata JSON files.

| Argument     | Description                                   |
|--------------|-----------------------------------------------|
| `directory`  | Path to folder with video JSON files          |
| **Returns**  | List of usernames (`List[str]`)               |

---

#### `video_data_to_csv(directory, output_file='...')`

Converts video metadata JSON files to a single CSV.

| Argument       | Description                                 |
|----------------|---------------------------------------------|
| `directory`     | Path to folder with video JSON files       |
| `output_file`   | Optional path to save CSV (default auto)   |
| **Effect**      | Saves concatenated CSV to `output_file`    |

---

#### `comments_data_to_csv(directory, output_file='...')`

Converts comment JSON files to a single CSV.

| Argument       | Description                                 |
|----------------|---------------------------------------------|
| `directory`     | Path to folder with comment JSON files     |
| `output_file`   | Optional path to save CSV (default auto)   |
| **Effect**      | Saves concatenated CSV to `output_file`    |




## Contributing

Contributions are welcome! Please feel free to submit a pull request.


## Citation

If you find this project useful, please cite:

> **Petro Tolochko** (2024). *TikTok API Client: A Python package for fetching TikTok video and comment metadata*. GitHub. https://github.com/PeterTolochko/tiktok_python

BibTeX:
```bibtex
@misc{tiktokapiclient,
  author       = {Petro Tolochko},
  title        = {TikTok API Client: A Python package for fetching TikTok video and comment metadata},
  year         = {2024},
  howpublished = {\url{https://github.com/PeterTolochko/tiktok_python}},
  note         = {Version 0.1.0}
}
```


## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
