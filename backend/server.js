const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { sequelize, connectDB } = require('./config/db');
const urlRoutes = require('./routes/urlRoutes');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());
app.use('/', urlRoutes);

const PORT = process.env.PORT || 5000;

connectDB().then(() => {
  sequelize.sync();
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
});