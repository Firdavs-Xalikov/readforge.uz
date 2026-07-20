require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const path = require('path');
const fs = require('fs');
const { Pool } = require('pg');
const crypto = require('crypto');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'login.html'));
});

/* ─── CONFIG ─── */
const BAZAARLINK_KEY  = process.env.BAZAARLINK_API_KEY;
const OPENROUTER_KEY  = process.env.OPENROUTER_API_KEY;
const PORT            = process.env.PORT || 3001;
const JWT_SECRET      = process.env.JWT_SECRET || 'change-me-in-production';
const ADMIN_JWT       = process.env.JWT_SECRET + '-admin';
const BAZAARLINK_MOD  = process.env.BAZAARLINK_MODEL || 'auto:free';
const OPENROUTER_MOD  = process.env.OPENROUTER_MODEL || 'google/gemini-2.5-flash:free';
const BAZAARLINK_BASE = 'https://bazaarlink.ai/api/v1/chat/completions';
const OPENROUTER_BASE = 'https://openrouter.ai/api/v1/chat/completions';

if (!BAZAARLINK_KEY) {
  console.warn('\n⚠️  No BazaarLink API key found in environment variables\n');
}
if (!OPENROUTER_KEY) {
  console.warn('\n⚠️  No OpenRouter API key found in environment variables\n');
}

/* ─── DATABASE ─── */
const databaseUrl = process.env.DATABASE_URL;
let db;
let sqliteDb;

if (!databaseUrl) {
  console.log('\n💡  No DATABASE_URL found in environment variables. Falling back to SQLite local database.\n');
  const Database = require('better-sqlite3');
  sqliteDb = new Database(path.join(__dirname, 'readforge.db'));
  sqliteDb.pragma('journal_mode = WAL');

  db = {
    query: async (text, params = []) => {
      // Convert Postgres-style parameters ($1, $2, ...) to SQLite (?)
      const sql = text.replace(/\$\d+/g, '?');
      const lowerSql = sql.trim().toLowerCase();
      const isSelect = lowerSql.startsWith('select') || lowerSql.includes(' returning');

      try {
        const stmt = sqliteDb.prepare(sql);
        if (isSelect) {
          const rows = stmt.all(...params);
          return { rows, rowCount: rows.length };
        } else {
          const info = stmt.run(...params);
          return { rows: [], rowCount: info.changes };
        }
      } catch (err) {
        throw err;
      }
    }
  };
} else {
  const pool = new Pool({
    connectionString: databaseUrl,
    ssl: databaseUrl.includes('localhost') || databaseUrl.includes('127.0.0.1')
      ? false
      : { rejectUnauthorized: false }
  });

  db = {
    query: (text, params) => pool.query(text, params)
  };
}

