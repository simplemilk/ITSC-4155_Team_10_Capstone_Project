import express from "express";

const router = express.Router();

const transactions = [
  { id: 1, type: "income", category: "Salary", amount: 3000, date: "2025-09-01" },
  { id: 2, type: "expense", category: "Food", amount: 500, date: "2025-09-05" },
  { id: 3, type: "expense", category: "Rent", amount: 1200, date: "2025-09-01" },
  { id: 4, type: "income", category: "Freelance", amount: 800, date: "2025-09-10" },
];

router.get("/summary", (req, res) => {
  const totalIncome = transactions
    .filter(t => t.type === "income")
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  const balance = totalIncome - totalExpenses;

  res.json({
    totalIncome,
    totalExpenses,
    balance,
    recent: transactions.slice(-5) // last 5 transactions
  });
});

export default router;
