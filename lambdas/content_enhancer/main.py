import json
import boto3
import os
import time
import hashlib
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

CACHE_TABLE = os.environ["CACHE_TABLE"]


def invoke_bedrock_with_retry(prompt, model_id="amazon.nova-lite-v1:0"):
    """Invoke Bedrock Nova Lite with exponential backoff retry. No fallback model."""
    bedrock_body = json.dumps(
        {
            "inferenceConfig": {"maxTokens": 600},
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
        }
    )

    delays = [1, 2, 4]
    last_exc = None
    for attempt, delay in enumerate(delays + [0]):
        try:
            logger.info(f"Invoking {model_id} (attempt {attempt + 1})")
            response = bedrock.invoke_model(
                body=bedrock_body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json",
            )
            res_body = json.loads(response.get("body").read())
            return res_body["output"]["message"]["content"][0]["text"]
        except Exception as e:
            logger.error(f"Bedrock attempt {attempt + 1} failed: {e}")
            last_exc = e
            if attempt == len(delays):
                raise last_exc
            time.sleep(delay)


def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        body = (
            json.loads(event.get("body", "{}"))
            if isinstance(event.get("body"), str)
            else event.get("body", {})
        )

        # Scope: News Summarization
        raw_trends = body.get("trends", [])
        if not raw_trends:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No trends provided to summarize"}),
            }

        trends_text = "\n".join(
            [f"- {t.get('topic', 'Unknown')}" for t in raw_trends[:10]]
        )

        prompt = f"""You are a YouTube trend analyst.
Analyze the following raw trending topics:
{trends_text}

Provide a concise summary with:
1. Key Insight: What is the overall theme?
2. Why it's trending: What triggered these topics?
3. Content Opportunity: How can a creator capitalize on this today?
"""

        input_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)

        try:
            cache_response = cache_table.get_item(Key={"input_hash": input_hash})
            if "Item" in cache_response:
                logger.info("Cache hit for summarization.")
                summary = cache_response["Item"]["response"]
            else:
                summary = invoke_bedrock_with_retry(prompt)
                cache_table.put_item(
                    Item={"input_hash": input_hash, "response": summary}
                )
        except Exception as e:
            logger.error("Cache/Bedrock error", exc_info=True)
            raise

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"summary": summary}),
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
