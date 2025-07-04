from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random

# Твой токен от BotFather вставь сюда
TOKEN = '7452845663:AAGCZvI2EUCae84pSH9FrvgK_CNCmjijQPs'

# Приветственные фразы
greetings = [
    "Привет, друг! 🍿 Готов обсудить киношку?",
    "О, киношный гость! Что сегодня ищем: драмы, комедии или что-то душевное?",
    "Добро пожаловать в PopcornPal 🍿 — твой уютный киногид с юмором!"
]

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(greetings))
# Обработка всех сообщений (тут будем распознавать настроение и вкусы)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "грустно" in text or "плачу" in text:
        await update.message.reply_text("Обнимаю 🤗 Давай включим что-то душевное и тёплое. Рекомендую 'Виноваты звёзды' 🌟")
    elif "весело" in text or "улыбка" in text:
        await update.message.reply_text("Ты как солнышко сегодня! ☀️ Давай посмотрим что-то смешное, например 'Мы – Миллеры' 😂")
    elif "любовь" in text or "романтика":
        await update.message.reply_text("О, любовь витает в воздухе! 💕 Советую 'Гордость и предубеждение' или 'До встречи с тобой'.")
    else:
        await update.message.reply_text("Расскажи, какое у тебя настроение или жанр, и я что-нибудь подберу! 🎬")

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("PopcornPal запущен...")
app.run_polling()

    