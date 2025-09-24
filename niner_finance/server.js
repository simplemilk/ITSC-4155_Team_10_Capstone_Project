import express from "express";
import financeRoutes from "./routes/financeRoutes.js";

const app = express();

app.use("/api/finance", financeRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
