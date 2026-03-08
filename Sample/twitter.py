from flask import Flask, jsonify
from ntscraper import Nitter

app = Flask(__name__)

# Initialize Nitter scraper
scraper = Nitter(log_level=1)


@app.route("/creator/<username>", methods=["GET"])
def get_creator_data(username):
    try:
        print(f"Fetching tweets for {username} via Nitter...")
        # Get up to 10 tweets for the user
        tweets = scraper.get_tweets(username, mode="user", number=10)

        if not tweets or "tweets" not in tweets or not tweets["tweets"]:
            return jsonify(
                {
                    "error": "No tweets found or scraper blocked (try a different instance)"
                }
            ), 404

        result = []
        for t in tweets["tweets"]:
            result.append(
                {
                    "text": t.get("text", ""),
                    "likes": t.get("stats", {}).get("likes", 0),
                    "retweets": t.get("stats", {}).get("retweets", 0),
                    "replies": t.get("stats", {}).get("comments", 0),
                    "created_at": t.get("date", ""),
                }
            )

        return jsonify(result)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/creator/<username>/profile", methods=["GET"])
def get_creator_profile(username):
    try:
        print(f"Fetching profile for {username} via Nitter...")
        profile = scraper.get_profile_info(username)
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
        return jsonify(profile)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
