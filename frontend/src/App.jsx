import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Subscriptions from './pages/Subscriptions';
import Content from './pages/Content';
import Transactions from './pages/Transactions';
import Schedule from './pages/Schedule';
import BotSettings from './pages/BotSettings';
import Logs from './pages/Logs';

export default function App() {
  return (
    <div>
      <nav>
        <ul>
          <li><Link to="/">Dashboard</Link></li>
          <li><Link to="/users">Users</Link></li>
          <li><Link to="/subscriptions">Subscriptions</Link></li>
          <li><Link to="/content">Content</Link></li>
          <li><Link to="/transactions">Transactions</Link></li>
          <li><Link to="/schedule">Schedule</Link></li>
          <li><Link to="/settings">Bot Settings</Link></li>
          <li><Link to="/logs">Logs</Link></li>
        </ul>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/users" element={<Users />} />
        <Route path="/subscriptions" element={<Subscriptions />} />
        <Route path="/content" element={<Content />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/schedule" element={<Schedule />} />
        <Route path="/settings" element={<BotSettings />} />
        <Route path="/logs" element={<Logs />} />
      </Routes>
    </div>
  );
}
