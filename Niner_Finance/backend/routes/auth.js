const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const db = require('../db');
const { resetPasswordWithSecurity } = require('../controllers/passwordResetController');

// Registration route with password hashing
router.post('/register', async (req, res) => {
  const { email, username, password, favoriteColor } = req.body;
  if (!email || !username || !password || !favoriteColor) {
    return res.status(400).json({ error: 'All fields required.' });
  }
  try {
    const [existing] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(400).json({ error: 'Email already registered.' });
    }
    // Hash the password before saving!
    const hashedPassword = await bcrypt.hash(password, 10);
    await db.query(
      'INSERT INTO users (email, username, password, favoriteColor) VALUES (?, ?, ?, ?)',
      [email, username, hashedPassword, favoriteColor]
    );
    return res.json({ success: true, message: 'Registration successful!' });
  } catch (err) {
    console.error('Registration error:', err);
    return res.status(500).json({ error: 'Database error.' });
  }
});

router.post('/verify-security', async (req, res) => {
  const { email, favoriteColor } = req.body;
  try {
    const [rows] = await db.query(
      'SELECT * FROM users WHERE email = ? AND favoriteColor = ?',
      [email, favoriteColor]
    );
    if (rows.length === 0) {
      return res.json({ success: false, message: 'Incorrect email or security answer.' });
    }
    return res.json({ success: true });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Reset Password
router.post('/reset-password-security', async (req, res) => {
  const { email, newPassword } = req.body;
  if (!email || !newPassword) {
    return res.status(400).json({ success: false, message: 'Email and new password required.' });
  }

  try {
    // Hash the new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    
    // Update user's password
    const [result] = await db.query(
      'UPDATE users SET password = ? WHERE email = ?',
      [hashedPassword, email]
    );

    if (result.affectedRows === 0) {
      return res.json({ success: false, message: 'User not found.' });
    }

    return res.json({ success: true, message: 'Password has been reset successfully!' });
  } catch (err) {
    console.error('Reset password error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Login route with password comparison
// In your backend auth.js login route
router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ success: false, message: 'Username and password required.' });
  }

  try {
    const [rows] = await db.query('SELECT * FROM users WHERE username = ?', [username]);
    if (rows.length === 0) {
      return res.json({ success: false, message: 'Invalid credentials.' });
    }

    const user = rows[0];
    const isValidPassword = await bcrypt.compare(password, user.password);

    if (isValidPassword) {
      return res.json({ 
        success: true, 
        message: 'Login successful!',
        userId: user.id // Add this line
      });
    } else {
      return res.json({ success: false, message: 'Invalid credentials.' });
    }
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Add a transaction
router.post('/transactions', async (req, res) => {
  const { type, category, subcategory = null, amount, date, userId } = req.body; // Add userId
  if (!type || !category || !amount || !date || !userId) { // Check userId
    return res.status(400).json({ error: 'Missing required fields.' });
  }
  try {
    await db.query(
      'INSERT INTO transactions (type, category, subcategory, amount, date, user_id) VALUES (?, ?, ?, ?, ?, ?)', // Add user_id
      [type, category, subcategory, amount, date, userId] // Add userId
    );
    return res.json({ success: true, message: 'Transaction saved!' });
  } catch (err) {
    console.error('Transaction error:', err);
    return res.status(500).json({ error: 'Database error.' });
  }
});

router.get('/categories', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM categories ORDER BY type, name');
    return res.json({ success: true, categories: rows });
  } catch (err) {
    console.error('Error fetching categories:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

router.get('/transactions/:userId', async (req, res) => {
  const { userId } = req.params;
  try {
    const [rows] = await db.query(
      'SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC',
      [userId]
    );
    return res.json({ success: true, transactions: rows });
  } catch (err) {
    console.error('Error fetching transactions:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

router.get('/summary/:userId', async (req, res) => {
  const { userId } = req.params;
  try {
    const [income] = await db.query(
      'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "income"',
      [userId]
    );
    const [expenses] = await db.query(
      'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense"',
      [userId]
    );
    
        // Convert to numbers
    const totalIncome = parseFloat(income[0].total) || 0;
    const totalExpenses = parseFloat(expenses[0].total) || 0;
    
    return res.json({
      success: true,
      summary: {
        totalIncome: totalIncome,
        totalExpenses: totalExpenses,
        balance: totalIncome - totalExpenses,
        categories: []
      }
    });
  } catch (err) {
    console.error('Error fetching summary:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Password reset routes
module.exports = router;