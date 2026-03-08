import json
import base64
import boto3
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
DATASET_BUCKET = os.environ["DATASET_BUCKET"]

def lambda_handler(event, context):
    logger.info("Processing Kinesis batch")
    records = []

    for record in event.get("Records", []):
        try:
            payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
            data = json.loads(payload)
            if "creator_id" in data and "content_id" in data:
                clean_record = {
                    "creator_id": data.get("creator_id"),
                    "content_id": data.get("content_id"),
                    "likes": int(data.get("likes", 0)),
                    "comments": int(data.get("comments", 0)),
                    "shares": int(data.get("shares", 0)),
                    "views": int(data.get("views", 100)),
                    "title": data.get("title", "Unknown"),
                    "topic": data.get("topic", "General"),
                    "platform": data.get("platform", "YouTube"),
                    "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
                }
                records.append(clean_record)
        except Exception as e:
            logger.error("Skipping malformed record", exc_info=True)

    if records:
        try:
            batch_id = context.aws_request_id
            s3.put_object(
                Bucket=DATASET_BUCKET,
                Key=f"feedback_ingest/batch-{batch_id}.json",
                Body=json.dumps(records),
                ContentType="application/json",
            )
            logger.info(f"Successfully wrote {len(records)} records to S3")
        except Exception as e:
            logger.error("Failed to write to S3", exc_info=True)
            raise e

    return {"statusCode": 200, "body": json.dumps({"message": "Processed Kinesis batch"})}
