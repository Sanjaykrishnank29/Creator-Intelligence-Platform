export interface Post {
  id: number;
  content?: string;
  title?: string;
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  views: number;
  timestamp: string;
  topic?: string;
}

export interface CreatorProfile {
  id: number;
  style_description: string;
  top_topics: string[]; // Parsed JSON in frontend, string in DB (handled by API)
  performance_patterns: string[]; // Parsed JSON in frontend
  last_updated: string;
}
