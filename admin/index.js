require('dotenv').config();
const express = require('express');
const session = require('express-session');
const AdminJS = require('adminjs');
const AdminJSExpress = require('@adminjs/express');
const AdminJSSequelize = require('@adminjs/sequelize');
const { sequelize, User } = require('./models');

AdminJS.registerAdapter({ Database: AdminJSSequelize.Database, Resource: AdminJSSequelize.Resource });

const app = express();

if (!process.env.ADMIN_EMAIL || !process.env.ADMIN_PASSWORD) {
  console.error('ADMIN_EMAIL and ADMIN_PASSWORD must be set');
  process.exit(1);
}

const adminJs = new AdminJS({
  resources: [{ resource: User }],
  rootPath: '/admin',
});

const ADMIN = {
  email: process.env.ADMIN_EMAIL,
  password: process.env.ADMIN_PASSWORD,
};

sequelize.sync();

const router = AdminJSExpress.buildAuthenticatedRouter(adminJs, {
  authenticate: async (email, password) => {
    if (email === ADMIN.email && password === ADMIN.password) {
      return ADMIN;
    }
    return null;
  },
  cookieName: 'adminjs',
  cookiePassword: 'sessionsecret',
}, null, {
  resave: false,
  saveUninitialized: true,
  secret: 'sessionsecret',
});

app.use(adminJs.options.rootPath, router);

const port = process.env.PORT || 3002;
app.listen(port, () => {
  console.log(`Admin panel running at http://localhost:${port}${adminJs.options.rootPath}`);
});
