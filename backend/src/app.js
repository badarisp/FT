const express = require('express');
const bodyParser = require('body-parser');
const flightsRoutes = require('./routes/flights');
const db = require('./utils/db');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(bodyParser.json());
app.use('/api/flights', flightsRoutes);

db.connect()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  })
  .catch(err => {
    console.error('Database connection failed:', err);
  });

module.exports = app;