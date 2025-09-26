const express = require('express');
const router = express.Router();

const defaultCategories = [
  { id: 1, name: "Food", isDefault: true },
  { id: 2, name: "Rent", isDefault: true },
  { id: 3, name: "Transport", isDefault: true },
];

let customCategories = [];
let nextCategoryId = 4;

router.get("/", (req, res) => {
  res.json([...defaultCategories, ...customCategories]);
});

router.post("/", (req, res) => {
  const { name } = req.body;

  if (!name || typeof name !== "string") {
    return res.status(400).json({ error: "Category name is required" });
  }

  const exists = [...defaultCategories, ...customCategories].some(
    (c) => c.name.toLowerCase() === name.toLowerCase()
  );
  if (exists) {
    return res.status(400).json({ error: "Category already exists" });
  }

  const newCategory = { id: nextCategoryId++, name, isDefault: false };
  customCategories.push(newCategory);

  res.status(201).json(newCategory);
});

router.put("/:id", (req, res) => {
  const { id } = req.params;
  const { name } = req.body;
  const category = customCategories.find((c) => c.id === parseInt(id));

  if (!category) {
    return res.status(404).json({ error: "Custom category not found" });
  }
  if (!name) {
    return res.status(400).json({ error: "New name is required" });
  }

  category.name = name;
  res.json(category);
});

router.delete("/:id", (req, res) => {
  const { id } = req.params;
  const index = customCategories.findIndex((c) => c.id === parseInt(id));

  if (index === -1) {
    return res.status(404).json({ error: "Custom category not found" });
  }

  const deleted = customCategories.splice(index, 1);
  res.json({ message: "Category deleted", deleted });
});

module.exports = router;
