import json
import os
import boto3
import urllib.request
import urllib.parse
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

RAW_TRENDS_BUCKET = os.environ.get("RAW_TRENDS_BUCKET")
TRENDS_TABLE = os.environ["TRENDS_TABLE"]

def fetch_creator_trends():
    api_key = os.environ["NEWS_API_KEY"]
    keywords = ["youtube creator", "tiktok creator", "creator economy", "instagram influencer"]
    trends = []

    for keyword in keywords:
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://newsapi.org/v2/everything?q={encoded_keyword}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
                for article in data.get("articles", []):
                    trends.append({"source": "NewsAPI", "topic": article["title"], "trend_score": 0.9, "sentiment": "news"})
        except Exception as e:
            logger.error(f"Error fetching keyword {keyword}", exc_info=True)
            raise # SRE: Raise failures instead of masking
    return trends[:20]

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        trends = fetch_creator_trends()
        timestamp = datetime.utcnow().isoformat()
        table = dynamodb.Table(TRENDS_TABLE)
        
        for trend in trends:
            table.put_item(
                Item={
                    "topic": trend["topic"],
                    "timestamp": timestamp,
                    "source": trend["source"],
                    "trend_score": str(trend["trend_score"]),
                    "sentiment": trend["sentiment"],
                    "last_updated": timestamp,
                }
            )

        if RAW_TRENDS_BUCKET:
            payload = {"timestamp": timestamp, "data": trends}
            s3.put_object(Bucket=RAW_TRENDS_BUCKET, Key=f"trends/{timestamp}-trends.json", Body=json.dumps(payload), ContentType="application/json")

        return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"message": "Successfully updated TrendSignals and S3"})}
    except Exception as e:
        logger.error("Service invocation failed", exc_info=True)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": "Internal server error"})}
