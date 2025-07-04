import logging
import random
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔐 Токены
TELEGRAM_TOKEN = "7452845663:AAGCZvI2EUCae84pSH9FrvgK_CNCmjijQPs"
KINOPOISK_API_KEY = "2642ce70-0dc7-40e4-8cc9-caa62799dba4"

# 🎬 Жанры
GENRES = {
    "Драма": 2,
    "Комедия": 13,
    "Мелодрама": 4,
    "Триллер": 1,
    "Детектив": 5,
    "Ужасы": 17,
    "Фантастика": 6,
    "Приключения": 12,
    "Боевик": 11,
    "Романтическая комедия": 33,
    "Семейный": 7,
}


# ▶️ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"genre_{id_}")]
        for name, id_ in GENRES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! 🍿 Выбери жанр фильма:", reply_markup=reply_markup
    )


# ▶️ Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    print("👉 Нажата кнопка:", data)

    if data.startswith("genre_"):
        try:
            genre_id = int(data.split("_")[1])
            context.user_data["genre_id"] = genre_id
            print("✅ Жанр сохранён в context.user_data:", context.user_data)
            await send_random_film(query, context)
        except ValueError:
            await query.message.reply_text("Ошибка: неверный жанр.")
    elif data == "next":
        await send_random_film(query, context)
    elif data == "menu":
        await start(query, context)


# ▶️ Отправка случайного фильма
async def send_random_film(query, context):
    genre_id = context.user_data.get("genre_id", 13)

    # Первый запрос — по фильтрам
    url = "https://kinopoiskapiunofficial.tech/api/v2.2/films"
    params = {
        "type": "FILM",
        "genre": genre_id,
        "order": "NUM_VOTE",
        "ratingFrom": 6,
        "ratingTo": 10,
        "yearFrom": 2010,
        "yearTo": 2025,
        "page": 1
    }
    headers = {
        "X-API-KEY": KINOPOISK_API_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        if response.status_code != 200:
            await query.message.reply_text("😢 Не получилось получить список фильмов.")
            return

        data = response.json()
        films = data.get("items", [])
        if not films:
            await query.message.reply_text("😢 Фильмы не найдены.")
            return

        film = random.choice(films)
        film_id = film.get("kinopoiskId")

        # Второй запрос — подробности о фильме
        detail_url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}"
        detail_response = await client.get(detail_url, headers=headers)
        if detail_response.status_code != 200:
            await query.message.reply_text("😢 Не удалось получить информацию о фильме.")
            return

        detail = detail_response.json()

    # Данные о фильме
    name = detail.get("nameRu") or detail.get("nameEn") or "Без названия"
    description = detail.get("description") or "Описание потерялось где-то в кадрах 🎬"
    if len(description) > 500:
        description = description[:500] + "..."

    rating = detail.get("ratingKinopoisk")
    country = detail.get("countries", [{}])[0].get("country", "Неизвестно")
    year = detail.get("year")
    poster = detail.get("posterUrlPreview") or detail.get("posterUrl")
    trailer_url = f"https://www.kinopoisk.ru/film/{film_id}"

    # Кнопки
    keyboard = [
        [
            InlineKeyboardButton("🎲 Ещё фильм", callback_data="next"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="menu"),
        ],
        [InlineKeyboardButton("▶ Смотреть на Кинопоиске", url=trailer_url)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Текст
    text = f"<b>{name} ({year})</b>\n🌍 Страна: {country} | ⭐ Рейтинг: {rating}\n\n📝 {description}"

    await query.message.reply_photo(
        photo=poster,
        caption=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


# ▶️ Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("PopcornPal запущен... 🍿")
    app.run_polling()
