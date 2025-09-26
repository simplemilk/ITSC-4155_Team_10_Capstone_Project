require('dotenv').config();

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const passwordResetRoutes = require('./passwordReset');

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(bodyParser.json());

app.use('/api', passwordResetRoutes);

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
