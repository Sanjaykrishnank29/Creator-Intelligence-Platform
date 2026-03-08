# -*- coding: utf-8 -*-
import boto3
import time
import os
from dotenv import load_dotenv

load_dotenv()
REGION = "us-east-1"

print("Triggering Trend Collector...")
l_client = boto3.client("lambda", region_name=REGION)
l_client.invoke(FunctionName="creator-intelligence-dev-trend_collector")

print("Waiting for new trends to be pulled into DynamoDB...")
time.sleep(3)

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table("creator-intelligence-dev-TrendSignals")
response = table.scan()

print("\n========= NEW SCHEMA DYNAMODB DATA (TrendSignals) =========")
for item in response.get("Items", []):
    topic = item.get("topic")
    print(
        f"- {topic[:50] if topic else 'None'}... \n  Timestamp: {item.get('timestamp')} \n  Score: {item.get('trend_score')}\n"
    )
print("===========================================================")
