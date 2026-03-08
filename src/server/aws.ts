import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";
import { Post, CreatorProfile } from "../types.ts";

const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;
const region = process.env.AWS_REGION || "us-east-1";

if (!accessKeyId || !secretAccessKey) {
  console.error("AWS credentials are missing!");
}

const client = new BedrockRuntimeClient({
  region,
  credentials: {
    accessKeyId: accessKeyId || "",
    secretAccessKey: secretAccessKey || "",
  },
});

export async function analyzeCreatorHistory(posts: Post[]) {
  if (!accessKeyId) {
    console.error("Cannot analyze history: AWS credentials missing");
    return null;
  }
  if (!posts || posts.length === 0) return null;

  const postsText = posts.map(p => 
    `[${p.platform}] "${p.content}" (Likes: ${p.likes}, Comments: ${p.comments}, Views: ${p.views})`
  ).join("\n");

  const prompt = `
    Analyze the following social media posts and engagement metrics to build a creator profile.
    
    Posts:
    ${postsText}

    Extract the following:
    1. A description of the creator's unique style and tone.
    2. The top 3 performing topics based on engagement.
    3. Key performance patterns (e.g., specific formats, lengths, or themes that work well).

    Return the result in strictly valid JSON format with the keys: style_description (string), top_topics (array of strings), and performance_patterns (array of strings). Do not include markdown formatting or backticks around the json.
  `;

  try {
    const command = new InvokeModelCommand({
      modelId: "anthropic.claude-3-haiku-20240307-v1:0", // Fast model for analysis
      contentType: "application/json",
      accept: "application/json",
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: 1000,
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: prompt }],
          },
        ],
      }),
    });

    const response = await client.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));
    const text = responseBody.content[0].text;
    return JSON.parse(text || "{}");
  } catch (error) {
    console.error("Error analyzing history:", error);
    return null;
  }
}

export async function predictPerformance(idea: string, profile: CreatorProfile) {
  if (!accessKeyId) {
    console.error("Cannot predict performance: AWS credentials missing");
    return null;
  }
  const prompt = `
    Given the following creator profile, predict the engagement score (0-100) for a new content idea.
    
    Creator Profile:
    Style: ${profile.style_description}
    Top Topics: ${profile.top_topics}
    Patterns: ${profile.performance_patterns}

    New Content Idea: "${idea}"

    Predict the engagement score (0-100) where 100 is a viral hit and 0 is no engagement.
    Provide a reasoning based on the profile.
    Suggest 3 specific improvements to increase the score.

    Return strictly valid JSON with the keys: score (integer), reasoning (string), improvements (array of strings). Do not include markdown formatting or backticks around the json.
  `;

  try {
    const command = new InvokeModelCommand({
      modelId: "anthropic.claude-3-haiku-20240307-v1:0",
      contentType: "application/json",
      accept: "application/json",
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: 1000,
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: prompt }],
          },
        ],
      }),
    });

    const response = await client.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));
    const text = responseBody.content[0].text;
    return JSON.parse(text || "{}");
  } catch (error) {
    console.error("Error predicting performance:", error);
    return null;
  }
}

export async function adaptContent(idea: string, profile: CreatorProfile) {
  if (!accessKeyId) {
    console.error("Cannot adapt content: AWS credentials missing");
    return null;
  }
  const prompt = `
    Rewrite the following content idea for Instagram, LinkedIn, and Twitter.
    Maintain the creator's unique style but optimize for each platform's best practices.

    Creator Style: ${profile.style_description}
    Content Idea: "${idea}"

    Return strictly valid JSON with platform names (instagram, linkedin, twitter) as keys and the rewritten content as values (strings). Do not include markdown formatting or backticks around the json.
  `;

  try {
     const command = new InvokeModelCommand({
      modelId: "anthropic.claude-3-haiku-20240307-v1:0",
      contentType: "application/json",
      accept: "application/json",
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: 1000,
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: prompt }],
          },
        ],
      }),
    });

    const response = await client.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));
    const text = responseBody.content[0].text;
    return JSON.parse(text || "{}");
  } catch (error) {
    console.error("Error adapting content:", error);
    return null;
  }
}

export async function chatWithCreatorAI(message: string, history: { role: string, parts: { text: string }[] }[]) {
  if (!accessKeyId) {
    console.error("Cannot chat: AWS credentials missing");
    return null;
  }

  // Convert Gemini history format to Claude history format
  const convertedHistory = history.map(h => ({
    role: h.role === "model" ? "assistant" : "user",
    content: [{ type: "text", text: h.parts[0].text }]
  }));

  // Append new message
  convertedHistory.push({
    role: "user",
    content: [{ type: "text", text: message }]
  });

  try {
    const command = new InvokeModelCommand({
      modelId: "anthropic.claude-3-haiku-20240307-v1:0",
      contentType: "application/json",
      accept: "application/json",
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: 1000,
        messages: convertedHistory,
      }),
    });

    const response = await client.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));
    return responseBody.content[0].text;
  } catch (error) {
    console.error("Chat error:", error);
    return null;
  }
}
