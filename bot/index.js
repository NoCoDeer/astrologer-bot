require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Simple in-memory storage for user profiles
const users = new Map();

const languages = {
  en: 'English',
  ru: 'Русский',
  es: 'Español',
};

bot.start((ctx) => {
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
  const userId = ctx.from.id;
  const profile = users.get(userId) || { language: lang };
  profile.language = lang;
  users.set(userId, profile);
  ctx.editMessageText(`Language set to ${languages[lang]}\nUse /help to see commands.`);
});

bot.command('help', (ctx) => {
  ctx.reply('Available commands:\n/profile - edit profile\n/horoscope - daily horoscope\n/tarot - tarot reading\n/subscribe - subscription info');
});

bot.command('profile', (ctx) => {
  ctx.reply('Profile management coming soon.');
});

bot.command('horoscope', async (ctx) => {
  ctx.reply('✨ Generating horoscope...');
  // Placeholder for AI request
  const text = 'Today is a great day to embrace new opportunities!';
  ctx.reply(text);
});

bot.command('tarot', (ctx) => {
  ctx.reply('🔮 Tarot reading feature coming soon.');
});

bot.command('subscribe', (ctx) => {
  ctx.reply('Subscription management coming soon.');
});

// Launch bot
bot.launch().then(() => {
  console.log('Bot started');
});

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
