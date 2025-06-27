require('dotenv').config();
const cron = require('node-cron');
const axios = require('axios');

// Placeholder: fetch users from API and send horoscope via bot API
cron.schedule('0 9 * * *', async () => {
  console.log('Running daily horoscope task');
  try {
    const users = await axios.get(`${process.env.API_URL}/users`);
    // send horoscope via bot or Telegram API
    console.log(`Would send horoscope to ${users.data.length} users`);
  } catch (e) {
    console.error('Scheduler error', e.message);
  }
});

console.log('Scheduler started');
