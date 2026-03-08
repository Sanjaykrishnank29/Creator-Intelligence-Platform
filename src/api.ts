/**
 * API configuration for the Creator Intelligence Platform.
 * 
 * In production (CloudFront), the frontend calls AWS API Gateway directly.
 * In development, Vite proxy routes /api/* to localhost:8000 (Express server).
 */

// Detect production by checking if we're NOT on localhost
const IS_PRODUCTION = typeof window !== 'undefined' && !window.location.hostname.includes('localhost');

export const AWS_API_BASE = 'https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod';

/**
 * Build the correct API URL — direct to AWS in production, relative in dev.
 */
export function apiUrl(path: string): string {
  return IS_PRODUCTION ? `${AWS_API_BASE}${path}` : path;
}

/**
 * Standard fetch wrapper that handles the AWS API Gateway response envelope.
 * Lambda returns { statusCode, headers, body } — this unwraps it automatically.
 */
export async function apiFetch(path: string, options: RequestInit = {}): Promise<any> {
  const url = apiUrl(path);
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

  const res = await fetch(url, { ...options, headers });
  const text = await res.text();

  let data: any;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Non-JSON response from ${path}: ${text.substring(0, 200)}`);
  }

  // Unwrap AWS Lambda API Gateway envelope when present
  if (data && typeof data.statusCode === 'number' && typeof data.body === 'string') {
    try {
      return JSON.parse(data.body);
    } catch {
      return { raw: data.body };
    }
  }

  return data;
}
