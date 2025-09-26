const express = require('express');
modules.exports = router;
const router = express.Router();



const transactions = [
  { id: 1, type: "income", category: "Salary", amount: 3000, date: "2025-09-01" },
  { id: 2, type: "expense", category: "Food", amount: 500, date: "2025-09-05" },
  { id: 3, type: "expense", category: "Rent", amount: 1200, date: "2025-09-01" },
  { id: 4, type: "income", category: "Freelance", amount: 800, date: "2025-09-10" },
  { id: 5, type: "expense", category: "Entertainment", amount: 300, date: "2025-09-12" },
  { id: 6, type: "expense", category: "Transport", amount: 200, date: "2025-09-14" },
];

router.get("/summary", (req, res) => {
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
      acc[t.category] = (acc[t.category] || 0) + t.amount;
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

export default router;
