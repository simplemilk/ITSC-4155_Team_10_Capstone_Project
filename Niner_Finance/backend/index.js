const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const authRoutes= require('./routes/auth');
app.use('/api', authRoutes);

const categoryRoutes = require('./routes/categoryRoutes');
app.use('/api/categories', categoryRoutes);

// Registration endpoint (if not using authRoutes)
app.post('/api/register', (req, res) => {
  const { email, username, password } = req.body;
  if (!email || !username || !password) {
    return res.status(400).json({ error: 'All fields required.' });
  }
  return res.json({ message: 'Registration successful!' });
});

app.listen(4000, () => console.log('Backend running on port 4000'));