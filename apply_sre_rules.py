import os
import boto3
import json
import time

lambdas_dir = "lambdas"

idea_gen_code = """import json
import boto3
import os
import time
import hashlib
import logging
import math
from boto3.dynamodb.conditions import Key

# Use print for immediate CloudWatch capture
def log_info(msg):
    print(f"[INFO] {msg}")
def log_error(msg, exc=None):
    print(f"[ERROR] {msg}")
    if exc: print(f"Exception: {exc}")

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

TRENDS_TABLE = os.environ["TRENDS_TABLE"]
CONTENT_TABLE = os.environ["CONTENT_TABLE"]
CACHE_TABLE = os.environ["CACHE_TABLE"]

def get_embedding(text):
    body = json.dumps({"inputText": text})
    response = bedrock.invoke_model(
        body=body,
        modelId="amazon.titan-embed-text-v1",
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
    return response_body.get("embedding")

def cosine_similarity(v1, v2):
    dot_product = sum(x * y for x, y in zip(v1, v2))
    magnitude = math.sqrt(sum(x * x for x in v1)) * math.sqrt(sum(y * y for y in v2))
    return dot_product / magnitude if magnitude > 0 else 0

def invoke_bedrock_with_retry(prompt, model_id="amazon.nova-lite-v1:0"):
    # Nova format
    bedrock_body = json.dumps({
        "inferenceConfig": {"maxTokens": 1500},
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
    })
    
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays + [0]):
        try:
            log_info(f"Invoking bedrock model {model_id} (Attempt {attempt+1})")
            response = bedrock.invoke_model(
                body=bedrock_body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json",
            )
            res_body = json.loads(response.get("body").read())
            return res_body["output"]["message"]["content"][0]["text"]
        except Exception as e:
            log_error(f"Bedrock invocation failed for {model_id}", e)
            if attempt == len(delays):
                raise
            time.sleep(delay)

def lambda_handler(event, context):
    try:
        log_info(f"Event: {json.dumps(event)}")
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
        
        creator_id = body.get("creator_id", "techwithtim")
        niche = body.get("niche") or body.get("topic", "General Tech")
        platform = body.get("platform", "YouTube")

        trends_table = dynamodb.Table(TRENDS_TABLE)
        trends_data = trends_table.scan(Limit=10).get("Items", [])
        trends = [item.get("topic") for item in trends_data if item.get("topic")]

        content_table = dynamodb.Table(CONTENT_TABLE)
        history_data = content_table.query(
            KeyConditionExpression=Key("creator_id").eq(creator_id), 
            Limit=10
        ).get("Items", [])
        history_titles = [item.get("title") for item in history_data if item.get("title")]

        if not trends or not history_titles:
            prompt = f"You are an elite YouTube strategist. Generate 5 viral video ideas for the niche: {niche} on {platform}."
        else:
            log_info(f"Found {len(trends)} trends and {len(history_titles)} past videos. Matching...")
            trend_embeddings = {t: get_embedding(t) for t in trends[:5]}
            history_embeddings = {h: get_embedding(h) for h in history_titles[:5]}

            matched_pairs = []
            for t_text, t_emb in trend_embeddings.items():
                for h_text, h_emb in history_embeddings.items():
                    score = cosine_similarity(t_emb, h_emb)
                    matched_pairs.append({"trend": t_text, "past_video": h_text, "score": score})

            matched_pairs.sort(key=lambda x: x["score"], reverse=True)
            top_pairs = matched_pairs[:3]
            log_info(f"Top matches identified.")

            context_str = "\\n".join([f"- Trend: {p['trend']} (Related: {p['past_video']})" for p in top_pairs])
            prompt = f\"\"\"You are an elite YouTube strategist.
Match the following trends against past creator content:
{context_str}

Platform: {platform}
TASK: Generate 5 viral video ideas. Return ONLY a JSON array of objects with keys 'title', 'explanation', 'performance_reasoning', 'trend_source', 'related_video'.\"\"\"

        input_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)
        
        try:
            cache_res = cache_table.get_item(Key={"input_hash": input_hash})
            if "Item" in cache_res:
                log_info("Cache hit.")
                content = cache_res["Item"]["response"]
            else:
                content = invoke_bedrock_with_retry(prompt)
                cache_table.put_item(Item={"input_hash": input_hash, "response": content})
        except Exception as e:
            log_error("Cache/AI failure", e)
            raise

        json_str = content.strip()
        if "```json" in json_str: json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str: json_str = json_str.split("```")[1].split("```")[0].strip()
        
        try:
            ideas = json.loads(json_str)
        except:
            ideas = [{"title": "Content Idea", "explanation": content[:200]}]

        return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"ideas": ideas, "content": content})}
            
    except Exception as e:
        log_error("Handled 500", e)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": str(e)})}
"""

