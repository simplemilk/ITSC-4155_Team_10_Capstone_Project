import express from "express";
import cors from "cors";
import financeRoutes from "./routes/financeRoutes.js";

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

app.use("/api/finance", financeRoutes);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
