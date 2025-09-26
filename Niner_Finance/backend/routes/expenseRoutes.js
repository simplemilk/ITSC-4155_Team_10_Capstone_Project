const express = require('express');
import { getAllCategories } from "./helpers/categoryHelpers.js";
const router = express.Router();

let expenses = [];
let nextExpenseId = 1;

router.get("/", (req, res) => {
  res.json(expenses);
});

router.post("/", (req, res) => {
  const { description, amount, categoryId } = req.body;

  if (!description || !amount || !categoryId) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const categories = getAllCategories();
  const category = categories.find((c) => c.id === parseInt(categoryId));

  if (!category) {
    return res.status(400).json({ error: "Invalid category" });
  }

  const expense = {
    id: nextExpenseId++,
    description,
    amount,
    categoryId: category.id,
    categoryName: category.name,
    date: new Date().toISOString(),
  };

  expenses.push(expense);
  res.status(201).json(expense);
});

export default router;