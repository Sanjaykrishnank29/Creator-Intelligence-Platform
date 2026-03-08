import Database from 'better-sqlite3';
import { Post, CreatorProfile } from '../types.ts';

interface CreatorProfileDB extends Omit<CreatorProfile, 'top_topics' | 'performance_patterns'> {
  top_topics: string;
  performance_patterns: string;
}

const db = new Database('creator_intelligence.db');


export function initDb() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      platform TEXT NOT NULL,
      likes INTEGER DEFAULT 0,
      comments INTEGER DEFAULT 0,
      shares INTEGER DEFAULT 0,
      views INTEGER DEFAULT 0,
      timestamp TEXT NOT NULL,
      topic TEXT
    );

    CREATE TABLE IF NOT EXISTS creator_profile (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      style_description TEXT,
      top_topics TEXT,
      performance_patterns TEXT,
      last_updated TEXT
    );
  `);

  // Check if we have data, if not, seed some
  const count = db.prepare('SELECT count(*) as count FROM posts').get() as { count: number };
  if (count.count === 0) {
    seedData();
  }
}

function seedData() {
  const posts = [
    {
      content: "5 tips to improve your React performance instantly! 🚀 #coding #reactjs",
      platform: "Twitter",
      likes: 120,
      comments: 15,
      shares: 30,
      views: 5000,
      timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
      topic: "Coding Tips"
    },
    {
      content: "Why I stopped using Redux in 2024. A thread. 🧵",
      platform: "Twitter",
      likes: 850,
      comments: 120,
      shares: 200,
      views: 25000,
      timestamp: new Date(Date.now() - 86400000 * 5).toISOString(),
      topic: "Opinion"
    },
    {
      content: "Day in the life of a Software Engineer at a startup. 💻☕️",
      platform: "Instagram",
      likes: 2500,
      comments: 80,
      shares: 50,
      views: 15000,
      timestamp: new Date(Date.now() - 86400000 * 10).toISOString(),
      topic: "Lifestyle"
    },
    {
      content: "How to center a div. The ultimate guide.",
      platform: "LinkedIn",
      likes: 500,
      comments: 45,
      shares: 20,
      views: 8000,
      timestamp: new Date(Date.now() - 86400000 * 15).toISOString(),
      topic: "Tutorial"
    },
    {
      content: "Just shipped a new feature! Check it out.",
      platform: "Twitter",
      likes: 30,
      comments: 2,
      shares: 1,
      views: 800,
      timestamp: new Date(Date.now() - 86400000 * 20).toISOString(),
      topic: "Update"
    }
  ];

  const insert = db.prepare(`
    INSERT INTO posts (content, platform, likes, comments, shares, views, timestamp, topic)
    VALUES (@content, @platform, @likes, @comments, @shares, @views, @timestamp, @topic)
  `);

  const insertMany = db.transaction((posts) => {
    for (const post of posts) insert.run(post);
  });

  insertMany(posts);
  console.log('Seeded initial data');
}

export function getPosts(): Post[] {
  return db.prepare('SELECT * FROM posts ORDER BY timestamp DESC').all() as Post[];
}

export function addPost(post: Omit<Post, 'id'>) {
  const insert = db.prepare(`
    INSERT INTO posts (content, platform, likes, comments, shares, views, timestamp, topic)
    VALUES (@content, @platform, @likes, @comments, @shares, @views, @timestamp, @topic)
  `);
  return insert.run(post);
}

export function getProfile(): CreatorProfileDB | undefined {
  return db.prepare('SELECT * FROM creator_profile ORDER BY id DESC LIMIT 1').get() as CreatorProfileDB | undefined;
}

export function updateProfile(profile: Omit<CreatorProfileDB, 'id'>) {
  const insert = db.prepare(`
    INSERT INTO creator_profile (style_description, top_topics, performance_patterns, last_updated)
    VALUES (@style_description, @top_topics, @performance_patterns, @last_updated)
  `);
  return insert.run(profile);
}
