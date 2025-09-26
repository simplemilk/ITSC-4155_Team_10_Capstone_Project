const express = require('express');
const router = express.Router();
const db = require('../db');

router.post('/register', async (req, res) => {
  const { email, username, password } = req.body;
  if (!email || !username || !password) {
    return res.status(400).json({ error: 'All fields required.' });
  }
  try {
    // Check if email already exists
    const [existing] = await db.query('SELECT id FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'Email already registered.' });
    }
    // Insert new user
    await db.query(
      'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
      [email, username, password]
    );
    return res.json({ message: 'Registration successful!' });
  } catch (err) {
    console.error('DB Error:', err);
    return res.status(500).json({ error: 'Database error.' });
  }
});

module.exports = router;