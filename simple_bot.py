"""
УПРОЩЕННАЯ РАБОЧАЯ ВЕРСИЯ БОТА
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import sqlite3
import hashlib
import time
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "8485530622:AAHoF8EUmJ-I2wrWAsz8vmRfLgDFFeATMmU"
ADMIN_ID = 6970104969

# Простая база данных
class SimpleDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('construction_simple.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        """Инициализация простой базы"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            queries INTEGER DEFAULT 0,
            created TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_pairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            question TEXT,
            answer TEXT,
            usage INTEGER DEFAULT 0
        )
        ''')
        
        # Добавляем базовые QA если их нет
        self.cursor.execute("SELECT COUNT(*) FROM qa_pairs")
        if self.cursor.fetchone()[0] == 0:
            self.add_base_qa()
        
        self.conn.commit()
    
    def add_base_qa(self):
        """Добавляем базовые вопросы-ответы"""
        base_qa = [
            ("фундамент", "Какой глубины должен быть фундамент?", 
             "Глубина фундамента зависит от глубины промерзания грунта. Для средней полосы России: 1.2-1.8 м."),
            ("фундамент", "Сколько стоит залить фундамент 10 на 10?", 
             "Ленточный фундамент для дома 10×10 м стоит примерно 200-350 тыс. рублей."),
            ("стены", "Сколько кирпича нужно на дом 100 м²?", 
             "Для дома 100 м² нужно примерно 22,000 шт. кирпича."),
            ("стены", "Что лучше газобетон или кирпич?", 
             "Газобетон: теплее, легче, дешевле. Кирпич: прочнее, долговечнее."),
            ("крыша", "Как рассчитать стропила для крыши?", 
             "Сечение стропил: 50×150 мм или 50×200 мм. Шаг: 600-1200 мм."),
            ("электрика", "Какое сечение провода для розеток?", 
             "Для розеток: кабель 3×2.5 мм², автомат 16А."),
        ]
        
        for category, question, answer in base_qa:
            self.cursor.execute(
                "INSERT INTO qa_pairs (category, question, answer) VALUES (?, ?, ?)",
                (category, question, answer)
            )
        
        self.conn.commit()
    
    def search_qa(self, query):
        """Поиск вопросов-ответов"""
        self.cursor.execute(
            "SELECT * FROM qa_pairs WHERE question LIKE ? OR answer LIKE ? LIMIT 10",
            (f"%{query}%", f"%{query}%")
        )
        return self.cursor.fetchall()
    
    def add_user(self, user_id, username, first_name):
        """Добавить пользователя"""
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )
        self.conn.commit()
    
    def update_queries(self, user_id):
        """Обновить счетчик запросов"""
        self.cursor.execute(
            "UPDATE users SET queries = queries + 1 WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()

# Основной бот
db = SimpleDatabase()

async def start(update: Update, context: CallbackContext):
    """Команда /start"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск", callback_data="search")],
        [InlineKeyboardButton("🧮 Калькуляторы", callback_data="calculators")],
        [InlineKeyboardButton("📦 Материалы", callback_data="materials")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🏗️ Привет, {user.first_name}!\n\nЯ - строительный бот. Чем могу помочь?",
        reply_markup=reply_markup
    )

async def search_command(update: Update, context: CallbackContext):
    """Команда /search"""
    if not context.args:
        await update.message.reply_text("Введите запрос для поиска: /search фундамент")
        return
    
    query = ' '.join(context.args)
    await perform_search(update, query)

async def perform_search(update: Update, query: str):
    """Выполнить поиск"""
    user_id = update.effective_user.id
    db.update_queries(user_id)
    
    results = db.search_qa(query)
    
    if results:
        response = f"🔍 *Результаты поиска по запросу '{query}':*\n\n"
        
        for i, row in enumerate(results, 1):
            response += f"*{i}. {row[2]}*\n"
            response += f"{row[3][:100]}...\n\n"
        
        # Создаем кнопки для результатов
        keyboard = []
        for i, row in enumerate(results[:3], 1):
            keyboard.append([
                InlineKeyboardButton(f"📝 {row[2][:30]}...", callback_data=f"qa_{row[0]}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔍 Новый поиск", callback_data="new_search"),
            InlineKeyboardButton("🏠 В меню", callback_data="menu")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"По запросу '{query}' ничего не найдено.\n\nПопробуйте другие ключевые слова."
        )

async def handle_message(update: Update, context: CallbackContext):
    """Обработка всех сообщений"""
    text = update.message.text
    
    # Если сообщение похоже на вопрос
    if any(word in text.lower() for word in ['?', 'сколько', 'как', 'что', 'почему']):
        await perform_search(update, text)
    else:
        await update.message.reply_text(
            "Я понимаю вопросы о строительстве. Например:\n"
            "• Какой фундамент лучше?\n"
            "• Сколько нужно кирпича на дом?\n"
            "• Какое сечение провода для розеток?\n\n"
            "Или используйте /search [ваш запрос]"
        )

async def button_handler(update: Update, context: CallbackContext):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "search":
        await query.edit_message_text("Введите ваш вопрос о строительстве:")
    
    elif data == "calculators":
        keyboard = [
            [InlineKeyboardButton("🧱 Фундамент", callback_data="calc_foundation")],
            [InlineKeyboardButton("🏠 Стены", callback_data="calc_walls")],
            [InlineKeyboardButton("💰 Стоимость", callback_data="calc_cost")],
            [InlineKeyboardButton("🏠 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🧮 Выберите калькулятор:", reply_markup=reply_markup)
    
    elif data == "materials":
        keyboard = [
            [InlineKeyboardButton("🧱 Кирпич", callback_data="mat_brick")],
            [InlineKeyboardButton("🧱 Бетон", callback_data="mat_concrete")],
            [InlineKeyboardButton("🧱 Утеплитель", callback_data="mat_insulation")],
            [InlineKeyboardButton("🏠 В меню", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📦 Выберите материал:", reply_markup=reply_markup)
    
    elif data == "profile":
        user = query.from_user
        await query.edit_message_text(
            f"👤 *Ваш профиль*\n\n"
            f"Имя: {user.first_name}\n"
            f"Username: @{user.username or 'не указан'}\n"
            f"ID: {user.id}\n\n"
            f"Используйте /start для главного меню.",
            parse_mode='Markdown'
        )
    
    elif data == "menu":
        keyboard = [
            [InlineKeyboardButton("🔍 Поиск", callback_data="search")],
            [InlineKeyboardButton("🧮 Калькуляторы", callback_data="calculators")],
            [InlineKeyboardButton("📦 Материалы", callback_data="materials")],
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏗️ *Главное меню*", reply_markup=reply_markup, parse_mode='Markdown')
    
    elif data.startswith("calc_"):
        calc_type = data.replace("calc_", "")
        if calc_type == "foundation":
            await query.edit_message_text(
                "🧱 *Калькулятор фундамента*\n\n"
                "Введите параметры:\n`длина ширина глубина тип`\n\n"
                "*Пример:* `10 8 1.5 ленточный`\n\n"
                "*Расчет:* Объем = Длина × Ширина × Глубина\n"
                "*Стоимость:* Объем × 3500 руб/м³",
                parse_mode='Markdown'
            )
        elif calc_type == "walls":
            await query.edit_message_text(
                "🏠 *Калькулятор стен*\n\n"
                "Введите параметры:\n`периметр высота материал`\n\n"
                "*Пример:* `40 3 кирпич`\n\n"
                "*Для кирпича:* 102 шт/м² × Площадь\n"
                "*Площадь:* Периметр × Высота",
                parse_mode='Markdown'
            )
        elif calc_type == "cost":
            await query.edit_message_text(
                "💰 *Калькулятор стоимости*\n\n"
                "Введите параметры:\n`площадь тип качество`\n\n"
                "*Пример:* `150 дом стандарт`\n\n"
                "*Цены за м²:*\n"
                "• Дом: 25-40 тыс. руб\n"
                "• Дача: 15-25 тыс. руб\n"
                "• Ремонт: 10-20 тыс. руб",
                parse_mode='Markdown'
            )
    
    elif data.startswith("mat_"):
        mat_type = data.replace("mat_", "")
        if mat_type == "brick":
            await query.edit_message_text(
                "🧱 *Кирпич керамический*\n\n"
                "*Цены:* 25-35 руб/шт\n"
                "*Расход:* 102 шт/м² (толщина 510 мм)\n"
                "*Стандартный размер:* 250×120×65 мм\n\n"
                "*Применение:* стены, фундаменты, цоколи"
            )
        elif mat_type == "concrete":
            await query.edit_message_text(
                "🧱 *Бетон М300*\n\n"
                "*Цена:* 4500-5500 руб/м³\n"
                "*Применение:* фундаменты, монолитные конструкции\n"
                "*Состав на 1 м³:*\n"
                "• Цемент: 380 кг\n"
                "• Песок: 645 кг\n"
                "• Щебень: 1080 кг\n"
                "• Вода: 190 л"
            )
        elif mat_type == "insulation":
            await query.edit_message_text(
                "🧱 *Утеплители*\n\n"
                "*Минеральная вата:*\n"
                "• Цена: 300-400 руб/м² (100 мм)\n"
                "• λ=0.036 Вт/м·К\n"
                "• Негорючая\n\n"
                "*Пеноплекс:*\n"
                "• Цена: 250-350 руб/м² (50 мм)\n"
                "• λ=0.032 Вт/м·К\n"
                "• Водонепроницаемый"
            )
    
    elif data.startswith("qa_"):
        qa_id = int(data.replace("qa_", ""))
        db.cursor.execute("SELECT * FROM qa_pairs WHERE id = ?", (qa_id,))
        result = db.cursor.fetchone()
        
        if result:
            db.cursor.execute(
                "UPDATE qa_pairs SET usage = usage + 1 WHERE id = ?",
                (qa_id,)
            )
            db.conn.commit()
            
            await query.edit_message_text(
                f"📝 *Вопрос:* {result[2]}\n\n"
                f"*Ответ:* {result[3]}\n\n"
                f"*Категория:* {result[1]}\n"
                f"*Использований:* {result[4] + 1}",
                parse_mode='Markdown'
            )
    
    elif data == "new_search":
        await query.edit_message_text("Введите новый запрос для поиска:")

async def help_command(update: Update, context: CallbackContext):
    """Команда /help"""
    await update.message.reply_text(
        "📚 *Помощь*\n\n"
        "*Основные команды:*\n"
        "/start - Начало работы\n"
        "/search [запрос] - Поиск информации\n"
        "/help - Эта справка\n\n"
        "*Примеры:*\n"
        "/search фундамент глубина\n"
        "/search сколько кирпича\n\n"
        "*Или просто напишите вопрос в чат!*",
        parse_mode='Markdown'
    )

def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("=" * 60)
    print("🚀 ПРОСТОЙ СТРОИТЕЛЬНЫЙ БОТ ЗАПУЩЕН!")
    print("=" * 60)
    print("📊 База знаний: готовые вопросы-ответы")
    print("🧮 Калькуляторы: фундамент, стены, стоимость")
    print("📦 Материалы: цены и характеристики")
    print("=" * 60)
    print("🤖 Бот готов к работе! Отправьте /start в Telegram")
    print("=" * 60)
    
    application.run_polling()

if __name__ == "__main__":
    main()