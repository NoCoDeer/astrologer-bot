require('dotenv').config();
const express = require('express');

const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Placeholder user route
app.get('/users', (req, res) => {
  res.json([]);
});

const port = process.env.PORT || 3003;
app.listen(port, () => {
  console.log(`API server listening on port ${port}`);
});
