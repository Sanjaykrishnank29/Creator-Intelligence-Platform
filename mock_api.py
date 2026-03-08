import json
import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from lambdas.common.youtube_utils import YouTubeClient

load_dotenv()

os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["RAW_TRENDS_BUCKET"] = "mock-raw-trends"
os.environ["SECRET_ARN"] = "mock-secret-arn"
os.environ["CONTENT_TABLE_NAME"] = "mock-content-table"
os.environ["DATASET_BUCKET"] = "mock-dataset-bucket"
os.environ["SAGEMAKER_ENDPOINT_NAME"] = "mock-sagemaker-endpoint"
os.environ["PREDICTIONS_TABLE"] = "mock-predictions-table"
os.environ["TRENDS_TABLE"] = "mock-trends-table"
os.environ["CONTENT_TABLE"] = "mock-content-table"
os.environ["CACHE_TABLE"] = "mock-cache-table"

# Creds for real-data integration
os.environ["Access_key"] = os.getenv("Access_key")
os.environ["Secret_access_key"] = os.getenv("Secret_access_key")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lambdas.idea_generator.main import lambda_handler as idea_handler
from lambdas.prediction_api.main import lambda_handler as prediction_handler
from lambdas.insight_engine.main import lambda_handler as insight_handler
from lambdas.content_enhancer.main import lambda_handler as enhancer_handler

app = FastAPI()

# Initialize YouTube Client
yt_client = YouTubeClient(api_key=os.getenv("YOUTUBE_API_KEY"))
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DummyContext:
    aws_request_id = "local-12345"


mock_db = {
    "posts": [],
    "recent_videos": [],  # Real YouTube data storage
    "profile": {
        "style_description": "Data-driven, precise, and tech-focused.",
        "top_topics": '["AWS", "Generative AI", "Coding"]',
        "performance_patterns": '["Technical deep dives", "Code examples"]',
    },
}


@app.get("/api/health")
def health():
    return {"status": "ok", "backend": "fastapi"}


@app.post("/api/chat")
async def chat(request: Request):
    return {
        "response": "I am the Creator Assistant powered by local Python Lambdas! I've been successfully refactored out of the old Node server."
    }


@app.post("/api/summarize")
async def summarize(request: Request):
    body = await request.json()
    contents = body.get("contents", [""])
    topic = contents[0][:100] if contents else "General Topic"

    event = {"body": {"topic": topic, "predicted_score": 88}}
    res = insight_handler(event, DummyContext())
    return {"summary": json.loads(res["body"]).get("insight")}


@app.post("/api/generate")
async def generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")

    event = {
        "body": {
            "creator_id": "test",
            "niche": "Tech",
            "platform": "YouTube",
            "prompt": prompt,
            "recent_topics": [v["title"] for v in mock_db["recent_videos"][:5]],
        }
    }
    res = idea_handler(event, DummyContext())

    ideas = json.loads(res["body"]).get("ideas", [])
    if isinstance(ideas, list) and len(ideas) > 0:
        content = "\\n".join(
            [f"- {i.get('title', 'Idea')}: {i.get('reason', '')}" for i in ideas]
        )
    else:
        content = json.loads(res["body"]).get("note", "Generated new ideas.")
    return {"content": content}


@app.get("/api/posts")
def get_posts():
    return mock_db["posts"]


@app.post("/api/posts")
async def add_post(request: Request):
    body = await request.json()
    mock_db["posts"].append(body)
    return {"success": True}


@app.get("/api/profile")
def get_profile():
    return mock_db["profile"]


@app.post("/api/analyze")
async def analyze(request: Request):
    print(f"Analyzing YouTube Channel: {CHANNEL_ID}")
    try:
        videos = yt_client.fetch_creator_history(CHANNEL_ID)
        mock_db["recent_videos"] = videos

        # Basic profile derivation from real data
        top_titles = [v["title"] for v in videos[:5]]
        avg_engagement = (
            sum([v["engagement_score"] for v in videos]) / len(videos) if videos else 0
        )

        profile = {
            "style_description": f"Focuses on topics like: {', '.join(top_titles[:2])}.",
            "top_topics": top_titles,
            "performance_patterns": [
                f"Average engagement score of {round(avg_engagement, 2)} across last 30 videos."
            ],
        }

        mock_db["profile"].update(
            {
                "style_description": profile["style_description"],
                "top_topics": json.dumps(profile["top_topics"]),
                "performance_patterns": json.dumps(profile["performance_patterns"]),
            }
        )
        return profile
    except Exception as e:
        print(f"Error analyzing YouTube: {e}")
        return {"error": str(e)}


@app.post("/api/predict")
async def predict(request: Request):
    body = await request.json()
    idea = body.get("idea", "")

    # Calculate real context from history
    recent_performance = 0.05  # Default
    if mock_db["recent_videos"]:
        scores = [v["engagement_score"] for v in mock_db["recent_videos"]]
        avg = sum(scores) / len(scores)
        recent_performance = min(avg / 1000, 1.0)  # Scale to ratio

    event = {
        "body": {
            "creator_id": "test",
            "content_id": "draft_mock",
            "engagement_ratio": recent_performance,
            "title_length": len(idea),
            "trend_velocity": 0.8,
            "sentiment_score": 0.9,
        }
    }
    res = prediction_handler(event, DummyContext())
    data = json.loads(res["body"])

    return {
        "score": data.get("predicted_score", 50),
        "reasoning": f"Based on your recent YouTube performance ({round(recent_performance * 100, 1)}% engagement benchmark), this idea shows strong potential. Views est: {data.get('predicted_views', 0)}",
        "improvements": [
            "Use stronger hooks relative to your top videos",
            "Keep title length optimized for your audience",
            "Leverage the high trend velocity of this topic",
        ],
    }


@app.post("/api/adapt")
async def adapt(request: Request):
    body = await request.json()
    idea = body.get("idea", "")

    event = {"body": {"topic": idea[:50], "title": idea, "platform": "multi"}}
    res = enhancer_handler(event, DummyContext())
    data = json.loads(res["body"])

    return {
        "instagram": data.get("creative_enhancements", "IG Hook"),
        "linkedin": f"Professional thread setup for: {idea}",
        "twitter": f"Thread: 1/ {idea} #Tech",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mock_api:app", host="0.0.0.0", port=8000, reload=True)
