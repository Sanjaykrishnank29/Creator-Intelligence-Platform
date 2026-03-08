import json
import boto3
import os
import time
import hashlib


# Use print for immediate CloudWatch capture
def log_info(msg):
    print(f"[INFO] {msg}")


def log_error(msg, exc=None):
    print(f"[ERROR] {msg}")
    if exc:
        print(f"Exception: {exc}")


bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

PROFILES_TABLE = os.environ["PROFILES_TABLE"]
CACHE_TABLE = os.environ["CACHE_TABLE"]
TRENDS_TABLE = os.environ.get("TRENDS_TABLE", "creator-intelligence-dev-TrendSignals")

# ─── In-memory trend cache (reuses Lambda container for 5 min) ─────────────────
_trends_cache: dict = {"data": None, "expires": 0.0}


def get_trends_cached():
    """Get trends from DynamoDB with 5-minute in-memory cache. Eliminates repeated scans."""
    now = time.time()
    if _trends_cache["data"] is not None and now < _trends_cache["expires"]:
        log_info("Trend cache hit (in-memory)")
        return _trends_cache["data"]
    table = dynamodb.Table(TRENDS_TABLE)
    items = table.scan(Limit=10).get("Items", [])
    _trends_cache["data"] = items
    _trends_cache["expires"] = now + 300  # 5-minute TTL
    return items


def invoke_bedrock_with_retry(prompt, model_id="amazon.nova-lite-v1:0"):
    bedrock_body = json.dumps(
        {
            "inferenceConfig": {"maxTokens": 500},
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
        }
    )

    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays + [0]):
        try:
            log_info(f"Invoking bedrock model {model_id} (Attempt {attempt + 1})")
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
            serialized_profile = {
                k: (int(v) if hasattr(v, "to_integral_value") else v)
                for k, v in profile.items()
            }
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(serialized_profile),
            }

        body = (
            json.loads(event.get("body", "{}"))
            if isinstance(event.get("body"), str)
            else event.get("body", {})
        )
        user_message = body.get("message")
        history = body.get("history", [])
        contents_to_summarize = body.get("contents")
        platform = body.get("platform")
        target_type = body.get("target_type")

        system_prompt = "You are a professional YouTube strategist and social media growth expert. Your speaking style is natural, charismatic, and high-energy—like a real creator. Your goal is to maximize retention and engagement."

        if contents_to_summarize and isinstance(contents_to_summarize, list):
            context_text = "\n\n".join(
                [
                    f"Source Material {i + 1}:\n{c}"
                    for i, c in enumerate(contents_to_summarize)
                ]
            )

            if platform and target_type:
                if platform == "YouTube":
                    prompt = f"{system_prompt}\n\nTASK: Generate a natural, high-retention YouTube video script based on the source material below. The script should sound like a YouTuber speaking directly to the camera—concise, punchy, and engaging. Include a strong Hook, a natural transition, key value points, and a CTA.\n\nPLATFORM: YouTube (Natural Speech Style)\n\nSOURCE MATERIAL:\n{context_text}\n\nScript Synthesis (Natural Voice):"
                elif platform == "Instagram":
                    prompt = f"{system_prompt}\n\nTASK: Generate an engaging Instagram caption and visual suggestion based on the source material below. Use catchy emojis, a clear value proposition, and a call-to-action that encourages comments/shares. Keep the tone vibrant and social.\n\nPLATFORM: Instagram\n\nSOURCE MATERIAL:\n{context_text}\n\nPost Synthesis:"
                elif platform == "Twitter":
                    prompt = f"{system_prompt}\n\nTASK: Generate a viral-style Twitter (X) thread based on the source material below. Break the info into 3-5 punchy tweets. Use line breaks for readability and ensure the hook tweet is irresistible.\n\nPLATFORM: Twitter/X Thread\n\nSOURCE MATERIAL:\n{context_text}\n\nThread Synthesis:"
                else:
                    prompt = f"{system_prompt}\n\nTASK: Synthesize the material below into a natural, platform-appropriate content script. Tone: High-energy creator.\n\nSOURCE MATERIAL:\n{context_text}\n\nSynthesis:"
            else:
                prompt = f"{system_prompt}\n\nTASK: Please summarize, synthesize, and organize the following connected brainstorming nodes into a highly cohesive, concise single-paragraph overview that perfectly captures the overarching theme, actionable insights, and key takeaways.\n\n{context_text}\n\nSummary and Action Plan Synthesis:"

            response_key = "summary"
        elif user_message:
            history_str = "\n".join(
                [
                    f"{msg.get('role', 'user')}: {msg.get('text', '')}"
                    for msg in history[-4:]
                ]
            )

            # --- RAG IMPLEMENTATION ---
            # Fetch top 10 recent trends from DynamoDB using cached function
            try:
                trends_data = get_trends_cached()
                trends_list = []
                for item in trends_data:
                    topic = item.get("topic", "")
                    summary = item.get("summary", "")
                    if topic:
                        trends_list.append(f"- {topic}: {summary}")

                if trends_list:
                    trends_context = "\n".join(trends_list)
                    ragContext = f"\n\n--- CURRENT REAL-TIME TRENDS (RAG CONTEXT) ---\nUse the following trending news from the database if the user asks about recent trends, top 10 news, or what's happening now:\n{trends_context}\n----------------------------------------------"
                else:
                    ragContext = ""
            except Exception as e:
                log_error("Failed to fetch TrendSignals for RAG context", e)
                ragContext = ""

            prompt = f"{system_prompt}{ragContext}\n\nChat History:\n{history_str}\n\nUser Question: {user_message}"
            response_key = "response"
        else:
            engagement_score = body.get("predicted_score", 85)
            topic = body.get("topic", "AI APIs")
            prompt = f'{system_prompt}\n\nAnalysis Request:\nThe AI model predicted an engagement score of {engagement_score}/100 for the topic "{topic}".\n1. Give a 2-sentence explanation of why this score is what it is.\n2. Give a brief suggested script outline (Hook, Intro, Main, CTA).\nFormat your response nicely.'
            response_key = "insight"

        input_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)

        try:
            cache_response = cache_table.get_item(Key={"input_hash": input_hash})
            if "Item" in cache_response:
                log_info("Cache hit.")
                content = cache_response["Item"]["response"]
            else:
                content = invoke_bedrock_with_retry(prompt)
                cache_table.put_item(
                    Item={"input_hash": input_hash, "response": content}
                )
        except Exception as e:
            log_error("Cache/AI error", e)
            raise

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({response_key: content}),
        }

    except Exception as e:
        log_error("Handled 500", e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }
