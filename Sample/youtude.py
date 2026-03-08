import requests
import pandas as pd
from datetime import datetime

# ==========================
# 🔑 CONFIGURATION
# ==========================

API_KEY = "AIzaSyDuSci6CmiBpLnFdcv2MjpPHgkdKZAjeHg"
CHANNEL_ID = "UC4JX40jDee_tINbkjycV4Sg"

# ==========================
# STEP 1: Get Upload Playlist ID
# ==========================

channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={CHANNEL_ID}&key={API_KEY}"
channel_data = requests.get(channel_url).json()

uploads_playlist = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# ==========================
# STEP 2: Get Last 30 Video IDs
# ==========================

playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist}&maxResults=30&key={API_KEY}"
playlist_data = requests.get(playlist_url).json()

video_ids = [
    item["snippet"]["resourceId"]["videoId"]
    for item in playlist_data["items"]
]

# ==========================
# STEP 3: Get Video Details & Statistics
# ==========================

video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(video_ids)}&key={API_KEY}"
video_data = requests.get(video_url).json()

data = []

for item in video_data["items"]:
    snippet = item["snippet"]
    stats = item["statistics"]

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))

    # Basic preprocessing
    title_length = len(snippet["title"])
    publish_time = datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
    publish_hour = publish_time.hour

    # Engagement score formula
    engagement_score = (
        (likes * 0.5) +
        (comments * 0.3) +
        (views * 0.2)
    )

    data.append({
        "video_id": item["id"],
        "title": snippet["title"],
        "published_date": publish_time.date(),
        "published_hour": publish_hour,
        "title_length": title_length,
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagement_score": round(engagement_score, 2)
    })

# ==========================
# STEP 4: Save to CSV
# ==========================

df = pd.DataFrame(data)

# Normalize engagement score (optional improvement)
df["normalized_engagement"] = (
    (df["engagement_score"] - df["engagement_score"].min()) /
    (df["engagement_score"].max() - df["engagement_score"].min())
)

df.to_csv("last_30_videos_processed.csv", index=False)

print("✅ Data saved to last_30_videos_processed.csv")