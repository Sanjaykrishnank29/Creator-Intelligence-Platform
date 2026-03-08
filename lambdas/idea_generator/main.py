import json
import boto3
import os
import time
import hashlib
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

TRENDS_TABLE = os.environ["TRENDS_TABLE"]
CONTENT_TABLE = os.environ["CONTENT_TABLE"]
CACHE_TABLE = os.environ["CACHE_TABLE"]

# ─── In-memory trend cache (reuses Lambda container for 5 min) ─────────────────
_trends_cache: dict = {"data": None, "expires": 0.0}


def get_trends_cached():
    """Get trends from DynamoDB with 5-minute in-memory cache. Eliminates repeated scans."""
    now = time.time()
    if _trends_cache["data"] is not None and now < _trends_cache["expires"]:
        logger.info("Trend cache hit (in-memory)")
        return _trends_cache["data"]
    table = dynamodb.Table(TRENDS_TABLE)
    items = table.scan(Limit=8).get("Items", [])
    _trends_cache["data"] = items
    _trends_cache["expires"] = now + 300  # 5-minute TTL
    return items


def keyword_overlap(a: str, b: str) -> float:
    """Free keyword-based similarity — replaces expensive Titan Embeddings."""
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa:
        return 0.0
    return len(wa & wb) / len(wa)


def invoke_bedrock(
    prompt: str, model_id: str = "amazon.nova-lite-v1:0", max_tokens: int = 800
) -> str:
    """Invoke Bedrock Nova Lite with exponential backoff."""
    body = json.dumps(
        {
            "inferenceConfig": {"maxTokens": max_tokens},
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
        }
    )
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays + [0]):
        try:
            logger.info(f"Bedrock invoke attempt {attempt + 1}")
            resp = bedrock.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json",
            )
            return json.loads(resp["body"].read())["output"]["message"]["content"][0][
                "text"
            ]
        except Exception as e:
            logger.error(f"Bedrock attempt {attempt + 1} failed: {e}")
            if attempt == len(delays):
                raise
            time.sleep(delay)


def lambda_handler(event, context):
    try:
        body = (
            json.loads(event.get("body", "{}"))
            if isinstance(event.get("body"), str)
            else event.get("body", {})
        )

        creator_id = body.get("creator_id", "techwithtim")
        niche = body.get("niche") or body.get("topic", "General Tech")
        platform = body.get("platform", "YouTube")

        # ── DynamoDB response cache check (no Bedrock call if same niche+platform) ──
        cache_key = hashlib.sha256(
            f"{niche.strip().lower()}:{platform.lower()}".encode()
        ).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)
        cached = cache_table.get_item(Key={"input_hash": cache_key}).get("Item")
        if cached:
            logger.info("DynamoDB cache hit — skipping Bedrock call")
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {"ideas": json.loads(cached["response"]), "cached": True}
                ),
            }

        # ── Keyword-based trend matching (replaces 10 Titan Embed API calls) ──────────
        trends = [t.get("topic", "") for t in get_trends_cached() if t.get("topic")]

        from boto3.dynamodb.conditions import Key as DKey

        content_table = dynamodb.Table(CONTENT_TABLE)
        history = [
            i.get("title", "")
            for i in content_table.query(
                KeyConditionExpression=DKey("creator_id").eq(creator_id), Limit=8
            ).get("Items", [])
            if i.get("title")
        ]

        # Score pairs with free keyword matching — no Bedrock Titan calls
        if trends and history:
            matches = sorted(
                [
                    {"trend": t, "video": h, "score": keyword_overlap(t, h)}
                    for t in trends[:5]
                    for h in history[:5]
                ],
                key=lambda x: x["score"],
                reverse=True,
            )[:3]
            context_str = "\n".join(
                [f"- {m['trend']} (related: {m['video']})" for m in matches]
            )
            prompt = (
                f"You are an elite YouTube strategist. Generate 5 viral video ideas for the niche: "
                f'"{niche}" on {platform}.\n'
                f"Use these current trends as inspiration:\n{context_str}\n\n"
                f'Return ONLY a JSON array: [{{"title":"...","explanation":"...","performance_reasoning":"..."}}]'
            )
        else:
            prompt = (
                f'You are an elite YouTube strategist. Generate 5 viral video ideas for: "{niche}" on {platform}.\n'
                f'Return ONLY a JSON array: [{{"title":"...","explanation":"...","performance_reasoning":"..."}}]'
            )

        # ── Single Bedrock call (down from 11 calls per request) ────────────────────
        content = invoke_bedrock(prompt, max_tokens=800)

        # Parse JSON from response
        cleaned = content.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        try:
            ideas = json.loads(cleaned)
        except Exception:
            ideas = [
                {
                    "title": "Content Idea",
                    "explanation": content[:300],
                    "performance_reasoning": "",
                }
            ]

        # Store in cache for next identical request
        cache_table.put_item(
            Item={"input_hash": cache_key, "response": json.dumps(ideas)}
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"ideas": ideas}),
        }

    except Exception as e:
        logger.error(f"idea_generator failed: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }
