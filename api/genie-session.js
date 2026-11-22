/**
 * Vercel Serverless Function: /api/genie-session
 *
 * Mints a single-session ephemeral Genie 4 auth token so a long-lived
 * GEMINI_API_KEY never enters client-side browser code.
 *
 * Security / cost guardrails:
 * - GET returns capability flags only (never secrets).
 * - POST accepts either:
 *   1. Server key mode (process.env.GEMINI_API_KEY), gated by
 *      process.env.GENIE_ACCESS_CODE whenever configured or in Vercel production.
 *   2. Stateless BYOK mode (body.userApiKey), used strictly for this request
 *      to mint a single-session ephemeral auth_token and never logged or stored.
 */

const crypto = require('node:crypto');

const GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta';
const MODEL_ID = 'genie-4';

function safeEqual(a, b) {
  const bufA = Buffer.from(String(a || ''), 'utf8');
  const bufB = Buffer.from(String(b || ''), 'utf8');
  if (bufA.length !== bufB.length || bufA.length === 0) return false;
  return crypto.timingSafeEqual(bufA, bufB);
}

function sendJson(res, status, payload) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(payload));
}

async function parseJsonBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string' && req.body.trim()) {
    return JSON.parse(req.body);
  }
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8').trim();
  if (!raw) return {};
  return JSON.parse(raw);
}

function extractGeminiError(data, fallback) {
  const first = Array.isArray(data) ? data[0] : data;
  if (first && typeof first === 'object') {
    return first?.error?.message || first?.message || fallback;
  }
  return fallback;
}

async function callGeminiPost(path, apiKey, payload) {
  const response = await fetch(`${GEMINI_API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'x-goog-api-key': apiKey,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!response.ok) {
    const detail = extractGeminiError(data, `HTTP ${response.status}`);
    const err = new Error(detail);
    err.status = response.status;
    throw err;
  }
  return data;
}

module.exports = async function handler(req, res) {
  const hasServerKey = Boolean((process.env.GEMINI_API_KEY || '').trim());
  const accessCode = process.env.GENIE_ACCESS_CODE || '';
  const isVercelProd = process.env.VERCEL_ENV === 'production' || Boolean(process.env.VERCEL);
  const prodEnabled = process.env.GENIE_ENABLE_PROD === 'true';
  const comingSoonLocked = isVercelProd && !prodEnabled;
  const serverKeyAvailable = !comingSoonLocked && hasServerKey && (!isVercelProd || Boolean(accessCode));

  if (req.method === 'GET') {
    return sendJson(res, 200, {
      model: MODEL_ID,
      apiVersion: 'v1beta',
      comingSoon: comingSoonLocked,
      serverKeyConfigured: serverKeyAvailable,
      requiresPasscode: Boolean(accessCode) || isVercelProd,
      acceptsByok: !comingSoonLocked,
      estimatedCostPerSecUsd: 0.10,
      defaultDurationSec: 20,
      maxDurationSec: 90,
      hardLimitSec: 120,
    });
  }

  if (comingSoonLocked) {
    return sendJson(res, 503, {
      comingSoon: true,
      error: 'Commander Pip Genie 4 World is currently under construction (Coming Soon). Live outputs are disabled in production during exploratory R&D.',
    });
  }

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'GET, POST');
    return sendJson(res, 405, { error: 'Method not allowed. Use GET or POST.' });
  }

  let body;
  try {
    body = await parseJsonBody(req);
  } catch {
    return sendJson(res, 400, { error: 'Invalid JSON request body.' });
  }

  const userApiKey = typeof body.userApiKey === 'string' ? body.userApiKey.trim() : '';
  const passcode = typeof body.passcode === 'string' ? body.passcode.trim() : '';

  let apiKey = '';
  let authMode = 'byok';

  if (userApiKey) {
    apiKey = userApiKey;
    authMode = 'byok';
  } else {
    const serverKey = (process.env.GEMINI_API_KEY || '').trim();
    if (!serverKey) {
      return sendJson(res, 503, {
        error: 'Server GEMINI_API_KEY is not configured. Provide your own paid-tier Gemini API key (BYOK) or open Genie 4 in Google AI Studio.',
      });
    }
    if (isVercelProd && !accessCode) {
      return sendJson(res, 403, {
        error: 'Production passcode guard is active: set GENIE_ACCESS_CODE in Vercel env vars for demo access, or enter your own paid-tier Gemini API key (BYOK).',
      });
    }
    if (accessCode && !safeEqual(passcode, accessCode)) {
      return sendJson(res, 401, {
        error: 'Invalid or missing demo passcode. Enter the invite passcode or use your own paid-tier Gemini API key (BYOK).',
      });
    }
    apiKey = serverKey;
    authMode = 'server';
  }

  try {
    // Step 1: Create Genie 4 interaction on v1beta
    const interaction = await callGeminiPost('/interactions', apiKey, {
      model: MODEL_ID,
    });
    if (!interaction?.id) {
      throw new Error('Gemini Interactions API did not return an interaction id.');
    }

    // Step 2: Mint single-session ephemeral auth_token scoped to this interaction
    const tokenResp = await callGeminiPost(
      `/interactions/${encodeURIComponent(interaction.id)}/auth_tokens`,
      apiKey,
      {}
    );
    if (!tokenResp?.auth_token) {
      throw new Error('Gemini Interactions API did not return an ephemeral auth_token.');
    }

    return sendJson(res, 200, {
      interactionId: interaction.id,
      authToken: tokenResp.auth_token,
      model: MODEL_ID,
      apiVersion: 'v1beta',
      authMode,
    });
  } catch (err) {
    const status = err.status && err.status >= 400 && err.status < 600 ? err.status : 502;
    let hint = '';
    if (status === 400 || status === 403 || status === 429) {
      hint = ' Note: genie-4 requires a paid-tier Gemini API key with billing enabled.';
    }
    return sendJson(res, status, {
      error: `${err.message || 'Failed to initialize Genie 4 session.'}${hint}`,
    });
  }
};
