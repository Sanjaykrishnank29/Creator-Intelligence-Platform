import os
import json
import urllib.request
import boto3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")
TABLE_NAME = os.environ.get("CONTENT_TABLE", "creator-intelligence-dev-CreatorContent")


def fetch_youtube_api_data(channel_id, api_key, days=30):
    base_url = "https://www.googleapis.com/youtube/v3"

    # 1. Get uploads playlist
    url1 = f"{base_url}/channels?part=contentDetails&id={channel_id}&key={api_key}"
    with urllib.request.urlopen(url1) as r:
        data = json.loads(r.read())

    if "items" not in data or not data["items"]:
        print("Channel not found in live YouTube.")
        return {}

    playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # 2. Get playlist items
    url2 = f"{base_url}/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={api_key}"
    with urllib.request.urlopen(url2) as r:
        data2 = json.loads(r.read())

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    video_ids = []
    for item in data2.get("items", []):
        pub_date = datetime.fromisoformat(
            item["snippet"]["publishedAt"].replace("Z", "+00:00")
        )
        if pub_date >= cutoff_date:
            video_ids.append(item["snippet"]["resourceId"]["videoId"])

    if not video_ids:
        print("No videos found in the last 30 days.")
        return {}

    # 3. Get video stats
    url3 = f"{base_url}/videos?part=snippet,statistics&id={','.join(video_ids)}&key={api_key}"
    with urllib.request.urlopen(url3) as r:
        data3 = json.loads(r.read())

    yt_data = {}
    for item in data3.get("items", []):
        yt_data[item["id"]] = {
            "title": item["snippet"]["title"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "publishedAt": item["snippet"]["publishedAt"],
        }

    return yt_data


def fetch_dynamodb_data(channel_id, table_name):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(table_name)

    from boto3.dynamodb.conditions import Key

    response = table.query(KeyConditionExpression=Key("creator_id").eq(channel_id))

    db_data = {}
    for item in response.get("Items", []):
        db_data[item["content_id"]] = {
            "title": item.get("title", ""),
            "views": int(item.get("views", 0)),
            "timestamp": item.get("timestamp", ""),
        }

    return db_data


def report():
    print(f"🔍 Testing YouTube Data Fetching for Channel: {CHANNEL_ID}")
    print("-" * 50)

    print("1. Fetching last 30 days of videos from official YouTube API...")
    yt_data = fetch_youtube_api_data(CHANNEL_ID, API_KEY, days=30)
    print(f"   -> Found {len(yt_data)} live videos on YouTube.")

    print(f"2. Fetching records from DynamoDB table ({TABLE_NAME})...")
    db_data = fetch_dynamodb_data(CHANNEL_ID, TABLE_NAME)
    print(f"   -> Found {len(db_data)} matching records in DB.")

    print("-" * 50)
    print("3. Comparing Data (Titles and Views)...")

    all_match = True
    discrepancies = []

    for vid, yt_info in yt_data.items():
        if vid not in db_data:
            discrepancies.append(
                f"❌ Video {vid} ('{yt_info['title']}') is MISSING from DynamoDB."
            )
            all_match = False
            continue

        db_info = db_data[vid]

        # We allow a small leniency on title in case strings get truncated or encoding differs
        title_match = yt_info["title"] == db_info["title"]
        views_match = yt_info["views"] == db_info["views"]

        if not title_match or not views_match:
            all_match = False
            error_msg = f"❌ Video {vid}:"
            if not title_match:
                error_msg += f"\n   - Title Mismatch: \n      YT: '{yt_info['title']}' \n      DB: '{db_info['title']}'"
            if not views_match:
                error_msg += f"\n   - View Mismatch: \n      YT: {yt_info['views']} views\n      DB: {db_info['views']} views"
            discrepancies.append(error_msg)

    result = {
        "yt_total": len(yt_data),
        "db_total": len(db_data),
        "discrepancies": discrepancies,
    }
    with open("discrepancies.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    report()
