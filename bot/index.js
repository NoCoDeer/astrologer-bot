require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Tarot deck used for simple readings
const TAROT_CARDS = [
  'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor',
  'The Hierophant', 'The Lovers', 'The Chariot', 'Strength', 'The Hermit',
  'Wheel of Fortune', 'Justice', 'The Hanged Man', 'Death', 'Temperance',
  'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun', 'Judgement', 'The World'
];

// Simple in-memory storage for user profiles
const users = new Map();

// Helper to get or create user profile
function getProfile(id) {
  if (!users.has(id)) {
    users.set(id, { language: 'en' });
  }
  return users.get(id);
}

async function askAI(prompt) {
  if (!process.env.OPENROUTER_API_KEY) {
    return 'AI service not configured.';
  }
  try {
    const res = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'anthropic/claude-3.5-sonnet',
        messages: [{ role: 'user', content: prompt }]
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return res.data.choices[0].message.content.trim();
  } catch (e) {
    console.error('OpenRouter error', e.message);
    return 'Unable to contact AI service.';
  }
}

const languages = {
  en: 'English',
  ru: 'Русский',
  es: 'Español',
};

bot.start((ctx) => {
  const profile = getProfile(ctx.from.id);
  ctx.reply(
    '🌟 Welcome to the Astrology Bot!\nSelect language:',
    Markup.inlineKeyboard([
      [Markup.button.callback('English', 'lang_en')],
      [Markup.button.callback('Русский', 'lang_ru')],
      [Markup.button.callback('Español', 'lang_es')],
    ])
  );
});

bot.action(/lang_(.+)/, (ctx) => {
  const lang = ctx.match[1];
  const profile = getProfile(ctx.from.id);
  profile.language = lang;
  ctx.editMessageText(
    `Language set to ${languages[lang]}\nUse /help to see commands.`
  );
});

bot.command('help', (ctx) => {
  ctx.reply(
    'Available commands:\n/profile - view profile\n/horoscope - daily horoscope\n/tarot - tarot reading\n/subscribe - subscription info'
  );
});

bot.command('profile', (ctx) => {
  const profile = getProfile(ctx.from.id);
  ctx.reply(`Language: ${languages[profile.language]}`);
});

bot.command('horoscope', async (ctx) => {
  ctx.reply('✨ Generating horoscope...');
  const response = await askAI('Give me a short general horoscope for today');
  ctx.reply(response);
});

bot.command('tarot', async (ctx) => {
  const card = TAROT_CARDS[Math.floor(Math.random() * TAROT_CARDS.length)];
  const aiText = await askAI(`Give a short interpretation for the tarot card ${card}`);
  ctx.replyWithMarkdown(`*${card}*\n${aiText}`);
});

bot.command('subscribe', (ctx) => {
  ctx.reply('Premium features will be available soon. Stay tuned!');
});

// Launch bot
bot.launch().then(() => {
  console.log('Bot started');
});

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
