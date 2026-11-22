/**
 * Vercel Serverless Function: /api/genie-stop
 *
 * Belt-and-suspenders emergency stop endpoint invoked via navigator.sendBeacon
 * on tab close / unload alongside browser-side `await session.complete()`.
 * Calls POST /v1beta/interactions/{id}/cancel to halt server-side billing.
 */

const crypto = require('node:crypto');

const GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta';
const INTERACTION_ID_RE = /^[A-Za-z0-9_.-]{4,128}$/;

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

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return sendJson(res, 405, { error: 'Method not allowed. Use POST.' });
  }

  const isVercelProd = process.env.VERCEL_ENV === 'production' || Boolean(process.env.VERCEL);
  if (isVercelProd && process.env.GENIE_ENABLE_PROD !== 'true') {
    return sendJson(res, 503, {
      stopped: false,
      comingSoon: true,
      error: 'Commander Pip Genie 4 World is disabled in production (Coming Soon).',
    });
  }

  let body;
  try {
    body = await parseJsonBody(req);
  } catch {
    return sendJson(res, 400, { error: 'Invalid JSON request body.' });
  }

  const interactionId = typeof body.interactionId === 'string' ? body.interactionId.trim() : '';
  if (!INTERACTION_ID_RE.test(interactionId)) {
    return sendJson(res, 400, { error: 'Invalid or missing interactionId.' });
  }

  const userApiKey = typeof body.userApiKey === 'string' ? body.userApiKey.trim() : '';
  const passcode = typeof body.passcode === 'string' ? body.passcode.trim() : '';
  const accessCode = process.env.GENIE_ACCESS_CODE || '';

  let apiKey = '';
  if (userApiKey) {
    apiKey = userApiKey;
  } else {
    const serverKey = (process.env.GEMINI_API_KEY || '').trim();
    if (!serverKey) return sendJson(res, 503, { error: 'Server key not configured.' });
    if (isVercelProd && !accessCode) return sendJson(res, 403, { error: 'Access code required in production.' });
    if (accessCode && !safeEqual(passcode, accessCode)) return sendJson(res, 401, { error: 'Unauthorized.' });
    apiKey = serverKey;
  }

  try {
    const response = await fetch(
      `${GEMINI_API_BASE}/interactions/${encodeURIComponent(interactionId)}/cancel`,
      {
        method: 'POST',
        headers: {
          'x-goog-api-key': apiKey,
          'Content-Type': 'application/json',
        },
        body: '{}',
      }
    );
    return sendJson(res, response.ok ? 200 : response.status, {
      stopped: response.ok,
      interactionId,
    });
  } catch (err) {
    return sendJson(res, 502, {
      stopped: false,
      error: err.message || 'Failed to cancel interaction.',
    });
  }
};