insight_engine_code = """import json
import boto3
import os
import time
import hashlib

# Use print for immediate CloudWatch capture
def log_info(msg):
    print(f"[INFO] {msg}")
def log_error(msg, exc=None):
    print(f"[ERROR] {msg}")
    if exc: print(f"Exception: {exc}")

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

PROFILES_TABLE = os.environ["PROFILES_TABLE"]
CACHE_TABLE = os.environ["CACHE_TABLE"]

def invoke_bedrock_with_retry(prompt, model_id="amazon.nova-lite-v1:0"):
    bedrock_body = json.dumps({
        "inferenceConfig": {"maxTokens": 1000},
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
    })
    
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays + [0]):
        try:
            log_info(f"Invoking bedrock model {model_id} (Attempt {attempt+1})")
            response = bedrock.invoke_model(
                body=bedrock_body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json",
            )
            res_body = json.loads(response.get("body").read())
            return res_body["output"]["message"]["content"][0]["text"]
        except Exception as e:
            log_error(f"Bedrock invocation failed for {model_id}", e)
            if attempt == len(delays):
                raise
            time.sleep(delay)

def lambda_handler(event, context):
    try:
        log_info(f"Event: {json.dumps(event)}")
        path = event.get("path", "")
        method = event.get("httpMethod", "GET")

        if "/profile" in path and method == "GET":
            table = dynamodb.Table(PROFILES_TABLE)
            response = table.get_item(Key={"creator_id": "techwithtim"})
            profile = response.get("Item", {})
            # Cast Decimals for JSON serialization
            serialized_profile = {k: (int(v) if hasattr(v, "to_integral_value") else v) for k, v in profile.items()}
            return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps(serialized_profile)}

        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
        user_message = body.get("message")
        
        system_prompt = "You are a professional YouTube strategist helping creators grow their channels. Your advice is data-driven, practical, and growth-oriented."
        
        if user_message:
            prompt = f"{system_prompt}\\n\\nUser Question: {user_message}"
        else:
            engagement_score = body.get("predicted_score", 85)
            topic = body.get("topic", "AI APIs")
            prompt = f"{system_prompt}\\n\\nAnalysis Request:\\nThe AI model predicted an engagement score of {engagement_score}/100 for the topic \\"{topic}\\".\\n1. Give a 2-sentence explanation of why this score is what it is.\\n2. Give a brief suggested script outline (Hook, Intro, Main, CTA).\\nFormat your response nicely."

        input_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)
        
        try:
            cache_response = cache_table.get_item(Key={"input_hash": input_hash})
            if "Item" in cache_response:
                log_info("Cache hit.")
                content = cache_response["Item"]["response"]
            else:
                content = invoke_bedrock_with_retry(prompt)
                cache_table.put_item(Item={"input_hash": input_hash, "response": content})
        except Exception as e:
            log_error("Cache/AI error", e)
            raise

        response_key = "response" if user_message else "insight"
        return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({response_key: content})}

    except Exception as e:
        log_error("Handled 500", e)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": str(e)})}
"""

