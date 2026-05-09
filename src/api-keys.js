/**
 * API Key Management for multi-user resale.
 * 
 * Features:
 *   - Generate unique API keys (sk-xxxx format)
 *   - Per-key rate limiting with configurable time windows
 *   - Usage tracking per key
 *   - Enable/disable keys
 *   - Persistent storage in api-keys.json
 */

import { randomUUID, randomBytes } from 'crypto';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import { log } from './config.js';

const KEYS_FILE = join(process.env.DATA_DIR || process.cwd(), 'api-keys.json');

// In-memory store
const apiKeys = [];

// ─── Persistence ──────────────────────────────────────────

function saveKeys() {
  try {
    const data = apiKeys.map(k => ({
      id: k.id,
      key: k.key,
      label: k.label,
      status: k.status,
      rateLimit: k.rateLimit,
      windowHours: k.windowHours,
      createdAt: k.createdAt,
      expiresAt: k.expiresAt,
      totalRequests: k.totalRequests,
      lastUsed: k.lastUsed,
    }));
    writeFileSync(KEYS_FILE, JSON.stringify(data, null, 2));
  } catch (e) {
    log.error('Failed to save API keys:', e.message);
  }
}

function loadKeys() {
  try {
    if (!existsSync(KEYS_FILE)) return;
    const data = JSON.parse(readFileSync(KEYS_FILE, 'utf-8'));
    for (const k of data) {
      if (apiKeys.find(x => x.key === k.key)) continue;
      apiKeys.push({
        ...k,
        _windowHistory: [],
      });
    }
    if (data.length > 0) log.info(`Loaded ${data.length} API key(s) from disk`);
  } catch (e) {
    log.error('Failed to load API keys:', e.message);
  }
}

// ─── Key Generation ───────────────────────────────────────

function generateKey() {
  return 'sk-' + randomBytes(24).toString('hex');
}

// ─── CRUD ─────────────────────────────────────────────────

/**
 * Create a new API key.
 * @param {Object} opts
 * @param {string} opts.label - Human-readable name (e.g., "Cliente João")
 * @param {number} opts.rateLimit - Max requests per window (e.g., 100)
 * @param {number} opts.windowHours - Time window in hours (e.g., 24)
 * @param {string} opts.expiresAt - Optional ISO date string for expiration
 */
export function createApiKey({ label = '', rateLimit = 100, windowHours = 24, expiresAt = null } = {}) {
  const key = {
    id: randomUUID().slice(0, 8),
    key: generateKey(),
    label: label || `Key-${apiKeys.length + 1}`,
    status: 'active',
    rateLimit,
    windowHours,
    createdAt: Date.now(),
    expiresAt: expiresAt ? new Date(expiresAt).getTime() : null,
    totalRequests: 0,
    lastUsed: null,
    _windowHistory: [],
  };
  apiKeys.push(key);
  saveKeys();
  log.info(`API key created: ${key.id} (${key.label}) limit=${rateLimit}/${windowHours}h`);
  return { id: key.id, key: key.key, label: key.label, rateLimit, windowHours };
}

/**
 * List all API keys (without exposing full key to dashboard).
 */
export function listApiKeys() {
  const now = Date.now();
  return apiKeys.map(k => {
    pruneWindowHistory(k, now);
    return {
      id: k.id,
      key: k.key.slice(0, 8) + '...' + k.key.slice(-4),
      fullKey: k.key,
      label: k.label,
      status: k.status,
      rateLimit: k.rateLimit,
      windowHours: k.windowHours,
      createdAt: k.createdAt,
      expiresAt: k.expiresAt,
      totalRequests: k.totalRequests,
      windowRequests: k._windowHistory.length,
      lastUsed: k.lastUsed,
      expired: k.expiresAt ? k.expiresAt < now : false,
    };
  });
}

/**
 * Get a key by ID.
 */
export function getApiKeyById(id) {
  return apiKeys.find(k => k.id === id);
}

/**
 * Update a key's settings.
 */
