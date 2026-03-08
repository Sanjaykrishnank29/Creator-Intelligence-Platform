import json
import os
import boto3
import logging
import urllib.request
from datetime import datetime
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

CONTENT_TABLE = os.environ["CONTENT_TABLE"]
DATASET_BUCKET = os.environ.get("DATASET_BUCKET")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")
table = dynamodb.Table(CONTENT_TABLE)


def fetch_youtube_videos(channel_id):
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY not set")
        return []

    base_url = "https://www.googleapis.com/youtube/v3"
    try:
        url1 = f"{base_url}/channels?part=contentDetails&id={channel_id}&key={YOUTUBE_API_KEY}"
        with urllib.request.urlopen(url1) as r:
            data = json.loads(r.read())

        if "items" not in data or not data["items"]:
            return []

        playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        url2 = f"{base_url}/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
        with urllib.request.urlopen(url2) as r:
            data2 = json.loads(r.read())

        video_ids = [
            item["snippet"]["resourceId"]["videoId"] for item in data2.get("items", [])
        ]
        if not video_ids:
            return []

        url3 = f"{base_url}/videos?part=snippet,statistics&id={','.join(video_ids)}&key={YOUTUBE_API_KEY}"
        with urllib.request.urlopen(url3) as r:
            data3 = json.loads(r.read())

        results = []
        for item in data3.get("items", []):
            snippet = item["snippet"]
            stats = item["statistics"]

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            timestamp = snippet["publishedAt"]

            results.append(
                {
                    "creator_id": channel_id,
                    "content_id": item["id"],
                    "timestamp": timestamp,
                    "platform": "YouTube",
                    "topic": snippet["title"][:50],
                    "title": snippet["title"],
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": 0,
                }
            )

        return results
    except Exception as e:
        logger.error(f"Error fetching YouTube data: {e}", exc_info=True)
        return []


def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        method = event.get("httpMethod", "POST")

        if method == "GET":
            qs = event.get("queryStringParameters") or {}
            creator_id = qs.get("creator_id") or YOUTUBE_CHANNEL_ID
            sync = qs.get("sync") == "true"

            if sync and creator_id and YOUTUBE_API_KEY:
                logger.info(f"Syncing live YouTube data for {creator_id}...")
                videos = fetch_youtube_videos(creator_id)
                if videos:
                    logger.info(
                        f"Fetched {len(videos)} videos. Upserting to {CONTENT_TABLE}..."
                    )
                    for v in videos:
                        table.put_item(Item=v)

            if creator_id:
                response = table.query(
                    KeyConditionExpression=Key("creator_id").eq(creator_id), Limit=30
                )
            else:
                response = table.scan(Limit=30)

            items = response.get("Items", [])
            clean_items = []
            for item in items:
                clean_item = {
                    k: (int(v) if hasattr(v, "to_integral_value") else v)
                    for k, v in item.items()
                }
                clean_items.append(clean_item)

            clean_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(clean_items),
            }

        # (Existing POST logic)
        body = json.loads(event.get("body", "{}"))
        creator_id = body.get("creator_id")
        content_id = body.get("content_id")

        if not creator_id or not content_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Missing ID"}),
            }

        timestamp = datetime.utcnow().isoformat()
        item = {
            "creator_id": creator_id,
            "content_id": content_id,
            "timestamp": timestamp,
            "platform": body.get("platform", "unknown"),
            "topic": body.get("topic", "general"),
            "content_type": body.get("content_type", "video"),
            "title": body.get("title", ""),
            "likes": int(body.get("likes", 0)),
            "comments": int(body.get("comments", 0)),
            "shares": int(body.get("shares", 0)),
            "views": int(body.get("views", 0)),
        }
        table.put_item(Item=item)

        if DATASET_BUCKET:
            s3_key = f"content_ingest/{creator_id}/{content_id}-{timestamp}.json"
            s3.put_object(
                Bucket=DATASET_BUCKET,
                Key=s3_key,
                Body=json.dumps(item),
                ContentType="application/json",
            )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"message": "Content ingested successfully"}),
        }

    except Exception as e:
        logger.error("Service invocation failed", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": "Internal server error"}),
        }