prediction_api_code = """import json
import boto3
import os
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sagemaker_runtime = boto3.client("sagemaker-runtime")
dynamodb = boto3.resource("dynamodb")

ENDPOINT_NAME = os.environ["SAGEMAKER_ENDPOINT_NAME"]
PREDICTIONS_TABLE = os.environ["PREDICTIONS_TABLE"]
table = dynamodb.Table(PREDICTIONS_TABLE)

def invoke_sagemaker_with_retry(csv_input):
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays + [0]):
        try:
            logger.info("Invoking SageMaker", extra={"attempt": attempt + 1})
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=ENDPOINT_NAME, ContentType="text/csv", Body=csv_input
            )
            return json.loads(response["Body"].read().decode("utf-8"))
        except Exception as e:
            logger.error("SageMaker invocation failed", exc_info=True)
            if attempt == len(delays):
                raise
            time.sleep(delay)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        body = json.loads(event["body"]) if isinstance(event.get("body", "{}"), str) else event.get("body", {})

        creator_id = body.get("creator_id", "techwithtim")
        content_id = body.get("content_id", "draft_1")
        platform = body.get("platform", "youtube")

        engagement_ratio = float(body.get("engagement_ratio", 0.05))
        title_length = float(body.get("title_length", 30))
        trend_velocity = float(body.get("trend_velocity", 0.5))
        sentiment_score = float(body.get("sentiment_score", 0.5))

        csv_input = f"{engagement_ratio},{title_length},{trend_velocity},{sentiment_score}"
        
        result = invoke_sagemaker_with_retry(csv_input)
        prediction = result[0] if isinstance(result, list) else result

        viral_probability = prediction
        predicted_views = int(viral_probability * 1000000)

        prediction_id = f"pred_{content_id}_{context.aws_request_id}"

        item = {
            "creator_id": creator_id,
            "prediction_id": prediction_id,
            "platform": platform,
            "predicted_score": int(viral_probability * 100),
            "viral_probability": viral_probability,
            "predicted_views": predicted_views,
            "model_version": "xgboost_v1",
            "content_id": content_id
        }

        table.put_item(Item=item)

        return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps(item)}

    except Exception as e:
        log_msg = str(e)
        status_code = 503 if "Endpoint" in log_msg or "ModelError" in log_msg else 500
        error_msg = "SageMaker Prediction Service is currently inactive for this environment." if status_code == 503 else "Internal server error"
        logger.error(f"Prediction failed: {log_msg}", exc_info=True)
        return {"statusCode": status_code, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": error_msg, "details": log_msg})}
"""

content_enhancer_code = """import json
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
    # Nova models use different body structure than Anthropic
    if "nova" in model_id:
        bedrock_body = json.dumps({
            "inferenceConfig": {"maxTokens": 1000},
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
        })
    else:
        bedrock_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        })
    
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays + [0]):
        try:
            logger.info(f"Invoking bedrock model {model_id}", extra={"attempt": attempt + 1})
            response = bedrock.invoke_model(
                body=bedrock_body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json",
            )
            res_body = json.loads(response.get("body").read())
            
            if "nova" in model_id:
                return res_body["output"]["message"]["content"][0]["text"]
            else:
                return res_body.get("content", [{}])[0].get("text", "")
        except Exception as e:
            logger.error(f"Bedrock invocation failed for {model_id}", exc_info=True)
            # Fallback to Haiku if Nova fails or is unavailable
            if "nova" in model_id and attempt == 0:
                logger.warning("Falling back to Claude Haiku...")
                return invoke_bedrock_with_retry(prompt, model_id="anthropic.claude-3-haiku-20240307-v1:0")
            
            if attempt == len(delays):
                raise
            time.sleep(delay)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
        
        # Scope: News Summarization
        raw_trends = body.get("trends", [])
        if not raw_trends:
            return {"statusCode": 400, "body": json.dumps({"error": "No trends provided to summarize"})}

        trends_text = "\\n".join([f"- {t.get('topic', 'Unknown')}" for t in raw_trends[:10]])
        
        prompt = f\"\"\"You are a YouTube trend analyst.
Analyze the following raw trending topics:
{trends_text}

Provide a concise summary with:
1. Key Insight: What is the overall theme?
2. Why it's trending: What triggered these topics?
3. Content Opportunity: How can a creator capitalize on this today?
\"\"\"
        
        input_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)
        
        try:
            cache_response = cache_table.get_item(Key={"input_hash": input_hash})
            if "Item" in cache_response:
                logger.info("Cache hit for summarization.")
                summary = cache_response["Item"]["response"]
            else:
                summary = invoke_bedrock_with_retry(prompt)
                cache_table.put_item(Item={"input_hash": input_hash, "response": summary})
        except Exception as e:
            logger.error("Cache/Bedrock error", exc_info=True)
            raise

        return {
            "statusCode": 200, 
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"summary": summary}),
        }

    except Exception as e:
        logger.error("Service invocation failed", exc_info=True)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": "Internal server error"})}
"""