export function updateApiKey(id, { label, rateLimit, windowHours, status, expiresAt } = {}) {
  const key = apiKeys.find(k => k.id === id);
  if (!key) return null;
  if (label !== undefined) key.label = label;
  if (rateLimit !== undefined) key.rateLimit = rateLimit;
  if (windowHours !== undefined) key.windowHours = windowHours;
  if (status !== undefined) key.status = status;
  if (expiresAt !== undefined) key.expiresAt = expiresAt ? new Date(expiresAt).getTime() : null;
  saveKeys();
  log.info(`API key updated: ${key.id} (${key.label})`);
  return key;
}

/**
 * Delete a key by ID.
 */
export function deleteApiKey(id) {
  const idx = apiKeys.findIndex(k => k.id === id);
  if (idx === -1) return false;
  const removed = apiKeys.splice(idx, 1)[0];
  saveKeys();
  log.info(`API key deleted: ${removed.id} (${removed.label})`);
  return true;
}

/**
 * Revoke (disable) a key.
 */
export function revokeApiKey(id) {
  return updateApiKey(id, { status: 'disabled' });
}

// ─── Rate Limiting ────────────────────────────────────────

function pruneWindowHistory(key, now) {
  if (!key._windowHistory) key._windowHistory = [];
  const windowMs = (key.windowHours || 24) * 60 * 60 * 1000;
  const cutoff = now - windowMs;
  while (key._windowHistory.length && key._windowHistory[0] < cutoff) {
    key._windowHistory.shift();
  }
  return key._windowHistory.length;
}

/**
 * Validate an incoming API key and check rate limits.
 * Returns: { valid, key, error, retryAfter }
 */
export function validateAndTrack(bearerToken) {
  if (!bearerToken) return { valid: false, error: 'API key required' };

  // Check if it's the master key (backward compat with DASHBOARD_PASSWORD or direct env)
  const masterKey = process.env.API_KEY || '';
  if (masterKey && bearerToken === masterKey) {
    return { valid: true, key: { id: 'master', label: 'Master Key', isMaster: true } };
  }

  const key = apiKeys.find(k => k.key === bearerToken);
  if (!key) return { valid: false, error: 'Invalid API key' };
  if (key.status !== 'active') return { valid: false, error: 'API key is disabled' };

  const now = Date.now();

  // Check expiration
  if (key.expiresAt && key.expiresAt < now) {
    key.status = 'expired';
    saveKeys();
    return { valid: false, error: 'API key has expired' };
  }

  // Check rate limit
  const used = pruneWindowHistory(key, now);
  if (used >= key.rateLimit) {
    const oldestInWindow = key._windowHistory[0];
    const windowMs = (key.windowHours || 24) * 60 * 60 * 1000;
    const retryAfterMs = (oldestInWindow + windowMs) - now;
    const retryAfterSecs = Math.ceil(retryAfterMs / 1000);
    return {
      valid: false,
      error: `Rate limit exceeded: ${used}/${key.rateLimit} requests in ${key.windowHours}h window`,
      retryAfter: retryAfterSecs,
      key: { id: key.id, label: key.label },
    };
  }

  // Track usage
  key._windowHistory.push(now);
  key.totalRequests++;
  key.lastUsed = now;

  // Persist periodically (every 50 requests to avoid disk thrash)
  if (key.totalRequests % 50 === 0) saveKeys();

  return { valid: true, key: { id: key.id, label: key.label } };
}

/**
 * Get usage stats for a specific key.
 */
export function getKeyUsageStats(id) {
  const key = apiKeys.find(k => k.id === id);
  if (!key) return null;
  const now = Date.now();
  pruneWindowHistory(key, now);
  return {
    id: key.id,
    label: key.label,
    totalRequests: key.totalRequests,
    windowRequests: key._windowHistory.length,
    rateLimit: key.rateLimit,
    windowHours: key.windowHours,
    remaining: Math.max(0, key.rateLimit - key._windowHistory.length),
    lastUsed: key.lastUsed,
  };
}

// ─── Init ─────────────────────────────────────────────────

export function initApiKeys() {
  loadKeys();
  // Auto-save every 5 minutes to persist usage counters
  setInterval(() => {
    saveKeys();
  }, 5 * 60 * 1000).unref?.();
}

/**
 * Check if there are any API keys configured (master or user keys).
 * If none exist, the API is open access.
 */
export function hasAnyKeys() {
  const masterKey = process.env.API_KEY || '';
  return masterKey.length > 0 || apiKeys.length > 0;
}
