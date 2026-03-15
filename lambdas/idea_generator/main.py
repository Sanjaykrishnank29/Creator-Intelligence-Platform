import json
import boto3
import os
import time
import hashlib
import logging
import random
import urllib.request
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

TRENDS_TABLE = os.environ["TRENDS_TABLE"]
CONTENT_TABLE = os.environ["CONTENT_TABLE"]
CACHE_TABLE = os.environ["CACHE_TABLE"]
PROFILES_TABLE = os.environ.get("PROFILES_TABLE", "creator-intelligence-dev-CreatorProfiles")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")


def fetch_live_news(niche: str, page_size: int = 8) -> list[str]:
    """Fetch LIVE headlines from NewsAPI using the creator's niche as a query.
    Returns a list of article title strings."""
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set — skipping live news fetch")
        return []

    query = urllib.parse.quote(niche[:50])
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={query}&language=en&sortBy=publishedAt"
        f"&pageSize={page_size}&apiKey={NEWS_API_KEY}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        articles = data.get("articles", [])
        headlines = [a["title"] for a in articles if a.get("title") and "[Removed]" not in a["title"]]
        logger.info(f"Fetched {len(headlines)} live headlines for niche: {niche!r}")
        return headlines
    except Exception as e:
        logger.error(f"NewsAPI fetch failed: {e}")
        return []


def get_creator_niche(creator_id: str) -> str:
    """Read niche from the creator's DynamoDB profile. Falls back to 'General Tech'."""
    try:
        table = dynamodb.Table(PROFILES_TABLE)
        item = table.get_item(Key={"creator_id": creator_id}).get("Item", {})
        # Try common field names the profile might use
        niche = (
            item.get("niche")
            or item.get("primary_niche")
            or item.get("category")
            or item.get("content_category")
            or "General Tech"
        )
        logger.info(f"Creator {creator_id!r} niche → {niche!r}")
        return str(niche)
    except Exception as e:
        logger.error(f"Could not read creator profile: {e}")
        return "General Tech"


def invoke_bedrock(
    prompt: str, model_id: str = "amazon.nova-lite-v1:0", max_tokens: int = 800
) -> str:
    """Invoke Bedrock Nova Lite with temperature for varied outputs."""
    body = json.dumps(
        {
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.9},
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
            return json.loads(resp["body"].read())["output"]["message"]["content"][0]["text"]
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
        platform = body.get("platform", "YouTube")
        bust_cache = body.get("bust_cache", False)

        # ── Step 1: Get creator's real niche from DynamoDB profile ──────────────
        # Use niche from request body only if explicitly provided and NOT a generic placeholder
        niche_override = body.get("niche", "").strip()
        ignored_placeholders = (
            "Generate a creative content idea",
            "AI & Tech Trends",
            "Click regenerate to create content...",
            "New ai-note"
        )
        if niche_override and niche_override not in ignored_placeholders:
            niche = niche_override
        else:
            niche = get_creator_niche(creator_id)

        logger.info(f"Generating ideas for niche={niche!r}, platform={platform!r}, bust_cache={bust_cache}")

        # ── Step 2: Cache check (skip if bust_cache=True — i.e. manual regenerate) ──
        cache_key = hashlib.sha256(f"{niche.strip().lower()}:{platform.lower()}".encode()).hexdigest()
        cache_table = dynamodb.Table(CACHE_TABLE)

        if not bust_cache:
            cached = cache_table.get_item(Key={"input_hash": cache_key}).get("Item")
            if cached:
                logger.info("DynamoDB cache hit — returning cached ideas")
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"ideas": json.loads(cached["response"]), "cached": True}),
                }
        else:
            logger.info("bust_cache=True — fetching fresh content")

        # ── Step 3: Fetch LIVE news from NewsAPI using creator's niche ──────────
        live_headlines = fetch_live_news(niche)

        # ── Step 4: Build a unique prompt with live news as context ─────────────
        angles = [
            "Focus on a technical deep-dive into a specific software feature.",
            "Focus on an industry-shifting technical breakthrough.",
            "Focus on a step-by-step 'Hello World' to production guide.",
            "Focus on 'The State of [Niche] in 2026' — predictions and reality.",
            "Focus on why certain technical paradigms are failing and what's next.",
            "Focus on a critical comparison between two leading technologies in the niche.",
            "Focus on a myth-busting technical analysis of common misconceptions.",
            "Focus on an expert-level career path or advanced skill-building strategy.",
            "Focus on a post-mortem/root cause analysis of a well-known technical failure.",
            "Focus on how AI is fundamentally changing workflows within this specific niche.",
        ]
        angle_directive = random.choice(angles)

        base_prompt = (
            f"You are an elite {platform} content strategist and subject matter expert.\n\n"
            f"PRIMARY OBJECTIVE: Generate 5 UNIQUE, high-value video ideas for the niche: {niche}.\n"
            f"STRICT ADHERENCE: All ideas MUST be directly related to {niche}. Do not provide generic viral advice.\n"
        )

        if live_headlines:
            news_block = "\n".join(f"- {h}" for h in live_headlines[:6])
            prompt = (
                f"{base_prompt}\n"
                f"LATEST LIVE NEWS (Context):\n{news_block}\n\n"
                f"CREATIVE ANGLE FOR THIS BATCH: {angle_directive}\n\n"
                f"Generate ideas that are INSPIRED by the news above but tailored for a {niche} audience.\n\n"
                f'Return ONLY a JSON array: [{{"title":"...","explanation":"...","performance_reasoning":"..."}}]'
            )
        else:
            prompt = (
                f"{base_prompt}\n"
                f"Note: Current news could not be fetched. Rely on your internal knowledge of the latest developments and trends in {niche}.\n\n"
                f"CREATIVE ANGLE FOR THIS BATCH: {angle_directive}\n\n"
                f'Return ONLY a JSON array: [{{"title":"...","explanation":"...","performance_reasoning":"..."}}]'
            )


        # ── Step 5: Single Bedrock call ─────────────────────────────────────────
        content = invoke_bedrock(prompt, max_tokens=800)

        cleaned = content.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        try:
            ideas = json.loads(cleaned)
        except Exception:
            ideas = [{"title": "Content Idea", "explanation": content[:300], "performance_reasoning": ""}]

        # Store in cache only for non-busted calls (to reuse for Generate page)
        if not bust_cache:
            cache_table.put_item(Item={"input_hash": cache_key, "response": json.dumps(ideas)})

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"ideas": ideas, "niche_used": niche}),
        }

    except Exception as e:
        logger.error(f"idea_generator failed: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Internal server error"}),
        }
