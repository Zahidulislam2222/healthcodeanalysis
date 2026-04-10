/**
 * AskMe Assistant — Cloudflare Worker v3
 *
 * Proxies chat to Dialogflow ES for greetings/chitchat.
 * Handles all content questions by querying the WordPress REST API on demand.
 * Scales to any number of posts — fetches only what's needed per request.
 *
 * Secrets (set via `npx wrangler secret put <NAME>`):
 *   GOOGLE_PRIVATE_KEY, GOOGLE_CLIENT_EMAIL, DIALOGFLOW_PROJECT
 */

const WP_API = "https://healthcodeanalysis.com/wp-json/wp/v2";
const MAX_QUERY = 500;
const MAX_SESSION = 50;
const DEFAULT_COUNT = 3;
const MAX_COUNT = 10;
const CATEGORY_CACHE_TTL = 1800000; // 30 min — categories rarely change

// Lightweight caches (only small metadata, not post content)
let categoryCache = { data: [], fetchedAt: 0 };
let cachedToken = null;
let tokenExpiresAt = 0;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

// ==========================================================================
// Entry
// ==========================================================================
export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS });
    }
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    try {
      const body = await request.json();
      const query = (body.query || "").trim().slice(0, MAX_QUERY);
      const sessionId = (body.sessionId || "default")
        .slice(0, MAX_SESSION)
        .replace(/[^a-zA-Z0-9_-]/g, "");

      if (!query) {
        return json({ queryResult: { fulfillmentText: "Please type a message." } });
      }

      // Classify intent via Dialogflow
      const token = await getAccessToken(env);
      const dfData = await callDialogflow(env, token, query, sessionId);
      const intent = dfData.queryResult?.intent?.displayName || "";

      // If it's chitchat, let Dialogflow respond
      if (isChitchat(intent)) {
        return json(dfData);
      }

      // Otherwise, handle as a content question against WordPress
      const answer = await handleContent(query, intent);
      dfData.queryResult.fulfillmentText = answer;
      return json(dfData);
    } catch (e) {
      console.error("Worker error:", e.message, e.stack);
      return json({
        queryResult: {
          fulfillmentText: "Sorry, something went wrong. Please try again.",
        },
      });
    }
  },
};

// ==========================================================================
// Content Router — decides what to fetch from WordPress
// ==========================================================================
async function handleContent(query, intent) {
  const input = query.toLowerCase().trim();
  const count = parseCount(input);

  // Latest / Recent
  if (matches(input, ["latest", "newest", "recent", "new post", "new article", "what's new", "just published"])) {
    return fetchLatest(count);
  }

  // Popular / Featured / Top
  if (matches(input, ["popular", "trending", "top post", "best post", "top article", "best article", "most read", "featured"])) {
    return fetchFeatured(count);
  }

  // Category list
  if (matches(input, ["all categor", "list categor", "what categor", "show categor", "your categor", "topics", "sections", "what do you cover", "what do you write"])) {
    return fetchCategoryList();
  }

  // Posts in a specific category
  const cat = await findCategory(input);
  if (cat && matches(input, ["post", "article", "show", "list", "from", "in", "categor"])) {
    return fetchByCategory(cat, count);
  }

  // Content search — "what is X", "tell me about X", or anything Dialogflow didn't understand
  const term = cleanQuery(query);
  if (term.length >= 2) {
    return searchAndAnswer(term, cat);
  }

  return "I'm not sure what you're looking for. You can ask about our articles, browse categories, or search for a topic.";
}

// ==========================================================================
// WordPress Fetchers — query on demand, fetch only what's needed
// ==========================================================================

async function fetchLatest(count) {
  const posts = await wpGet(`/posts?per_page=${count}&orderby=date&order=desc&_fields=title,link,excerpt`);
  if (!posts || posts.length === 0) return "No posts found. Check back soon!";
  return formatList(posts, `Here are the ${posts.length} latest posts:`);
}

async function fetchFeatured(count) {
  // Fetch a larger pool, pick random to simulate "featured"
  // When sticky posts or a popularity plugin exist, this can be swapped
  const pool = await wpGet(`/posts?per_page=20&_fields=title,link,excerpt`);
  if (!pool || pool.length === 0) return "No posts found yet.";
  shuffle(pool);
  return formatList(pool.slice(0, count), `Here are ${Math.min(count, pool.length)} featured articles:`);
}

async function fetchCategoryList() {
  const cats = await getCategories();
  const visible = cats.filter((c) => c.count > 0 && c.slug !== "uncategorized");
  if (visible.length === 0) return "No categories found.";

  let html = "Here are our topics:<br/><br/>";
  for (const c of visible) {
    html += `<b><a href="${esc(c.link)}" target="_blank" style="color:#0d9488">${h(c.name)}</a></b> (${c.count} articles)<br/>`;
  }
  html += "<br/>Ask me about any category to see its articles!";
  return html;
}

