const { Sequelize, DataTypes } = require('sequelize');

// Use SQLite database for simplicity
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: process.env.DB_PATH || 'admin.sqlite',
});

const User = sequelize.define('User', {
  telegram_id: {
    type: DataTypes.BIGINT,
    allowNull: false,
    unique: true,
  },
  username: DataTypes.STRING,
  is_premium: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
});

module.exports = { sequelize, User };
