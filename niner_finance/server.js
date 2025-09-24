import express from "express";
import categoryRoutes from "./routes/categoryRoutes.js";
import expenseRoutes from "./routes/expenseRoutes.js";
import financeRoutes from "./routes/financeRoutes.js";

const app = express();
app.use(express.json());

app.use("/api/finance", financeRoutes);
app.use("/api/categories", categoryRoutes);
app.use("/api/expenses", expenseRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