content_ingest_code = """import json
import os
import boto3
import logging
from datetime import datetime
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

CONTENT_TABLE = os.environ["CONTENT_TABLE"]
DATASET_BUCKET = os.environ.get("DATASET_BUCKET")
table = dynamodb.Table(CONTENT_TABLE)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        method = event.get("httpMethod", "POST")

        if method == "GET":
            # Using query if creator_id provided, otherwise scan but optimized with projection or limit
            qs = event.get("queryStringParameters") or {}
            creator_id = qs.get("creator_id")
            
            if creator_id:
                response = table.query(KeyConditionExpression=Key("creator_id").eq(creator_id), Limit=30)
            else:
                response = table.scan(Limit=30)
                
            items = response.get("Items", [])
            # Cast Decimals for JSON serialization
            clean_items = []
            for item in items:
                clean_item = {k: (int(v) if hasattr(v, "to_integral_value") else v) for k, v in item.items()}
                clean_items.append(clean_item)
            
            clean_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps(clean_items)}

        body = json.loads(event.get("body", "{}"))
        creator_id = body.get("creator_id")
        content_id = body.get("content_id")

        if not creator_id or not content_id:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": "Missing ID"})}

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
            s3.put_object(Bucket=DATASET_BUCKET, Key=s3_key, Body=json.dumps(item), ContentType="application/json")

        return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"message": "Content ingested successfully"})}

    except Exception as e:
        logger.error("Service invocation failed", exc_info=True)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": "Internal server error"})}
"""

trend_collector_code = """import json
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
"""

feedback_ingest_code = """import json
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
"""

files_to_write = {
    "idea_generator/main.py": idea_gen_code,
    "insight_engine/main.py": insight_engine_code,
    "prediction_api/main.py": prediction_api_code,
    "content_enhancer/main.py": content_enhancer_code,
    "content_ingestion/main.py": content_ingest_code,
    "trend_collector/main.py": trend_collector_code,
    "feedback_ingest/cleaner.py": feedback_ingest_code,
}

for rel_path, code in files_to_write.items():
    full_path = os.path.join(lambdas_dir, rel_path)
    with open(full_path, "w") as f:
        f.write(code)
    print(f"✅ SRE refactored {full_path}")

# IAM LEAST PRIVILEGE UPDATER
import boto3


def fix_iam_least_privilege():
    iam = boto3.client("iam", region_name="us-east-1")
    ROLE_NAME = "creator-intelligence-dev-lambda-execution-role"

    print("\\nFixing IAM Role to strictly scoped policies...")

    bad_policies = [
        "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
    ]

    for arn in bad_policies:
        try:
            iam.detach_role_policy(RoleName=ROLE_NAME, PolicyArn=arn)
            print(f"Detached {arn}")
        except Exception:
            pass

    # Create Least Privilege Inline Policy
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                "Resource": "arn:aws:dynamodb:us-east-1:*:table/creator-intelligence-dev-*",
            },
            {
                "Effect": "Allow",
                "Action": ["s3:PutObject", "s3:GetObject"],
                "Resource": "arn:aws:s3:::creator-intelligence-dev-*/*",
            },
            {"Effect": "Allow", "Action": "bedrock:InvokeModel", "Resource": "*"},
            {"Effect": "Allow", "Action": "sagemaker:InvokeEndpoint", "Resource": "*"},
            {
                "Effect": "Allow",
                "Action": "secretsmanager:GetSecretValue",
                "Resource": "*",
            },
        ],
    }

    try:
        iam.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName="CreatorIntelligenceSRELeastPrivilege",
            PolicyDocument=json.dumps(policy_doc),
        )
        print("✅ Least Privilege attached.")
    except Exception as e:
        print(f"❌ Error applying IAM policy: {e}")


fix_iam_least_privilege()
