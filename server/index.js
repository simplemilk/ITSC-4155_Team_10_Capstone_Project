const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const path = require('path');
const { open } = require('sqlite');
const sqlite3 = require('sqlite3');

const app = express();
app.use(cors());
app.use(express.json());

const DB_PATH = path.join(__dirname, 'db.sqlite');

async function initDb() {
  const db = await open({ filename: DB_PATH, driver: sqlite3.Database });
  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      password TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  return db;
}

initDb().then(db => {
  app.locals.db = db;
}).catch(err => {
  console.error('Failed to initialize database', err);
  process.exit(1);
});

function validateEmail(email) {
  return typeof email === 'string' && /\S+@\S+\.\S+/.test(email);
}

function validatePassword(password) {
  return typeof password === 'string' && password.length >= 8;
}

app.post('/api/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  if (!validateEmail(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  if (!validatePassword(password)) {
    return res.status(400).json({ error: 'Password must be at least 8 characters' });
  }

  try {
    const db = app.locals.db;
    const existing = await db.get('SELECT id FROM users WHERE email = ?', email);
    if (existing) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    const hashed = await bcrypt.hash(password, 10);
    const result = await db.run(
      'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
      name, email, hashed
    );
    const user = { id: result.lastID, name, email };
    return res.status(201).json({ user });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
