import boto3
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add current dir to path for imports
sys.path.append(os.getcwd())
from lambdas.common.youtube_utils import YouTubeClient

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
PROJECT = "creator-intelligence"
ENV = "dev"
TABLE_NAME = f"{PROJECT}-{ENV}-CreatorContent"


def seed():
    print(f"🚀 Seeding Creator Content from YouTube Channel: {CHANNEL_ID}")

    yt_client = YouTubeClient(api_key=API_KEY)
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.getenv("Access_key"),
        aws_secret_access_key=os.getenv("Secret_access_key"),
        region_name="us-east-1",
    )

    table = dynamodb.Table(TABLE_NAME)

    try:
        videos = yt_client.fetch_creator_history(CHANNEL_ID)
        print(f"✅ Fetched {len(videos)} videos from YouTube API.")

        print(f"Writing to DynamoDB table: {TABLE_NAME}...")
        with table.batch_writer() as batch:
            for v in videos:
                # Prepare item for DynamoDB
                item = {
                    "creator_id": "techwithtim",
                    "content_id": v["video_id"],
                    "title": v["title"],
                    "timestamp": v["published_at"],
                    "topic": v["title"][:50],  # Mock topic extraction
                    "engagement_score": str(v["engagement_score"]),
                    "views": str(v["views"]),
                    "likes": str(v["likes"]),
                    "comments": str(v["comments"]),
                }
                batch.put_item(Item=item)

        print("✅ Live DynamoDB seeding completed successfully.")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")


if __name__ == "__main__":
    seed()
