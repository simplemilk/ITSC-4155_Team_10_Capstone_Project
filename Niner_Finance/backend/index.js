// TODO: implement email verification
//require('dotenv').config();
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const authRoutes = require('./routes/auth');
app.use('/api', authRoutes);

const categoryRoutes = require('./routes/categoryRoutes');
app.use('/api/categories', categoryRoutes);

const financeRoutes = require('./routes/financeRoutes');
app.use('/api', financeRoutes);

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));