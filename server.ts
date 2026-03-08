/**
 * Creator Intelligence Platform - Express Server (AWS Bedrock Backend)
 *
 * This server proxies all /api/* requests from the Vite frontend to the
 * AWS API Gateway, which routes them to Bedrock-powered Lambda functions.
 *
 * API Gateway: https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod
 *
 * Frontend Route -> AWS Lambda mapping:
 *   POST /api/chat      -> insight_engine  (Creator Assistant chat via Bedrock)
 *   POST /api/summarize -> content_enhancer (Summary node via Bedrock)
 *   POST /api/generate  -> idea_generator   (AI Note canvas node)
 *   POST /api/analyze   -> insight_engine   (Profile analysis)
 *   POST /api/predict   -> prediction_api   (Performance prediction)
 *   GET  /api/posts     -> content_ingestion (Post history)
 *   GET  /api/profile   -> insight_engine   (Creator profile)
 */

import 'dotenv/config';
import express from 'express';

const app = express();
const PORT = 8000;

const AWS_API_BASE = 'https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod';

app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// Utility: Forward a request to AWS API Gateway and return the response
// ─────────────────────────────────────────────────────────────────────
async function forwardToAWS(awsPath: string, method: string, body?: object, queryString?: string) {
  const url = `${AWS_API_BASE}${awsPath}${queryString ? '?' + queryString : ''}`;
  console.log(`[PROXY] ${method} ${url} | body: ${JSON.stringify(body)?.substring(0, 120)}`);

  const options: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
    ...(body ? { body: JSON.stringify(body) } : {}),
  };

  const res = await fetch(url, options);
  const text = await res.text();

  let data: any;
  try {
    data = JSON.parse(text);
  } catch {
    data = { error: text };
  }

  console.log(`[PROXY] Response ${res.status}: ${JSON.stringify(data)?.substring(0, 200)}`);

  // AWS Lambda wraps the real response in a statusCode + body envelope
  // when proxied through API Gateway. Unwrap it.
  if (data && typeof data.statusCode === 'number' && typeof data.body === 'string') {
    try {
      return { status: data.statusCode, data: JSON.parse(data.body) };
    } catch {
      return { status: data.statusCode, data: { raw: data.body } };
    }
  }

  return { status: res.status, data };
}

// ─────────────────────────────────────────────────────────────────────
// HEALTH CHECK
// ─────────────────────────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', backend: 'AWS Bedrock', gateway: AWS_API_BASE });
});

// ─────────────────────────────────────────────────────────────────────
// CREATOR ASSISTANT CHAT  →  insight_engine Lambda (Bedrock Nova Lite)
// Payload from frontend: { message: string, history: [...] }
// Lambda expects:        { message: string }
// ─────────────────────────────────────────────────────────────────────
app.post('/api/chat', async (req, res) => {
  try {
    const { message, history } = req.body;
    if (!message) return res.status(400).json({ error: 'message is required' });

    const { status, data } = await forwardToAWS('/api/chat', 'POST', { message, history });
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[CHAT] Error:', err.message);
    res.status(502).json({ error: 'Chat service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// SUMMARY NODE  →  content_enhancer Lambda (Bedrock Nova Lite)
// Payload from frontend: { contents: string[] }
// Lambda expects:        { trends: [{topic: string}] }
// ─────────────────────────────────────────────────────────────────────
app.post('/api/summarize', async (req, res) => {
  try {
    const { contents } = req.body;
    if (!contents || !Array.isArray(contents) || contents.length === 0) {
      return res.status(400).json({ error: 'contents array is required' });
    }

    // Transform frontend's contents[] into the Lambda's expected trends[] format
    const trends = contents.map(c => ({ topic: String(c) }));
    const { status, data } = await forwardToAWS('/api/summarize', 'POST', { trends });
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[SUMMARIZE] Error:', err.message);
    res.status(502).json({ error: 'Summarize service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// AI NOTE / IDEA GENERATION  →  idea_generator Lambda
// Payload from frontend: { prompt: string }
// Lambda expects:        { niche: string, platform: string }
// ─────────────────────────────────────────────────────────────────────
app.post('/api/generate', async (req, res) => {
  try {
    const { prompt } = req.body;
    // Map the generic prompt to idea_generator's expected fields
    const { status, data } = await forwardToAWS('/api/generate', 'POST', {
      niche: prompt || 'Software Engineering',
      platform: 'YouTube',
      creator_id: 'techwithtim',
    });
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[GENERATE] Error:', err.message);
    res.status(502).json({ error: 'Generate service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// POSTS (History page)  →  content_ingestion Lambda
// ─────────────────────────────────────────────────────────────────────
app.get('/api/posts', async (_req, res) => {
  try {
    const { status, data } = await forwardToAWS('/api/posts', 'GET');
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[POSTS] Error:', err.message);
    res.status(502).json({ error: 'Posts service unavailable: ' + err.message });
  }
});

app.post('/api/posts', async (req, res) => {
  try {
    const { status, data } = await forwardToAWS('/api/posts', 'POST', req.body);
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[POSTS POST] Error:', err.message);
    res.status(502).json({ error: 'Posts service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// PROFILE  →  insight_engine Lambda  (GET /profile)
// ─────────────────────────────────────────────────────────────────────
app.get('/api/profile', async (_req, res) => {
  try {
    const { status, data } = await forwardToAWS('/api/profile', 'GET');
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[PROFILE] Error:', err.message);
    res.status(502).json({ error: 'Profile service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// ANALYZE  →  insight_engine Lambda  (POST /analyze)
// ─────────────────────────────────────────────────────────────────────
app.post('/api/analyze', async (req, res) => {
  try {
    const { status, data } = await forwardToAWS('/api/analyze', 'POST', req.body);
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[ANALYZE] Error:', err.message);
    res.status(502).json({ error: 'Analyze service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// PREDICT  →  prediction_api Lambda (SageMaker / scoring)
// ─────────────────────────────────────────────────────────────────────
app.post('/api/predict', async (req, res) => {
  try {
    const { status, data } = await forwardToAWS('/api/predict', 'POST', req.body);
    res.status(status).json(data);
  } catch (err: any) {
    console.error('[PREDICT] Error:', err.message);
    res.status(502).json({ error: 'Predict service unavailable: ' + err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────
// START
// ─────────────────────────────────────────────────────────────────────
app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n✅ Creator Intelligence API Server (AWS Bedrock Mode)`);
  console.log(`   Listening: http://localhost:${PORT}`);
  console.log(`   Backend:   ${AWS_API_BASE}`);
  console.log(`\nRoutes:`);
  console.log(`  POST /api/chat      -> insight_engine (Bedrock Nova Lite)`);
  console.log(`  POST /api/summarize -> content_enhancer (Bedrock Nova Lite)`);
  console.log(`  POST /api/generate  -> idea_generator (Titan + Nova Lite)`);
  console.log(`  GET  /api/posts     -> content_ingestion`);
  console.log(`  GET  /api/profile   -> insight_engine`);
  console.log(`  POST /api/predict   -> prediction_api`);
});
