"""
ОСНОВНОЙ ФАЙЛ ЗАПУСКА БОТА v12.0
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import TOKEN
from handlers import BotHandlers
from database import HybridDatabase

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('construction_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота"""
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Инициализируем обработчики
    handlers = BotHandlers()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("menu", handlers.main_menu))
    
    # Поиск и информация
    application.add_handler(CommandHandler("search", handlers.search))
    application.add_handler(CommandHandler("ask", handlers.ask))
    application.add_handler(CommandHandler("topics", handlers.topics))
    application.add_handler(CommandHandler("materials", handlers.materials))
    
    # Калькуляторы
    application.add_handler(CommandHandler("calculate", handlers.calculate))
    application.add_handler(CommandHandler("calc", handlers.calc))
    
    # Личный кабинет
    application.add_handler(CommandHandler("profile", handlers.profile))
    application.add_handler(CommandHandler("history", handlers.history))
    application.add_handler(CommandHandler("favorites", handlers.favorites))
    application.add_handler(CommandHandler("projects", handlers.projects))
    
    # Дополнительные команды
    application.add_handler(CommandHandler("tip", handlers.tip))
    application.add_handler(CommandHandler("articles", handlers.articles))
    application.add_handler(CommandHandler("courses", handlers.courses))
    application.add_handler(CommandHandler("contractors", handlers.contractors))
    application.add_handler(CommandHandler("stats", handlers.stats))
    
    # Админ команды
    application.add_handler(CommandHandler("admin", handlers.admin))
    application.add_handler(CommandHandler("backup", handlers.backup))
    
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    
    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
    
    # Запускаем бота
    print("=" * 70)
    print("🚀 СТРОИТЕЛЬНЫЙ БОТ v12.0 ЗАПУЩЕН!")
    print("=" * 70)
    print("📊 ГИБРИДНАЯ БАЗА ДАННЫХ:")
    print("   • Реальных вопросов-ответов: 1,000+")
    print("   • Материалов с ценами: 100+")
    print("   • Статей и руководств: 10+")
    print("   • Категорий знаний: 7")
    print("=" * 70)
    print("🧮 ПОЛНЫЙ ФУНКЦИОНАЛ:")
    print("   • Умный поиск по всей базе")
    print("   • 10+ калькуляторов с реальными расчетами")
    print("   • Управление проектами и избранным")
    print("   • Ежедневные советы и статьи")
    print("   • Подрядчики и курсы обучения")
    print("   • Админ панель и резервное копирование")
    print("=" * 70)
    print("💾 База данных: construction.db")
    print("👤 Админ: @nopeaqe")
    print("=" * 70)
    print("🤖 Бот готов к работе! Отправьте /start в Telegram")
    print("=" * 70)
    
    # Запускаем polling
    application.run_polling(allowed_updates="*")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Критическая ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка: {e}")
        print("Проверьте токен бота и подключение к интернету.")