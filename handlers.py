"""
ОБРАБОТЧИКИ КОМАНД v12.0
"""

import logging
import hashlib
import time
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

from config import TOKEN, ADMIN_ID
from database import HybridDatabase
from keyboards import Keyboards
from calculators import ConstructionCalculators
from materials import MaterialsManager
from projects import ProjectsManager

logger = logging.getLogger(__name__)

class BotHandlers:
    """Класс обработчиков команд бота"""
    
    def __init__(self):
        self.db = HybridDatabase()
        self.calculators = ConstructionCalculators()
        self.materials = MaterialsManager(self.db)
        self.projects = ProjectsManager(self.db)
        self.user_states = {}  # Для хранения состояний пользователей
    
    # ==================== ОСНОВНЫЕ КОМАНДЫ ====================
    
    async def start(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Регистрируем пользователя
        self.db.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name or ""
        )
        
        welcome_text = f"""
🏗️ *Добро пожаловать, {user.first_name}!*

Я — *Строительный Бот v12.0* с полной базой знаний!

📊 *Мои возможности:*

🔍 *Умный поиск:*
• 1,000+ реальных вопросов-ответов
• 10+ категорий строительства
• Быстрый поиск по материалам

🧮 *Калькуляторы:*
• 10+ типов расчетов
• Реальные формулы и цены
• Детальные сметы

📦 *Материалы:*
• 100+ материалов с ценами
• Сравнение и выбор
• Поставщики и бренды

📚 *База знаний:*
• Статьи и руководства
• Ежедневные советы
• Курсы обучения

👤 *Личный кабинет:*
• Проекты и сметы
• История запросов
• Избранное

🤝 *Сервисы:*
• Подрядчики и услуги
• Рекомендации
• Поддержка

*Начните с /menu или просто задайте вопрос!*
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=Keyboards.main_menu(),
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /help"""
        help_text = """
📚 *ПОЛНАЯ СПРАВКА*

*Основные команды:*
/start - Начало работы
/menu - Главное меню
/help - Эта справка

*Поиск и информация:*
/search [текст] - Поиск в базе
/ask [вопрос] - Задать вопрос
/topics - Все категории
/materials - Материалы с ценами

*Калькуляторы:*
/calculate - Все калькуляторы
/calc - Быстрые расчеты

*Личный кабинет:*
/profile - Ваш профиль
/history - История запросов
/favorites - Избранное
/projects - Мои проекты

*Дополнительно:*
/tip - Совет дня
/articles - Статьи и руководства
/courses - Курсы обучения
/contractors - Подрядчики

*Примеры использования:*
• `/search фундамент глубина`
• `/ask Сколько нужно кирпича на дом 100 м²?`
• `/calculate фундамент 10 8 1.5 ленточный`
• `/materials цемент`

*Для быстрого доступа используйте кнопки в меню!*
"""
        
        await update.message.reply_text(
            help_text,
            reply_markup=Keyboards.back_to_menu(),
            parse_mode='Markdown'
        )
    
    async def main_menu(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /menu"""
        await update.message.reply_text(
            "🏗️ *Главное меню*\n\nВыберите раздел:",
            reply_markup=Keyboards.main_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== ПОИСК И ИНФОРМАЦИЯ ====================
    
    async def search(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /search"""
        if not context.args:
            await update.message.reply_text(
                "🔍 *Поиск информации*\n\n"
                "Введите поисковый запрос:\n"
                "`/search фундамент глубина промерзание`\n\n"
                "Или просто напишите вопрос в чат!",
                parse_mode='Markdown',
                reply_markup=Keyboards.search_menu()
            )
            return
        
        query = ' '.join(context.args)
        await self.perform_search(update, query)
    
    async def ask(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /ask"""
        if not context.args:
            await update.message.reply_text(
                "❓ *Задать вопрос эксперту*\n\n"
                "Введите ваш вопрос:\n"
                "`/ask Какой фундамент лучше для дома из газобетона?`\n\n"
                "Или просто напишите вопрос в чат!",
                parse_mode='Markdown'
            )
            return
        
        query = ' '.join(context.args)
        await self.perform_search(update, query)
    
    async def perform_search(self, update: Update, query: str) -> None:
        """Выполняет поиск по базе знаний"""
        user_id = update.effective_user.id
        start_time = time.time()
        
        # Обновляем активность пользователя
        self.db.update_user_activity(user_id)
        
        # Сначала проверяем, не калькулятор ли это
        if any(word in query.lower() for word in ['посчитай', 'рассчитай', 'расчет', 'сколько нужно', 'как рассчитать']):
            calc_type, params, result = ConstructionCalculators.parse_calc_command(query)
            
            if "error" not in result:
                formatted_result = ConstructionCalculators.format_result(calc_type, result)
                await update.message.reply_text(formatted_result, parse_mode='Markdown')
                return
        
        # Ищем в базе знаний
        question_hash = hashlib.md5(query.lower().encode()).hexdigest()
        exact_answer = self.db.get_answer_by_hash(question_hash)
        
        response_time = time.time() - start_time
        
        if exact_answer:
            # Найден точный ответ
            self.db.increment_qa_usage(exact_answer['id'])
            self.db.add_query_history(user_id, query, exact_answer['id'], response_time)
            
            response = f"""
🔍 *Найден ответ на ваш запрос*

*Вопрос:* {query}

*Ответ:* {exact_answer['answer']}

*Категория:* {exact_answer.get('category_name', 'Общая')} {exact_answer.get('emoji', '')}
*Сложность:* {'★' * min(5, exact_answer.get('difficulty', 1))}
*Использований:* {exact_answer.get('usage_count', 0) + 1}

⏱️ *Ответ найден за {response_time:.2f} секунды*
"""
            
            await update.message.reply_text(
                response,
                reply_markup=Keyboards.qa_detail(exact_answer['id'], exact_answer['category_id']),
                parse_mode='Markdown'
            )
            
        else:
            # Ищем похожие вопросы
            similar_results = self.db.search_qa(query, limit=5)
            
            if similar_results:
                response = f"""
🔍 *По вашему запросу не найден точный ответ*

*Похожие вопросы:*
"""
                keyboard = []
                
                for result in similar_results:
                    response += f"\n• *{result['question']}*\n"
                    response += f"  {result['answer'][:80]}...\n"
                    
                    keyboard.append([
                        InlineKeyboardButton(
                            f"📝 {result['question'][:30]}...",
                            callback_data=f"qa_{result['id']}"
                        )
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("🔍 Новый поиск", callback_data="search_main"),
                    InlineKeyboardButton("❓ Задать вопрос", callback_data="ask_question")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    response,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
            else:
                # Ничего не найдено
                response = f"""
🤔 *По вашему запросу ничего не найдено*

*Запрос:* "{query}"

*Попробуйте:*
• Упростить формулировку
• Использовать другие ключевые слова
• Задать вопрос по-другому
• Использовать калькуляторы (/calculate)

*Или выберите действие ниже:*
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔍 Новый поиск", callback_data="search_main")],
                    [InlineKeyboardButton("🧮 Калькуляторы", callback_data="calculators_main")],
                    [InlineKeyboardButton("📚 Все темы", callback_data="knowledge_base")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    response,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
    
    async def topics(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /topics"""
        await update.message.reply_text(
            "📚 *Категории знаний*\n\nВыберите категорию:",
            reply_markup=Keyboards.knowledge_base(),
            parse_mode='Markdown'
        )
    
    # ==================== КАЛЬКУЛЯТОРЫ ====================
    
    async def calculate(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /calculate"""
        if context.args:
            # Пользователь ввел параметры калькулятора
            query = ' '.join(context.args)
            calc_type, params, result = ConstructionCalculators.parse_calc_command(query)
            
            if "error" in result:
                await update.message.reply_text(
                    f"❌ *Ошибка:* {result['error']}\n\n"
                    f"Используйте /calculate для выбора калькулятора",
                    parse_mode='Markdown'
                )
            else:
                formatted_result = ConstructionCalculators.format_result(calc_type, result)
                await update.message.reply_text(formatted_result, parse_mode='Markdown')
        else:
            # Показать меню калькуляторов
            await update.message.reply_text(
                "🧮 *Калькуляторы и расчеты*\n\nВыберите тип расчета:",
                reply_markup=Keyboards.calculators_menu(),
                parse_mode='Markdown'
            )
    
    async def calc(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /calc (короткая версия)"""
        await self.calculate(update, context)
    
    # ==================== МАТЕРИАЛЫ ====================
    
    async def materials(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /materials"""
        if context.args:
            query = ' '.join(context.args)
            await self.search_materials(update, query)
        else:
            await update.message.reply_text(
                "📦 *База материалов*\n\nВыберите категорию материалов:",
                reply_markup=Keyboards.materials_menu(),
                parse_mode='Markdown'
            )
    
    async def search_materials(self, update: Update, query: str) -> None:
        """Поиск материалов"""
        materials = self.db.search_materials(query, limit=10)
        
        if materials:
            response = f"📦 *Материалы по запросу '{query}':*\n\n"
            keyboard = []
            
            for i, mat in enumerate(materials[:5], 1):
                avg_price = (mat['price_min'] + mat['price_max']) / 2
                response += f"*{i}. {mat['name']}*\n"
                response += f"   Цена: {mat['price_min']}-{mat['price_max']} {mat['unit']} (средняя: {avg_price:.0f})\n"
                response += f"   Категория: {mat['category']}\n"
                response += f"   Применение: {mat['applications'][:60]}...\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"📦 {mat['name'][:25]}...",
                        callback_data=f"material_{mat['id']}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔍 Новый поиск", callback_data="search_materials_form"),
                InlineKeyboardButton("◀️ В меню", callback_data="menu_main")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"📦 *Материалы по запросу '{query}' не найдены*\n\n"
                "Попробуйте другой запрос или выберите категорию:",
                reply_markup=Keyboards.materials_menu(),
                parse_mode='Markdown'
            )
    
    # ==================== ЛИЧНЫЙ КАБИНЕТ ====================
    
    async def profile(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /profile"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if user_data:
            history = self.db.get_user_history(user.id, limit=5)
            projects = self.db.get_user_projects(user.id)
            favorites = self.db.get_favorites(user.id)
            
            response = f"""
👤 *Ваш профиль*

*Основное:*
• Имя: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'не указан'}
• Опыт: {user_data['experience']}/10
• Регион: {user_data['region'] or 'не указан'}

*Статистика:*
• Запросов: {user_data['queries_count']}
• Проектов: {len(projects)}
• В избранном: {len(favorites)}
• Активен: {user_data['last_active'][:10] if user_data['last_active'] else 'сегодня'}

*Бюджет:* {user_data['budget'] or 0:,.0f} руб
"""
        else:
            response = "Профиль не найден. Используйте /start для регистрации."
        
        await update.message.reply_text(
            response,
            reply_markup=Keyboards.profile_menu(),
            parse_mode='Markdown'
        )
    
    async def history(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /history"""
        user_id = update.effective_user.id
        history = self.db.get_user_history(user_id, limit=15)
        
        if history:
            response = "📜 *История ваших запросов:*\n\n"
            
            for i, record in enumerate(history, 1):
                date = record['created_at'][:10]
                time_str = record['created_at'][11:16]
                question = record['question'][:50] + "..." if len(record['question']) > 50 else record['question']
                
                response += f"*{i}. {date} {time_str}*\n"
                response += f"   {question}\n"
                
                if record.get('response_time'):
                    response += f"   ⏱️ {record['response_time']:.2f} сек\n"
                
                response += "\n"
        else:
            response = "📜 *История запросов пуста*\n\nУ вас еще не было запросов к боту."
        
        keyboard = [
            [InlineKeyboardButton("🧹 Очистить историю", callback_data="history_clear_confirm")],
            [InlineKeyboardButton("◀️ В профиль", callback_data="profile_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def favorites(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /favorites"""
        await update.message.reply_text(
            "⭐ *Избранное*\n\nВыберите категорию:",
            reply_markup=Keyboards.favorites_menu(),
            parse_mode='Markdown'
        )
    
    async def projects(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /projects"""
        user_id = update.effective_user.id
        projects = self.db.get_user_projects(user_id)
        
        if projects:
            response = "📋 *Ваши проекты:*\n\n"
            
            for i, project in enumerate(projects, 1):
                response += f"*{i}. {project['name']}*\n"
                response += f"   Тип: {project['type']}\n"
                response += f"   Площадь: {project['area']} м²\n"
                response += f"   Бюджет: {project['budget']:,.0f} руб\n"
                response += f"   Статус: {project['status']} ({project['progress']}%)\n"
                response += f"   Создан: {project['created_at'][:10]}\n\n"
        else:
            response = "📋 *У вас пока нет проектов*\n\nСоздайте первый проект!"
        
        await update.message.reply_text(
            response,
            reply_markup=Keyboards.projects_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ====================
    
    async def tip(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /tip (совет дня)"""
        tip = self.db.get_daily_tip()
        
        if tip:
            response = f"""
💡 *Совет дня*

*Категория:* {tip['category']}
*Сложность:* {'★' * tip['difficulty']}
*Сезон:* {tip['season']}

*Совет:*
{tip['tip']}

*Просмотров:* {tip['views']}
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("⭐ В избранное", callback_data=f"fav_tip_{tip['id']}"),
                    InlineKeyboardButton("📅 Другие советы", callback_data="more_tips")
                ],
                [InlineKeyboardButton("◀️ В меню", callback_data="menu_main")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "💡 *Совет дня*\n\nСоветы временно недоступны. Попробуйте позже.",
                parse_mode='Markdown'
            )
    
    async def articles(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /articles"""
        articles = self.db.get_articles(limit=10)
        
        if articles:
            response = "📚 *Статьи и руководства:*\n\n"
            keyboard = []
            
            for article in articles:
                response += f"• *{article['title']}*\n"
                response += f"  {article['short_content'] or article['content'][:80]}...\n"
                response += f"  Категория: {article.get('category_name', 'Общая')}\n"
                response += f"  Время чтения: {article['read_time']} мин\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"📖 {article['title'][:30]}...",
                        callback_data=f"article_{article['id']}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("◀️ В меню", callback_data="menu_main")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "📚 *Статьи*\n\nРаздел статей в разработке.",
                parse_mode='Markdown'
            )
    
    async def courses(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /courses"""
        courses = self.db.get_courses(limit=10)
        
        if courses:
            response = "🎓 *Курсы обучения:*\n\n"
            
            for course in courses:
                price = "Бесплатно" if course['free'] else f"{course['price']:,.0f} руб"
                response += f"• *{course['title']}*\n"
                response += f"  {course['description'][:80]}...\n"
                response += f"  Сложность: {'★' * course['difficulty']}\n"
                response += f"  Длительность: {course['duration_hours']} часов\n"
                response += f"  Цена: {price}\n"
                response += f"  Рейтинг: {course['rating']}/5 ({course['students_count']} студентов)\n\n"
            
            keyboard = [
                [InlineKeyboardButton("📚 Все курсы", callback_data="courses_all")],
                [InlineKeyboardButton("◀️ В меню", callback_data="menu_main")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "🎓 *Курсы*\n\nРаздел курсов в разработке.",
                parse_mode='Markdown'
            )
    
    async def contractors(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /contractors"""
        await update.message.reply_text(
            "🤝 *Подрядчики и услуги*\n\nВыберите действие:",
            reply_markup=Keyboards.contractors_menu(),
            parse_mode='Markdown'
        )
    
    async def stats(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /stats (статистика базы)"""
        stats = self.db.get_statistics()
        
        response = f"""
📊 *Статистика базы знаний*

*Объем информации:*
• Пользователей: {stats.get('users', 0)}
• Вопросов-ответов: {stats.get('qa_pairs', 0):,}
• Материалов: {stats.get('materials', 0):,}
• Статей: {stats.get('articles', 0)}
• Курсов: {stats.get('courses', 0)}
• Подрядчиков: {stats.get('contractors', 0)}

*Активность:*
• Всего запросов: {stats.get('query_history', 0):,}
• Использований QA: {stats.get('total_usage', 0):,}

*Популярные категории:*
"""
        
        for cat in stats.get('popular_categories', []):
            response += f"• {cat['emoji']} {cat['name']}: {cat['qa_count']:,} вопросов\n"
        
        response += f"\n*Топ пользователей:*\n"
        
        for user in stats.get('active_users', [])[:3]:
            response += f"• @{user.get('username', 'anonymous')}: {user.get('queries_count')} запросов\n"
        
        response += f"\n*Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="stats_refresh")],
            [InlineKeyboardButton("◀️ В меню", callback_data="menu_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ==================== АДМИН КОМАНДЫ ====================
    
    async def admin(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /admin"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text(
                "❌ *Доступ запрещен*\n\nЭта команда только для администратора @nopeaqe",
                parse_mode='Markdown'
            )
            return
        
        stats = self.db.get_statistics()
        
        response = f"""
⚙️ *Админ панель* (@nopeaqe)

*Статистика базы:*
• Вопросов-ответов: {stats.get('qa_pairs', 0):,}
• Материалов: {stats.get('materials', 0):,}
• Пользователей: {stats.get('users', 0):,}

*Размер базы:* ~{(stats.get('qa_pairs', 0) + stats.get('materials', 0)) // 1000}K записей
*Последнее обновление:* {datetime.now().strftime('%d.%m.%Y %H:%M')}

Выберите действие:
"""
        
        await update.message.reply_text(
            response,
            reply_markup=Keyboards.admin_menu(),
            parse_mode='Markdown'
        )
    
    async def backup(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /backup (только для админа)"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Эта команда только для администратора.")
            return
        
        try:
            backup_path = self.db.backup_database()
            await update.message.reply_text(
                f"✅ *Резервная копия создана успешно!*\n\n"
                f"Файл: `{backup_path}`\n"
                f"Время: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка резервного копирования: {e}")
            await update.message.reply_text(f"❌ Ошибка создания резервной копии: {e}")
    
    # ==================== ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ ====================
    
    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        """Обработчик всех текстовых сообщений"""
        message_text = update.message.text
        
        # Игнорируем команды
        if message_text.startswith('/'):
            return
        
        user_id = update.effective_user.id
        
        # Обновляем активность пользователя
        self.db.update_user_activity(user_id)
        
        # Проверяем, не является ли сообщение командой к калькулятору
        if any(word in message_text.lower() for word in ['посчитай', 'рассчитай', 'расчет', 'сколько нужно', 'как рассчитать']):
            calc_type, params, result = ConstructionCalculators.parse_calc_command(message_text)
            
            if "error" not in result:
                formatted_result = ConstructionCalculators.format_result(calc_type, result)
                await update.message.reply_text(formatted_result, parse_mode='Markdown')
                return
        
        # Проверяем, не является ли сообщение запросом материала
        if any(word in message_text.lower() for word in ['цена', 'стоимость', 'купить', 'материал', 'сколько стоит']):
            await self.search_materials(update, message_text)
            return
        
        # По умолчанию обрабатываем как поисковый запрос
        await self.perform_search(update, message_text)
    
    # ==================== ОБРАБОТЧИК КНОПОК ====================
    
    async def button_handler(self, update: Update, context: CallbackContext) -> None:
        """Обработчик нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            # Главное меню
            if data == "menu_main":
                await query.edit_message_text(
                    "🏗️ *Главное меню*\n\nВыберите раздел:",
                    reply_markup=Keyboards.main_menu(),
                    parse_mode='Markdown'
                )
            
            # Поиск
            elif data == "search_main":
                await query.edit_message_text(
                    "🔍 *Поиск информации*\n\nВведите ваш запрос:",
                    parse_mode='Markdown'
                )
            
            elif data == "search_materials_form":
                await query.edit_message_text(
                    "🔍 *Поиск материалов*\n\nВведите название материала:",
                    parse_mode='Markdown'
                )
            
            # База знаний
            elif data == "knowledge_base":
                await query.edit_message_text(
                    "📚 *База знаний*\n\nВыберите категорию:",
                    reply_markup=Keyboards.knowledge_base(),
                    parse_mode='Markdown'
                )
            
            # Калькуляторы
            elif data == "calculators_main":
                await query.edit_message_text(
                    "🧮 *Калькуляторы и расчеты*\n\nВыберите тип расчета:",
                    reply_markup=Keyboards.calculators_menu(),
                    parse_mode='Markdown'
                )
            
            elif data.startswith("calc_"):
                calc_type = data.replace("calc_", "")
                
                if calc_type == "help":
                    help_text = ConstructionCalculators.get_calc_help()
                    await query.edit_message_text(help_text, parse_mode='Markdown')
                else:
                    help_text = ConstructionCalculators.get_calc_help(calc_type)
                    await query.edit_message_text(help_text, parse_mode='Markdown')
            
            # Материалы
            elif data == "materials_main":
                await query.edit_message_text(
                    "📦 *База материалов*\n\nВыберите категорию:",
                    reply_markup=Keyboards.materials_menu(),
                    parse_mode='Markdown'
                )
            
            elif data.startswith("mat_category_"):
                category = data.replace("mat_category_", "")
                materials = self.db.get_materials_by_category(category, limit=10)
                
                if materials:
                    response = f"📦 *Категория: {category}*\n\n"
                    keyboard = []
                    
                    for mat in materials:
                        avg_price = (mat['price_min'] + mat['price_max']) / 2
                        response += f"• *{mat['name']}*\n"
                        response += f"  Цена: {mat['price_min']}-{mat['price_max']} {mat['unit']}\n"
                        response += f"  Средняя: {avg_price:.0f} {mat['unit']}\n\n"
                        
                        keyboard.append([
                            InlineKeyboardButton(
                                f"📦 {mat['name'][:25]}...",
                                callback_data=f"material_{mat['id']}"
                            )
                        ])
                    
                    keyboard.append([
                        InlineKeyboardButton("◀️ Назад", callback_data="materials_main")
                    ])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(
                        response,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        f"📦 *Категория: {category}*\n\nМатериалы не найдены.",
                        reply_markup=Keyboards.back_to_menu(),
                        parse_mode='Markdown'
                    )
            
            elif data.startswith("material_"):
                material_id = int(data.replace("material_", ""))
                await self.show_material_detail(query, material_id)
            
            # Профиль
            elif data == "profile_main":
                await self.profile(query, context)
            
            # Избранное
            elif data == "favorites_main":
                await query.edit_message_text(
                    "⭐ *Избранное*\n\nВыберите категорию:",
                    reply_markup=Keyboards.favorites_menu(),
                    parse_mode='Markdown'
                )
            
            # Проекты
            elif data == "projects_main":
                await self.projects(query, context)
            
            # Статистика
            elif data == "stats_main" or data == "stats_refresh":
                await self.stats(query, context)
            
            # Админ
            elif data.startswith("admin_"):
                await self.handle_admin_action(query, data)
            
            # QA детали
            elif data.startswith("qa_"):
                qa_id = int(data.replace("qa_", ""))
                await self.show_qa_detail(query, qa_id)
            
            # Категория детали
            elif data.startswith("category_"):
                category_id = int(data.replace("category_", ""))
                await self.show_category_detail(query, category_id)
            
            # Статья детали
            elif data.startswith("article_"):
                article_id = int(data.replace("article_", ""))
                await self.show_article_detail(query, article_id)
            
            # Добавление в избранное
            elif data.startswith("fav_"):
                await self.handle_favorite_action(query, data)
            
            # Назад
            elif data == "back":
                await query.edit_message_text(
                    "◀️ *Возврат в предыдущее меню*",
                    reply_markup=Keyboards.back_to_menu(),
                    parse_mode='Markdown'
                )
            
            else:
                await query.edit_message_text(
                    f"🔄 *Кнопка '{data}' обработана*\n\nИспользуйте /menu для навигации",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки кнопки {data}: {e}")
            await query.edit_message_text(
                "❌ *Ошибка обработки запроса*\n\nПопробуйте еще раз или используйте /menu",
                parse_mode='Markdown'
            )
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    async def show_material_detail(self, query, material_id: int) -> None:
        """Показать детали материала"""
        material = self.db.cursor.execute(
            "SELECT * FROM materials WHERE id = ?", (material_id,)
        ).fetchone()
        
        if material:
            avg_price = (material['price_min'] + material['price_max']) / 2
            
            response = f"""
📦 *{material['name']}*

*Категория:* {material['category']}
*Подкатегория:* {material['subcategory']}
*Единица измерения:* {material['unit']}

*Цены:*
• Минимальная: {material['price_min']} руб/{material['unit']}
• Максимальная: {material['price_max']} руб/{material['unit']}
• Средняя: {avg_price:.0f} руб/{material['unit']}

*Характеристики:*
• Плотность: {material['density']} кг/м³
• Свойства: {material['properties'][:150]}...

*Применение:* {material['applications'][:200]}...

*Преимущества:* {material['advantages'][:150]}...

*Недостатки:* {material['disadvantages'][:150]}...

*Поставщики:* {material['suppliers']}
*Стандарты:* {material['standards']}
*Экологичность:* {'★' * min(5, material['eco_rating'])}
"""
            
            await query.edit_message_text(
                response,
                reply_markup=Keyboards.material_detail(material_id, material['category']),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Материал не найден.",
                parse_mode='Markdown'
            )
    
    async def show_qa_detail(self, query, qa_id: int) -> None:
        """Показать детали QA"""
        qa_data = self.db.cursor.execute(
            "SELECT q.*, c.name as category_name, c.emoji FROM qa_pairs q "
            "LEFT JOIN categories c ON q.category_id = c.id "
            "WHERE q.id = ?", (qa_id,)
        ).fetchone()
        
        if qa_data:
            self.db.increment_qa_usage(qa_id)
            
            response = f"""
📝 *Вопрос-ответ*

*Вопрос:* {qa_data['question']}

*Ответ:* {qa_data['answer']}

*Категория:* {qa_data['category_name']} {qa_data['emoji']}
*Сложность:* {'★' * min(5, qa_data['difficulty'])}
*Использований:* {qa_data['usage_count'] + 1}
*Теги:* {qa_data['tags']}
"""
            
            await query.edit_message_text(
                response,
                reply_markup=Keyboards.qa_detail(qa_id, qa_data['category_id']),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Вопрос-ответ не найден.",
                parse_mode='Markdown'
            )
    
    async def show_category_detail(self, query, category_id: int) -> None:
        """Показать детали категории"""
        category = self.db.get_category_by_id(category_id)
        
        if category:
            # Получаем вопросы в категории
            qa_list = self.db.cursor.execute(
                "SELECT id, question FROM qa_pairs WHERE category_id = ? ORDER BY usage_count DESC LIMIT 5",
                (category_id,)
            ).fetchall()
            
            # Получаем статьи в категории
            articles = self.db.get_articles(category_id, limit=3)
            
            response = f"""
{category['emoji']} *{category['name']}*

*Вопросов в категории:* {category['questions_count']}

"""
            
            if qa_list:
                response += "*Популярные вопросы:*\n"
                for qa in qa_list:
                    response += f"• {qa['question'][:50]}...\n"
                response += "\n"
            
            if articles:
                response += "*Статьи:*\n"
                for article in articles:
                    response += f"• {article['title'][:50]}...\n"
            
            await query.edit_message_text(
                response,
                reply_markup=Keyboards.category_detail(category_id),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Категория не найдена.",
                parse_mode='Markdown'
            )
    
    async def show_article_detail(self, query, article_id: int) -> None:
        """Показать детали статьи"""
        article = self.db.get_article(article_id)
        
        if article:
            response = f"""
📚 *{article['title']}*

*Категория:* {article['category_name']}
*Автор:* {article['author'] or 'Неизвестен'}
*Время чтения:* {article['read_time']} минут
*Просмотров:* {article['views']}

*Содержание:*
{article['content'][:1500]}...

*Теги:* {article['tags']}
"""
            
            # Обрезаем если слишком длинный
            if len(response) > 4000:
                response = response[:4000] + "\n\n... (продолжение в полной версии)"
            
            await query.edit_message_text(
                response,
                reply_markup=Keyboards.article_detail(article_id, article['category_id']),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Статья не найдена.",
                parse_mode='Markdown'
            )
    
    async def handle_favorite_action(self, query, data: str) -> None:
        """Обработка действий с избранным"""
        parts = data.split("_")
        
        if len(parts) >= 3:
            action = parts[0]  # fav
            item_type = parts[1]  # qa, material, article, tip
            item_id = int(parts[2])
            user_id = query.from_user.id
            
            if self.db.add_favorite(user_id, item_type, item_id):
                await query.answer("✅ Добавлено в избранное")
            else:
                await query.answer("⚠️ Уже в избранном")
        else:
            # Показать избранное по типу
            fav_type = data.replace("fav_", "")
            await self.show_favorites_list(query, fav_type)
    
    async def show_favorites_list(self, query, fav_type: str) -> None:
        """Показать список избранного"""
        user_id = query.from_user.id
        favorites = self.db.get_favorites(user_id, fav_type)
        
        if favorites:
            response = f"⭐ *Избранное ({fav_type})*\n\n"
            keyboard = []
            
            for fav in favorites[:10]:
                response += f"• {fav.get('title', 'Без названия')[:50]}...\n"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"📌 {fav.get('title', 'Элемент')[:30]}...",
                        callback_data=f"{fav['item_type']}_{fav['item_id']}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("🗑️ Удалить все", callback_data=f"fav_clear_{fav_type}_confirm"),
                InlineKeyboardButton("◀️ Назад", callback_data="favorites_main")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"⭐ *Избранное ({fav_type})*\n\nЗдесь пока пусто.",
                reply_markup=Keyboards.back_to_menu(),
                parse_mode='Markdown'
            )
    
    async def handle_admin_action(self, query, action: str) -> None:
        """Обработка действий админа"""
        user_id = query.from_user.id
        
        if user_id != ADMIN_ID:
            await query.edit_message_text("❌ Доступ запрещен")
            return
        
        action_type = action.replace("admin_", "")
        
        if action_type == "stats":
            await self.stats(query, context)
        elif action_type == "backup":
            backup_path = self.db.backup_database()
            await query.edit_message_text(
                f"💾 *Резервная копия создана*\n\n"
                f"Файл: `{backup_path}`\n"
                f"Время: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='Markdown'
            )
        elif action_type == "export":
            await query.edit_message_text(
                "📤 *Экспорт данных*\n\n"
                "Функция в разработке...",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"⚙️ *Админ действие: {action_type}*\n\n"
                "Функция в разработке...",
                parse_mode='Markdown'
            )