async function fetchByCategory(cat, count) {
  const posts = await wpGet(`/posts?categories=${cat.id}&per_page=${count}&orderby=date&order=desc&_fields=title,link,excerpt`);
  if (!posts || posts.length === 0) return `No articles in "${h(cat.name)}" yet.`;
  return formatList(posts, `Here are ${posts.length} articles in <b>${h(cat.name)}</b>:`);
}

async function searchAndAnswer(term, preferredCat) {
  const encoded = encodeURIComponent(term);

  // 1. Search posts via WordPress (MySQL handles the heavy lifting)
  const posts = await wpGet(`/posts?search=${encoded}&per_page=5&_fields=id,title,link,excerpt`);

  // 2. Also check categories for an exact match
  if (!preferredCat) {
    const cats = await wpGet(`/categories?search=${encoded}&_fields=id,name,link,count`);
    const exact = cats?.find((c) => c.name.toLowerCase() === term.toLowerCase());
    if (exact && exact.count > 0) {
      const catPosts = await wpGet(`/posts?categories=${exact.id}&per_page=3&_fields=title,link,excerpt`);
      if (catPosts?.length > 0) {
        return formatList(catPosts, `Here are the latest articles in <b>${h(exact.name)}</b>:`);
      }
    }
  }

  if (!posts || posts.length === 0) {
    return `I couldn't find anything about "${h(term)}". Try different keywords, or ask me to show categories.`;
  }

  // 3. For the best match, fetch full content and extract a relevant snippet
  const bestId = posts[0].id;
  const snippet = await extractSnippet(bestId, term);

  let html = "";

  if (snippet) {
    const title = stripHtml(posts[0].title?.rendered || "");
    html += `From <b><a href="${esc(posts[0].link)}" target="_blank" style="color:#0d9488">${h(title)}</a></b>:<br/><br/>`;
    html += `<span style="color:#cbd5e1">${h(snippet)}</span><br/><br/>`;

    if (posts.length > 1) {
      html += "Related articles:<br/><br/>";
      html += formatListItems(posts.slice(1, 4));
    }
  } else {
    html = formatList(posts.slice(0, 3), `I found these about "${h(term)}":`);
  }

  return html;
}

// Fetch a single post's content and pull out the relevant sentence
async function extractSnippet(postId, term) {
  try {
    const post = await wpGet(`/posts/${postId}?_fields=content`);
    if (!post?.content?.rendered) return null;

    const plain = stripHtml(post.content.rendered);
    const lowerTerm = term.toLowerCase();
    const words = lowerTerm.split(/\s+/).filter((w) => w.length > 1);

    // Split into sentences
    const sentences = plain
      .split(/(?<=[.!?])\s+/)
      .filter((s) => s.length > 30 && !s.includes("{") && !s.includes("}"));

    let best = null;
    let bestScore = 0;

    for (const s of sentences) {
      const lower = s.toLowerCase();
      let score = 0;
      if (lower.includes(lowerTerm)) score += 100;
      for (const w of words) {
        if (lower.includes(w)) score += 10;
      }
      if (score > bestScore) {
        bestScore = score;
        best = s;
      }
    }

    if (!best || bestScore < 10) return null;
    return best.length > 280 ? best.slice(0, 280) + "..." : best;
  } catch {
    return null;
  }
}

// ==========================================================================
// Category Cache — only metadata, very small
// ==========================================================================
async function getCategories() {
  const now = Date.now();
  if (categoryCache.data.length > 0 && now - categoryCache.fetchedAt < CATEGORY_CACHE_TTL) {
    return categoryCache.data;
  }

  const cats = await wpGet("/categories?per_page=100&_fields=id,name,slug,count,link");
  if (cats && cats.length > 0) {
    categoryCache = {
      data: cats.map((c) => ({ ...c, name: stripHtml(c.name) })),
      fetchedAt: now,
    };
  }
  return categoryCache.data;
}

async function findCategory(input) {
  const cats = await getCategories();
  for (const cat of cats) {
    if (cat.slug === "uncategorized") continue;
    const nameLower = cat.name.toLowerCase();
    const slugSpaced = cat.slug.replace(/-/g, " ");
    if (input.includes(nameLower) || input.includes(cat.slug) || input.includes(slugSpaced)) {
      return cat;
    }
  }
  return null;
}

// ==========================================================================
// WordPress REST API helper
// ==========================================================================
async function wpGet(endpoint) {
  try {
    const resp = await fetch(`${WP_API}${endpoint}`);
    if (!resp.ok) return null;
    return resp.json();
  } catch {
    return null;
  }
}

