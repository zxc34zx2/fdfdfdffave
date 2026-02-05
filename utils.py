"""
ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ v12.0
"""

import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def format_number(num: float) -> str:
    """Форматирование числа с разделителями"""
    return f"{num:,.0f}".replace(",", " ")

def parse_dimensions(text: str) -> List[float]:
    """Парсинг размеров из текста"""
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(n) for n in numbers]

def calculate_area(length: float, width: float) -> float:
    """Расчет площади прямоугольника"""
    return length * width

def calculate_volume(length: float, width: float, height: float) -> float:
    """Расчет объема параллелепипеда"""
    return length * width * height

def calculate_circle_area(radius: float) -> float:
    """Расчет площади круга"""
    return math.pi * radius ** 2

def calculate_triangle_area(base: float, height: float) -> float:
    """Расчет площади треугольника"""
    return (base * height) / 2

def estimate_construction_time(area: float, project_type: str) -> Dict[str, Any]:
    """Оценка времени строительства"""
    # Дни на м² для разных типов проектов
    days_per_m2 = {
        "дом": 0.8,
        "дача": 0.6,
        "баня": 0.7,
        "гараж": 0.4,
        "ремонт": 0.3
    }
    
    days = area * days_per_m2.get(project_type.lower(), 0.5)
    weeks = math.ceil(days / 7)
    months = math.ceil(days / 30)
    
    return {
        "days": math.ceil(days),
        "weeks": weeks,
        "months": months,
        "estimated_completion": (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
    }

def estimate_material_quantity(material_type: str, area: float, thickness: float = None) -> Dict[str, Any]:
    """Оценка количества материала"""
    # Нормы расхода материалов
    norms = {
        "кирпич": {"unit": "шт", "per_m2": 102, "notes": "При толщине 510 мм (2 кирпича)"},
        "газоблок": {"unit": "шт", "per_m2": 8.33, "notes": "Блоки 600×300×200 мм"},
        "бетон": {"unit": "м³", "per_m2": 0.3, "notes": "Для фундамента толщиной 300 мм"},
        "утеплитель": {"unit": "м²", "per_m2": 1.1, "notes": "+10% на отходы"},
        "краска": {"unit": "л", "per_m2": 0.2, "notes": "В 2 слоя"},
        "плитка": {"unit": "м²", "per_m2": 1.1, "notes": "+10% на подрезку"},
        "гипсокартон": {"unit": "лист", "per_m2": 0.33, "notes": "Лист 1.2×2.5 м = 3 м²"},
        "доска": {"unit": "м³", "per_m2": 0.015, "notes": "Доска 25×150 мм с шагом 400 мм"}
    }
    
    material_info = norms.get(material_type.lower())
    
    if not material_info:
        return {"error": f"Неизвестный материал: {material_type}"}
    
    quantity = area * material_info["per_m2"]
    
    if thickness and material_type == "утеплитель":
        # Для утеплителя учитываем толщину
        volume = area * thickness / 1000  # м³
        quantity = volume
    
    return {
        "material": material_type,
        "area": area,
        "quantity": quantity,
        "unit": material_info["unit"],
        "notes": material_info["notes"]
    }

def format_price_range(price_min: float, price_max: float, unit: str) -> str:
    """Форматирование диапазона цен"""
    if price_min == price_max:
        return f"{format_number(price_min)} руб/{unit}"
    else:
        return f"{format_number(price_min)} - {format_number(price_max)} руб/{unit}"

def calculate_mortgage(price: float, initial_payment: float, years: int, rate: float) -> Dict[str, Any]:
    """Расчет ипотеки"""
    loan_amount = price - initial_payment
    monthly_rate = rate / 12 / 100
    months = years * 12
    
    # Формула аннуитетного платежа
    monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    
    total_payment = monthly_payment * months
    overpayment = total_payment - loan_amount
    
    return {
        "loan_amount": loan_amount,
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "overpayment": overpayment,
        "overpayment_percent": (overpayment / loan_amount) * 100
    }

def get_seasonal_recommendations(month: int = None) -> List[str]:
    """Рекомендации по сезону"""
    if month is None:
        month = datetime.now().month
    
    recommendations = {
        1: ["Зимнее строительство требует специальных мер", "Используйте противоморозные добавки для бетона"],
        2: ["Подготовьте материалы к весеннему строительству", "Заключайте договоры с подрядчиками заранее"],
        3: ["Начало строительного сезона", "Проверьте фундамент после зимы"],
        4: ["Идеальное время для земляных работ", "Начинайте строительство каркаса"],
        5: ["Продолжайте основные строительные работы", "Установите окна и двери"],
        6: ["Завершайте коробку дома", "Начинайте кровельные работы"],
        7: ["Монтаж инженерных систем", "Внутренняя отделка"],
        8: ["Подготовка к осени", "Утепление и наружная отделка"],
        9: ["Завершение строительного сезона", "Подготовка к зиме"],
        10: ["Последние наружные работы", "Внутренняя отделка"],
        11: ["Подготовка к зиме", "Консервация стройки если не завершена"],
        12: ["Планирование на следующий год", "Закупка материалов по скидкам"]
    }
    
    return recommendations.get(month, ["Строительные работы возможны круглый год при соблюдении технологий"])

def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    # Российские номера: +7, 8, 7
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    return bool(re.match(pattern, phone))

def generate_password(length: int = 8) -> str:
    """Генерация случайного пароля"""
    import random
    import string
    
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def format_duration(seconds: float) -> str:
    """Форматирование длительности"""
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} мин"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} час"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Обрезка текста до максимальной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix