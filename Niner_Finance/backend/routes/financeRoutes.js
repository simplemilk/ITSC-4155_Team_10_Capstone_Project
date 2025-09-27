const express = require('express');
const router = express.Router();
const db = require('../db');


const transactions = [
  { type: "income", category: "Salary", categoryName: "Salary", amount: 3000, date: "2025-09-01" },
  { type: "expense", category: "Food", categoryName: "Groceries", amount: 500, date: "2025-09-05" },
  { type: "expense", category: "Rent", categoryName: "Apartment", amount: 1200, date: "2025-09-01" },
  { type: "income", category: "Freelance", categoryName: "Freelance", amount: 800, date: "2025-09-10" },
  { type: "expense", category: "Entertainment", categoryName: "Movies", amount: 300, date: "2025-09-12" },
  { type: "expense", category: "Transport", categoryName: "Bus", amount: 200, date: "2025-09-14" },
];

async function seedTransactions() {
  const [rows] = await db.query('SELECT COUNT(*) AS count FROM transactions');
  if (rows[0].count === 0) {
    for (const tx of defaultTransactions) {
      await db.query(
        'INSERT INTO transactions (type, category, categoryName, amount, date, user_id) VALUES (?, ?, ?, ?, ?, ?)',
        [tx.type, tx.category, tx.categoryName, tx.amount, tx.date, 1] // Use user_id = 1 for default data
      );
    }
  }
}

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
    return res.json({
      success: true,
      summary: {
        totalIncome: income[0].total,
        totalExpenses: expenses[0].total,
        balance: income[0].total - expenses[0].total
      }
    });
  } catch (err) {
    console.error('Error fetching summary:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

router.get("/summary", async (req, res) => {
  await seedTransactions();
  const [rows] = await db.query('SELECT * FROM transactions');
  const transactions = rows;

  const totalIncome = transactions
    .filter(t => t.type === "income")
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  const balance = totalIncome - totalExpenses;

  const categories = transactions
    .filter(t => t.type === "expense")
    .reduce((acc, t) => {
      acc[t.category] = (acc[t.category] || 0) + Number(t.amount);
      return acc;
    }, {});

  const categoryData = Object.entries(categories).map(([name, amount]) => ({
    name,
    amount
  }));

  res.json({
    totalIncome,
    totalExpenses,
    balance,
    categories: categoryData, 
    recent: transactions.slice(-5) 
  });
});

// POST
router.post("/transaction", async (req, res) => {
  const { type, category, categoryName, amount, date } = req.body;
  if (!type || !category || !categoryName || !amount || !date) {
    return res.status(400).json({ error: "All fields are required" });
  }
  try {
    await db.query(
      'INSERT INTO transactions (type, category, categoryName, amount, date) VALUES (?, ?, ?, ?, ?)',
      [type, category, categoryName, amount, date]
    );
    res.status(201).json({ message: "Transaction added successfully" });
  } catch (error) {
    console.error("Error adding transaction:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
});


module.exports = router;
