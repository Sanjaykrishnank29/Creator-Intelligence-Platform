import requests
from datetime import datetime


class YouTubeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def get_uploads_playlist_id(self, channel_id):
        url = f"{self.base_url}/channels?part=contentDetails&id={channel_id}&key={self.api_key}"
        response = requests.get(url).json()
        if "items" not in response or not response["items"]:
            raise Exception(f"Channel {channel_id} not found.")
        return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def get_recent_video_ids(self, playlist_id, max_results=30):
        url = f"{self.base_url}/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max_results}&key={self.api_key}"
        response = requests.get(url).json()
        if "items" not in response:
            return []
        return [item["snippet"]["resourceId"]["videoId"] for item in response["items"]]

    def get_video_stats(self, video_ids):
        if not video_ids:
            return []
        url = f"{self.base_url}/videos?part=snippet,statistics&id={','.join(video_ids)}&key={self.api_key}"
        response = requests.get(url).json()

        data = []
        for item in response.get("items", []):
            snippet = item["snippet"]
            stats = item["statistics"]

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))

            # Preprocessing
            publish_time = datetime.strptime(
                snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
            )

            # Engagement score formula
            engagement_score = (likes * 0.5) + (comments * 0.3) + (views * 0.2)

            data.append(
                {
                    "video_id": item["id"],
                    "title": snippet["title"],
                    "published_at": snippet["publishedAt"],
                    "published_hour": publish_time.hour,
                    "title_length": len(snippet["title"]),
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "engagement_score": round(engagement_score, 2),
                }
            )
        return data

    def fetch_creator_history(self, channel_id, max_results=30):
        playlist_id = self.get_uploads_playlist_id(channel_id)
        video_ids = self.get_recent_video_ids(playlist_id, max_results)
        return self.get_video_stats(video_ids)