// ==========================================================================
// Dialogflow
// ==========================================================================
const CHITCHAT = new Set([
  "Default Welcome Intent",
  "Goodbye",
  "Thanks",
  "Help",
  "Who are you",
  "About Site",
]);

function isChitchat(intent) {
  return CHITCHAT.has(intent);
}

async function callDialogflow(env, token, query, sessionId) {
  const url = `https://dialogflow.googleapis.com/v2/projects/${env.DIALOGFLOW_PROJECT}/agent/sessions/${sessionId}:detectIntent`;
  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        queryInput: { text: { text: query, languageCode: "en" } },
      }),
    });
    if (!resp.ok) {
      return { queryResult: { intent: { displayName: "" }, fulfillmentText: "" } };
    }
    return resp.json();
  } catch {
    return { queryResult: { intent: { displayName: "" }, fulfillmentText: "" } };
  }
}

// ==========================================================================
// Formatting & Utilities
// ==========================================================================
function formatList(posts, intro) {
  if (!posts?.length) return "No results found.";
  return intro + "<br/><br/>" + formatListItems(posts);
}

function formatListItems(posts) {
  let html = "";
  for (const p of posts) {
    const title = h(stripHtml(p.title?.rendered || "Untitled"));
    const link = esc(p.link || "#");
    html += `<a href="${link}" target="_blank" style="color:#0d9488;font-weight:bold">${title}</a><br/>`;
    if (p.excerpt?.rendered) {
      let exc = stripHtml(p.excerpt.rendered).replace(/\[&hellip;\]/, "...").trim();
      if (exc.length > 100) exc = exc.slice(0, 100) + "...";
      html += `<span style="font-size:13px;color:#94a3b8">${h(exc)}</span><br/>`;
    }
    html += "<br/>";
  }
  return html;
}

function parseCount(input) {
  const m = input.match(/\b(\d{1,2})\b/);
  if (m) {
    const n = parseInt(m[1], 10);
    if (n >= 1 && n <= MAX_COUNT) return n;
  }
  return DEFAULT_COUNT;
}

function matches(input, keywords) {
  return keywords.some((k) => input.includes(k));
}

function cleanQuery(text) {
  let c = text.toLowerCase();
  const prefixes = [
    "go to", "show me", "search for", "find me", "find", "look for",
    "what is", "what are", "what's", "where is", "how to", "how does",
    "tell me about", "tell me", "explain", "describe",
    "i want to know about", "do you have", "any article on",
    "any post about", "any articles about",
  ];
  for (const p of prefixes) {
    if (c.startsWith(p)) { c = c.slice(p.length); break; }
  }
  const stops = [" the ", " a ", " an ", " post", " posts", " page", " pages", " article", " articles", " please"];
  for (const s of stops) c = c.replaceAll(s, " ");
  return c.replace(/[?!.]/g, "").replace(/\s+/g, " ").trim();
}

function stripHtml(html) {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#8217;/g, "'")
    .replace(/&#8220;/g, '"').replace(/&#8221;/g, '"').replace(/&#8211;/g, "-")
    .replace(/&#038;/g, "&").replace(/&hellip;/g, "...").replace(/&#\d+;/g, "")
    .replace(/\s+/g, " ").trim();
}

function h(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function esc(s) { return s.replace(/"/g, "&quot;").replace(/'/g, "&#39;"); }
function json(data) { return new Response(JSON.stringify(data), { headers: { "Content-Type": "application/json", ...CORS } }); }
function shuffle(arr) { for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; } }

// ==========================================================================
// Google OAuth — JWT + token caching
// ==========================================================================
async function getAccessToken(env) {
  const now = Math.floor(Date.now() / 1000);
  if (cachedToken && now < tokenExpiresAt - 300) return cachedToken;

  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = btoa(JSON.stringify({
    iss: env.GOOGLE_CLIENT_EMAIL,
    scope: "https://www.googleapis.com/auth/cloud-platform",
    aud: "https://oauth2.googleapis.com/token",
    exp: now + 3600, iat: now,
  }));

  const input = `${header}.${claim}`;
  const rawKey = env.GOOGLE_PRIVATE_KEY;
  const pem = rawKey
    .replace(/-----BEGIN PRIVATE KEY-----/g, "")
    .replace(/-----END PRIVATE KEY-----/g, "")
    .replace(/\\n/g, "")
    .replace(/\n/g, "")
    .replace(/\r/g, "")
    .replace(/\s/g, "");

  const keyBytes = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  const key = await crypto.subtle.importKey("pkcs8", keyBytes.buffer, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(input));
  const encodedSig = btoa(String.fromCharCode(...new Uint8Array(sig))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${input}.${encodedSig}`,
  });

  const data = await resp.json();
  if (!data.access_token) throw new Error("Google auth failed");

  cachedToken = data.access_token;
  tokenExpiresAt = now + (data.expires_in || 3600);
  return cachedToken;
}