// Database schema initialization
const initDb = async () => {
  if (!databaseUrl) {
    // Initialize SQLite tables
    sqliteDb.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        surname     TEXT NOT NULL,
        email       TEXT NOT NULL UNIQUE,
        password    TEXT NOT NULL,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS generations (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        type        TEXT NOT NULL,
        topic       TEXT,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS saved_articles (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title       TEXT NOT NULL,
        topic       TEXT,
        content     TEXT NOT NULL,
        difficulty  TEXT,
        word_count  INTEGER,
        saved_at    TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS admins (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        email       TEXT NOT NULL UNIQUE,
        password    TEXT NOT NULL,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS saved_vocabulary (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        word        TEXT NOT NULL,
        pos         TEXT,
        ipa         TEXT,
        definition  TEXT,
        synonym     TEXT,
        example     TEXT,
        level       TEXT,
        saved_at    TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, word)
      );
    `);

    try {
      sqliteDb.prepare(`ALTER TABLE users ADD COLUMN recovery_key TEXT`).run();
    } catch (e) {
      // Column already exists, ignore
    }
    return;
  }

  // Postgres Schema Initialization
  await db.query(`
    CREATE TABLE IF NOT EXISTS users (
      id          SERIAL PRIMARY KEY,
      name        VARCHAR(255) NOT NULL,
      surname     VARCHAR(255) NOT NULL,
      email       VARCHAR(255) NOT NULL UNIQUE,
      password    VARCHAR(255) NOT NULL,
      created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS generations (
      id          SERIAL PRIMARY KEY,
      user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      type        VARCHAR(50) NOT NULL,
      topic       VARCHAR(255),
      created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS saved_articles (
      id          SERIAL PRIMARY KEY,
      user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      title       VARCHAR(255) NOT NULL,
      topic       VARCHAR(255),
      content     TEXT NOT NULL,
      difficulty  VARCHAR(50),
      word_count  INTEGER,
      saved_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS admins (
      id          SERIAL PRIMARY KEY,
      name        VARCHAR(255) NOT NULL,
      email       VARCHAR(255) NOT NULL UNIQUE,
      password    VARCHAR(255) NOT NULL,
      created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS saved_vocabulary (
      id          SERIAL PRIMARY KEY,
      user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      word        VARCHAR(255) NOT NULL,
      pos         VARCHAR(100),
      ipa         VARCHAR(100),
      definition  TEXT,
      synonym     VARCHAR(255),
      example     TEXT,
      level       VARCHAR(50),
      saved_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(user_id, word)
    );
  `);

  await db.query(`ALTER TABLE users ADD COLUMN IF NOT EXISTS recovery_key VARCHAR(255)`);
};

/* ─── SEED ADMINS ─── */
const seedAdmins = async () => {
  try {
    let seededCount = 0;
    
    // Find all environment keys like ADMIN_1_EMAIL, ADMIN_2_EMAIL, etc.
    const keys = Object.keys(process.env).filter(key => key.match(/^ADMIN_(\d+)_EMAIL$/i));
    for (const key of keys) {
      const match = key.match(/^ADMIN_(\d+)_EMAIL$/i);
      if (match) {
        const index = match[1];
        const email = process.env[key].toLowerCase().trim();
        const password = (process.env[`ADMIN_${index}_PASSWORD`] || '').trim();
        
        if (email && password) {
          const alreadyRes = await db.query('SELECT id FROM admins WHERE email = $1', [email]);
          if (alreadyRes.rowCount === 0) {
            const hash = await bcrypt.hash(password, 10);
            await db.query('INSERT INTO admins (name, email, password) VALUES ($1, $2, $3)', [`Admin ${index}`, email, hash]);
            seededCount++;
          }
        }
      }
    }

    // Update old default fallback admin if it exists
    const oldAdminRes = await db.query('SELECT id FROM admins WHERE email = $1', ['admin@readforge.com']);
    if (oldAdminRes.rowCount > 0) {
      const newHash = await bcrypt.hash('Firdavs2009', 10);
      await db.query(
        'UPDATE admins SET name = $1, email = $2, password = $3 WHERE email = $4',
        ['Default Admin', 'fjesa@mail.ru', newHash, 'admin@readforge.com']
      );
      console.log('🔄 Updated old default admin (admin@readforge.com) to fjesa@mail.ru / Firdavs2009');
    }

    const countRes = await db.query('SELECT COUNT(*) as count FROM admins');
    let count = parseInt(countRes.rows[0].count);
    if (count === 0) {
      const email = 'fjesa@mail.ru';
      const password = 'Firdavs2009';
      const hash = await bcrypt.hash(password, 10);
      await db.query('INSERT INTO admins (name, email, password) VALUES ($1, $2, $3)', ['Default Admin', email, hash]);
      count = 1;
      console.log('💡 No admins found in environment. Seeded default fallback admin (fjesa@mail.ru / Firdavs2009)');
    }
    console.log(`✅ Loaded ${count} admin accounts in database`);

  } catch (e) {
    console.error('Error seeding admins from environment:', e.message);
  }
};

/* ─── AUTH HELPERS ─── */
function signToken(user) {
  return jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
}
function signAdminToken(admin) {
  return jwt.sign({ id: admin.id, email: admin.email, isAdmin: true }, ADMIN_JWT, { expiresIn: '12h' });
}

function authMiddleware(req, res, next) {
  const header = req.headers.authorization || '';
  const token  = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'Not authenticated' });
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid or expired token' });
  }
}

function adminMiddleware(req, res, next) {
  const header = req.headers.authorization || '';
  const token  = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'Admin not authenticated' });
  try {
    req.admin = jwt.verify(token, ADMIN_JWT);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid or expired admin token' });
  }
}

/* ─── AUTH ROUTES ─── */
app.post('/api/register', async (req, res) => {
  const { name, surname, email, password } = req.body;
  if (!name || !surname || !email || !password)
    return res.status(400).json({ error: 'All fields are required' });

  // Strict email check: must have format user@domain.tld
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email))
    return res.status(400).json({ error: 'Please enter a valid email address (e.g. you@example.com)' });

  if (password.length < 6)
    return res.status(400).json({ error: 'Password must be at least 6 characters' });

  try {
    const existsRes = await db.query('SELECT id FROM users WHERE email = $1', [email.toLowerCase().trim()]);
    if (existsRes.rowCount > 0) return res.status(409).json({ error: 'Email already registered' });

    const hash = await bcrypt.hash(password, 10);
    const recoveryKey = 'RF-' + crypto.randomBytes(4).toString('hex').toUpperCase().match(/.{1,4}/g).join('-');

    const resultRes = await db.query(
      'INSERT INTO users (name, surname, email, password, recovery_key) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [name.trim(), surname.trim(), email.toLowerCase().trim(), hash, recoveryKey]
    );

    const user = resultRes.rows[0];
    res.json({ 
      token: signToken(user), 
      user: { 
        id: user.id, 
        name: user.name, 
        surname: user.surname, 
        email: user.email, 
        recoveryKey: user.recovery_key 
      } 
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password)
    return res.status(400).json({ error: 'Email and password are required' });

  try {
    const userRes = await db.query('SELECT * FROM users WHERE email = $1', [email.toLowerCase().trim()]);
    const user = userRes.rows[0];
    if (!user) return res.status(401).json({ error: 'Invalid email or password' });

    const ok = await bcrypt.compare(password, user.password);
    if (!ok) return res.status(401).json({ error: 'Invalid email or password' });

    res.json({ token: signToken(user), user: { id: user.id, name: user.name, surname: user.surname, email: user.email } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/recover-password', async (req, res) => {
  const { email, recoveryKey, newPassword } = req.body;
  if (!email || !recoveryKey || !newPassword) {
    return res.status(400).json({ error: 'All fields are required' });
  }
  if (newPassword.length < 6) {
    return res.status(400).json({ error: 'Password must be at least 6 characters' });
  }

  try {
    const userRes = await db.query('SELECT * FROM users WHERE email = $1', [email.toLowerCase().trim()]);
    const user = userRes.rows[0];

    if (!user) {
      return res.status(404).json({ error: 'No account found with this email' });
    }

    const keyMatch = user.recovery_key && (user.recovery_key.replace(/\s+/g, '').toUpperCase() === recoveryKey.replace(/\s+/g, '').toUpperCase());
    if (!keyMatch) {
      return res.status(401).json({ error: 'Invalid recovery key' });
    }

    const hash = await bcrypt.hash(newPassword, 10);
    await db.query('UPDATE users SET password = $1 WHERE id = $2', [hash, user.id]);

    res.json({ success: true, message: 'Password updated successfully! You can now log in.' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/me', authMiddleware, async (req, res) => {
  try {
    const userRes = await db.query('SELECT id, name, surname, email, created_at FROM users WHERE id = $1', [req.user.id]);
    const user = userRes.rows[0];
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json({ user });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ─── ADMIN AUTH ─── */
app.post('/api/admin/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password)
    return res.status(400).json({ error: 'Email and password are required' });

  try {
    const adminRes = await db.query('SELECT * FROM admins WHERE email = $1', [email.toLowerCase().trim()]);
    const admin = adminRes.rows[0];
    if (!admin) return res.status(401).json({ error: 'Invalid email or password' });

    const ok = await bcrypt.compare(password, admin.password);
    if (!ok) return res.status(401).json({ error: 'Invalid email or password' });

    res.json({ token: signAdminToken(admin), admin: { id: admin.id, name: admin.name, email: admin.email } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ─── ADMIN ROUTE ─── */
app.get('/api/admin/stats', adminMiddleware, async (req, res) => {
  try {
    const totalUsersRes = await db.query('SELECT COUNT(*) as count FROM users');
    const totalUsers = parseInt(totalUsersRes.rows[0].count);

    const totalGensRes = await db.query('SELECT COUNT(*) as count FROM generations');
    const totalGens = parseInt(totalGensRes.rows[0].count);

    const usersRes = await db.query(`
      SELECT u.id, u.name, u.surname, u.email, u.created_at,
             COUNT(g.id) as generations
      FROM users u
      LEFT JOIN generations g ON g.user_id = u.id
      GROUP BY u.id
      ORDER BY u.created_at DESC
    `);

    const users = usersRes.rows.map(row => ({
      ...row,
      generations: parseInt(row.generations)
    }));

    res.json({ totalUsers, totalGenerations: totalGens, users });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ─── ADMIN MANAGEMENT ─── */
app.get('/api/admin/list', adminMiddleware, async (req, res) => {
  try {
    const adminsRes = await db.query('SELECT id, name, email, created_at FROM admins ORDER BY created_at DESC');
    res.json({ admins: adminsRes.rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/admin/create', adminMiddleware, async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) {
    return res.status(400).json({ error: 'Name, email and password are required' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return res.status(400).json({ error: 'Please enter a valid email address' });
  }
  if (password.length < 6) {
    return res.status(400).json({ error: 'Password must be at least 6 characters' });
  }

  try {
    const existsRes = await db.query('SELECT id FROM admins WHERE email = $1', [email.toLowerCase().trim()]);
    if (existsRes.rowCount > 0) {
      return res.status(409).json({ error: 'Admin email already exists' });
    }

    const hash = await bcrypt.hash(password, 10);
    await db.query(
      'INSERT INTO admins (name, email, password) VALUES ($1, $2, $3)',
      [name.trim(), email.toLowerCase().trim(), hash]
    );

    res.json({ success: true, message: 'Admin account created successfully!' });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.delete('/api/admin/delete/:id', adminMiddleware, async (req, res) => {
  // Prevent admin from deleting themselves
  if (parseInt(req.params.id) === req.admin.id) {
    return res.status(400).json({ error: 'You cannot delete your own admin account!' });
  }

  try {
    const result = await db.query('DELETE FROM admins WHERE id = $1', [req.params.id]);
    res.json({ success: result.rowCount > 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ─── AI HELPERS ─── */
async function callOpenRouter(systemPrompt, userPrompt, temperature = 0.85, maxTokens = 2000) {
  let lastError;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(OPENROUTER_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENROUTER_KEY}`,
          'HTTP-Referer': 'http://localhost:3001',
          'X-Title': 'ReadForge AI'
        },
        body: JSON.stringify({
          model: OPENROUTER_MOD,
          temperature,
          max_tokens: maxTokens,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user',   content: userPrompt   }
          ],
          response_format: { type: 'json_object' }
        })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error?.message || `OpenRouter HTTP ${res.status}`);
      }
      const result = await res.json();
      const raw = result?.choices?.[0]?.message?.content || '';
      if (!raw.trim()) {
        console.error(`[/api/article] Attempt ${attempt} returned empty content.`);
        throw new Error('Empty response from OpenRouter');
      }
      const jsonMatch = raw.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        console.error(`[/api/article] Attempt ${attempt} failed to find JSON in content. Content was:`, raw);
        console.error(`[/api/article] Attempt ${attempt} full response object:`, JSON.stringify(result));
        throw new Error('No JSON in OpenRouter response');
      }
      return JSON.parse(jsonMatch[0]);
    } catch (err) {
      console.warn(`[OpenRouter Attempt ${attempt} error]:`, err.message);
      lastError = err;
      if (attempt < 3) {
        // Wait 1 second before retrying
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }
  throw lastError;
}

async function callBazaarLink(systemPrompt, userPrompt, temperature = 0.6, maxTokens = 2000) {
  let lastError;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(BAZAARLINK_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${BAZAARLINK_KEY}`
        },
        body: JSON.stringify({
          model: BAZAARLINK_MOD,
          temperature,
          max_tokens: maxTokens,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user',   content: userPrompt   }
          ],
          response_format: { type: 'json_object' }
        })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error?.message || `BazaarLink HTTP ${res.status}`);
      }
      const result = await res.json();
      const raw = result?.choices?.[0]?.message?.content || '';
      if (!raw.trim()) {
        console.error(`[/api/quiz] Attempt ${attempt} returned empty content.`);
        throw new Error('Empty response from BazaarLink');
      }
      const jsonMatch = raw.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        console.error(`[/api/quiz] Attempt ${attempt} failed to find JSON in content. Content was:`, raw);
        console.error(`[/api/quiz] Attempt ${attempt} full response object:`, JSON.stringify(result));
        throw new Error('No JSON in BazaarLink response');
      }
      return JSON.parse(jsonMatch[0]);
    } catch (err) {
      console.warn(`[BazaarLink Attempt ${attempt} error]:`, err.message);
      lastError = err;
      if (attempt < 3) {
        // Wait 1 second before retrying
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }
  throw lastError;
}

/* ─── AI ROUTES (require login) ─── */
app.post('/api/article', authMiddleware, async (req, res) => {
  if (!OPENROUTER_KEY) {
    return res.status(500).json({ error: 'OpenRouter API key is not configured on the server. Please add it to your project environment variables.' });
  }
  const { topic } = req.body;
  if (!topic?.name) return res.status(400).json({ error: 'Missing topic' });

  const systemPrompt = `You are an expert author of English reading passages for language learners (SAT/IELTS/Academic level C1). You always respond with valid JSON only — no markdown, no extra text.`;
  const userPrompt   = `Generate a compelling, factual reading passage on the topic: "${topic.name}" — ${topic.desc}

Rules:
- Pick ONE specific, interesting real-world story, event, person, or discovery in this topic area. Make it surprising and specific.
- Write 5–6 paragraphs totaling 400–500 words. Separate each paragraph with a blank line (\\n\\n).
- Language level: C1 (advanced but clear). Writing style: journalistic and engaging.
- Include real names, dates, and numbers.

Respond ONLY with valid JSON:
{"title":"A compelling title (max 10 words)","content":"Full article. Paragraphs separated by \\n\\n","keyTakeaways":["Takeaway 1","Takeaway 2","Takeaway 3"],"difficulty":"C1"}`;

  try {
    const data = await callOpenRouter(systemPrompt, userPrompt, 0.85, 1800);
    await db.query('INSERT INTO generations (user_id, type, topic) VALUES ($1, $2, $3)', [req.user.id, 'article', topic.name]);
    res.json(data);
  } catch (e) {
    console.error('[/api/article]', e.message);
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/quiz', authMiddleware, async (req, res) => {
  if (!BAZAARLINK_KEY) {
    return res.status(500).json({ error: 'BazaarLink API key is not configured on the server. Please add it to your project environment variables.' });
  }
  const { article } = req.body;
  if (!article?.title || !article?.content) return res.status(400).json({ error: 'Missing article' });

  const systemPrompt = `You are an expert English language assessment author. You always respond with valid JSON only — no markdown, no extra text.`;
  const userPrompt   = `Based on this reading passage, generate:
1. Exactly 5 comprehension questions (mix of types: main_idea, detail, inference, vocabulary, cause_effect)
2. Exactly 6 vocabulary words from the passage (advanced B2-C1 words)

TITLE: ${article.title}
CONTENT:
${article.content}

Respond ONLY with valid JSON:
{"questions":[{"type":"main_idea","question":"Text?","choices":{"A":"...","B":"...","C":"...","D":"..."},"correct":"B","explanation":"Why (1-2 sentences)."}],"vocabulary":[{"word":"Word","pos":"noun","level":"C1","ipa":"/wɜːrd/","definition":"Clear definition.","synonym":"Similar word","example":"Sentence using the word."}]}`;

  try {
    const data = await callBazaarLink(systemPrompt, userPrompt, 0.6, 2500);
    await db.query('INSERT INTO generations (user_id, type, topic) VALUES ($1, $2, $3)', [req.user.id, 'quiz', article.title]);
    res.json(data);
  } catch (e) {
    console.error('[/api/quiz]', e.message);
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/translate', authMiddleware, async (req, res) => {
  if (!OPENROUTER_KEY) {
    return res.status(500).json({ error: 'OpenRouter API key is not configured on the server. Please add it to your project environment variables.' });
  }
  const { text, targetLang } = req.body;
  if (!text || !targetLang) {
    return res.status(400).json({ error: 'Missing text or targetLang' });
  }

  /*
   * NOTE FOR SWAPPING TO OTHER TRANSLATION APIS:
   * 
   * If you'd rather connect to Google Cloud Translation API directly:
   * 
   * const url = `https://translation.googleapis.com/language/translate/v2?key=${process.env.GOOGLE_TRANSLATE_API_KEY}`;
   * const response = await fetch(url, {
   *   method: 'POST',
   *   headers: { 'Content-Type': 'application/json' },
   *   body: JSON.stringify({ q: text, target: targetLang })
   * });
   * const data = await response.json();
   * return res.json({ translation: data.data.translations[0].translatedText });
   * 
   * Or if you'd like to use DeepL API:
   * 
   * const response = await fetch('https://api-free.deepl.com/v2/translate', {
   *   method: 'POST',
   *   headers: {
   *     'Authorization': `DeepL-Auth-Key ${process.env.DEEPL_API_KEY}`,
   *     'Content-Type': 'application/json'
   *   },
   *   body: JSON.stringify({ text: [text], target_lang: targetLang.toUpperCase() })
   * });
   * const data = await response.json();
   * return res.json({ translation: data.translations[0].text });
   */

  const langNames = {
    uz: 'Uzbek (Oʻzbek)',
    ru: 'Russian (Русский)',
    en: 'English'
  };
  const targetLangName = langNames[targetLang] || targetLang;

  const systemPrompt = `You are a professional literary and academic translator. Translate the text precisely to the target language: ${targetLangName}. Preserve paragraphs and formatting. Return your response ONLY as a JSON object: {"translation": "translated text here"}`;
  const userPrompt = `Translate the following text to ${targetLangName}:\n\n${text}`;

  try {
    const data = await callOpenRouter(systemPrompt, userPrompt, 0.3, 1000);
    res.json({ translation: data.translation });
  } catch (e) {
    console.error('[/api/translate]', e.message);
    res.status(500).json({ error: e.message });
  }
});

/* ─── SAVED ARTICLES ─── */
app.post('/api/articles/save', authMiddleware, async (req, res) => {
  const { title, topic, content, difficulty, wordCount } = req.body;
  if (!title || !content) return res.status(400).json({ error: 'Missing title or content' });

  try {
    // Check if already saved (avoid duplicates)
    const existsRes = await db.query(
      'SELECT id FROM saved_articles WHERE user_id = $1 AND title = $2',
      [req.user.id, title]
    );

    if (existsRes.rowCount > 0) return res.json({ saved: false, message: 'Already in your library' });

    await db.query(
      'INSERT INTO saved_articles (user_id, title, topic, content, difficulty, word_count) VALUES ($1, $2, $3, $4, $5, $6)',
      [req.user.id, title, topic || '', content, difficulty || '', wordCount || 0]
    );

    res.json({ saved: true, message: 'Saved to your library!' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/articles/saved', authMiddleware, async (req, res) => {
  try {
    const articlesRes = await db.query(
      'SELECT id, title, topic, content, difficulty, word_count, saved_at FROM saved_articles WHERE user_id = $1 ORDER BY saved_at DESC',
      [req.user.id]
    );
    res.json({ articles: articlesRes.rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/articles/saved/:id', authMiddleware, async (req, res) => {
  try {
    const result = await db.query(
      'DELETE FROM saved_articles WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    res.json({ deleted: result.rowCount > 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ─── SAVED VOCABULARY ─── */
app.post('/api/vocab/save', authMiddleware, async (req, res) => {
  const { word, pos, ipa, definition, synonym, example, level } = req.body;
  if (!word || !definition) return res.status(400).json({ error: 'Missing word or definition' });

  try {
    const existsRes = await db.query(
      'SELECT id FROM saved_vocabulary WHERE user_id = $1 AND word = $2',
      [req.user.id, word.trim()]
    );

    if (existsRes.rowCount > 0) return res.json({ saved: false, message: 'Word already saved' });

    await db.query(
      'INSERT INTO saved_vocabulary (user_id, word, pos, ipa, definition, synonym, example, level) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
      [req.user.id, word.trim(), pos || '', ipa || '', definition, synonym || '', example || '', level || '']
    );

    res.json({ saved: true, message: 'Saved to your notebook!' });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/vocab/saved', authMiddleware, async (req, res) => {
  try {
    const wordsRes = await db.query(
      'SELECT id, word, pos, ipa, definition, synonym, example, level, saved_at FROM saved_vocabulary WHERE user_id = $1 ORDER BY saved_at DESC',
      [req.user.id]
    );
    res.json({ words: wordsRes.rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/vocab/saved/:id', authMiddleware, async (req, res) => {
  try {
    const result = await db.query(
      'DELETE FROM saved_vocabulary WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    res.json({ deleted: result.rowCount > 0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ─── HEALTH ─── */
app.get('/api/health', async (req, res) => {
  let dbOk = false;
  try {
    await db.query('SELECT 1');
    dbOk = true;
  } catch (e) {
    console.error('Healthcheck DB connection error:', e.message);
  }
  res.json({ 
    ok: true, 
    message: 'ReadForge AI server is running 🚀', 
    openrouterModel: OPENROUTER_MOD,
    bazaarlinkModel: BAZAARLINK_MOD,
    openrouterKeyLoaded: !!OPENROUTER_KEY,
    bazaarlinkKeyLoaded: !!BAZAARLINK_KEY,
    postgresConnected: dbOk
  });
});

/* ─── STARTUP ─── */
(async () => {
  try {
    await initDb();
    console.log('✅ Database schema initialized');
    await seedAdmins();
  } catch (err) {
    console.error('❌ Database initialization failed:', err.message);
  }

  app.listen(PORT, () => {
    console.log(`\n✅  ReadForge AI server running at http://localhost:${PORT}`);
    console.log(`   Articles (OpenRouter): Model ${OPENROUTER_MOD}`);
    console.log(`   Quiz/Vocab (BazaarLink): Model ${BAZAARLINK_MOD}`);
    console.log('\n   Open login.html to get started.\n');
  });
})();
