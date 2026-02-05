"""
КАЛЬКУЛЯТОРЫ v12.0
10+ калькуляторов с реальными расчетами
"""

import math
import re
from typing import Dict, List, Tuple, Optional
from config import PRICES, CATEGORIES

class ConstructionCalculators:
    """Класс калькуляторов для строительства"""
    
    @staticmethod
    def calculate_foundation(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор фундамента
        Формат: длина ширина глубина тип
        Пример: 10 8 1.5 ленточный
        """
        if len(params) < 4:
            return {"error": "Недостаточно параметров. Формат: длина ширина глубина тип"}
        
        try:
            length = float(params[0])  # м
            width = float(params[1])   # м
            depth = float(params[2])   # м
            f_type = params[3].lower()  # тип
            
            # Расчет объема
            volume = length * width * depth  # м³
            
            # Расчет материалов
            if f_type == "ленточный":
                # Для ленточного: периметр × ширина × глубина
                perimeter = (length + width) * 2
                volume = perimeter * 0.5 * depth  # ширина ленты 0.5 м
                
                # Материалы
                concrete = volume * 1.05  # +5% на потери
                rebar = volume * 100  # кг/м³
                formwork = perimeter * depth * 2  # м²
                
                # Стоимость
                concrete_cost = concrete * PRICES.get("materials_beton", 4500)
                rebar_cost = rebar * 45  # 45 руб/кг
                work_cost = volume * PRICES.get("fundament_lenta", 3500)
                
                total_cost = concrete_cost + rebar_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Ленточный фундамент",
                    "parameters": {
                        "Длина": f"{length} м",
                        "Ширина": f"{width} м", 
                        "Глубина": f"{depth} м",
                        "Периметр": f"{perimeter} м"
                    },
                    "materials": {
                        "Бетон М300": f"{concrete:.1f} м³",
                        "Арматура Ø12": f"{rebar:.0f} кг",
                        "Опалубка": f"{formwork:.1f} м²"
                    },
                    "cost": {
                        "Бетон": f"{concrete_cost:,.0f} руб",
                        "Арматура": f"{rebar_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "V = П × Ш × Г, где П - периметр, Ш - ширина ленты, Г - глубина"
                }
                
            elif f_type == "плитный":
                # Для плитного: площадь × толщина
                area = length * width
                volume = area * 0.3  # толщина плиты 0.3 м
                
                # Материалы
                concrete = volume * 1.05
                rebar = volume * 120  # больше арматуры для плиты
                insulation = area  # м² утеплителя
                
                # Стоимость
                concrete_cost = concrete * PRICES.get("materials_beton", 4500)
                rebar_cost = rebar * 45
                insulation_cost = insulation * 350  # руб/м²
                work_cost = volume * PRICES.get("fundament_plita", 4500)
                
                total_cost = concrete_cost + rebar_cost + insulation_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Плитный фундамент (УШП)",
                    "parameters": {
                        "Длина": f"{length} м",
                        "Ширина": f"{width} м",
                        "Толщина": "0.3 м",
                        "Площадь": f"{area:.1f} м²"
                    },
                    "materials": {
                        "Бетон М300": f"{concrete:.1f} м³",
                        "Арматура Ø12-16": f"{rebar:.0f} кг",
                        "Утеплитель 100 мм": f"{insulation:.1f} м²"
                    },
                    "cost": {
                        "Бетон": f"{concrete_cost:,.0f} руб",
                        "Арматура": f"{rebar_cost:,.0f} руб",
                        "Утеплитель": f"{insulation_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "V = Д × Ш × Т, где Т - толщина плиты"
                }
                
            else:
                return {"error": f"Неизвестный тип фундамента: {f_type}. Доступно: ленточный, плитный"}
                
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_walls(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор стен
        Формат: периметр высота толщина материал
        Пример: 40 3 0.4 газобетон
        """
        if len(params) < 4:
            return {"error": "Недостаточно параметров. Формат: периметр высота толщина материал"}
        
        try:
            perimeter = float(params[0])  # м
            height = float(params[1])     # м
            thickness = float(params[2])  # м
            material = params[3].lower()  # материал
            
            # Расчет площади стен
            area = perimeter * height  # м²
            
            # Расчет материалов в зависимости от материала
            if material == "газобетон":
                # Газоблок 600×300×200 мм = 0.036 м³
                block_volume = 0.6 * 0.3 * 0.2  # м³
                blocks_per_m2 = thickness / 0.3  # количество блоков в толщине
                blocks_count = area * blocks_per_m2
                
                # Материалы
                blocks = blocks_count
                glue = area * 0.03  # кг/м²
                rebar = perimeter / 0.5 * 4 * height  # м арматуры для армирования
                
                # Стоимость
                blocks_cost = blocks * 150  # руб/блок
                glue_cost = glue * 25  # руб/кг
                work_cost = area * PRICES.get("walls_gas", 1800)
                
                total_cost = blocks_cost + glue_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Стены из газобетона",
                    "parameters": {
                        "Периметр": f"{perimeter} м",
                        "Высота": f"{height} м",
                        "Толщина": f"{thickness} м",
                        "Площадь": f"{area:.1f} м²"
                    },
                    "materials": {
                        "Газоблок D500 600×300×200": f"{blocks:.0f} шт",
                        "Клей для газобетона": f"{glue:.0f} кг",
                        "Арматура Ø8": f"{rebar:.0f} м"
                    },
                    "cost": {
                        "Газоблоки": f"{blocks_cost:,.0f} руб",
                        "Клей": f"{glue_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "Кол-во = S / (0.6×0.3) × (Т/0.3), где S - площадь, Т - толщина"
                }
                
            elif material == "кирпич":
                # Кирпич 250×120×65 мм
                # Кладка в 2 кирпича = 510 мм
                bricks_per_m2 = 102  # шт/м² при толщине 510 мм
                bricks_count = area * bricks_per_m2 * (thickness / 0.51)
                
                # Материалы
                bricks = bricks_count
                mortar = area * 0.25 * (thickness / 0.51)  # м³ раствора
                
                # Стоимость
                bricks_cost = bricks * PRICES.get("materials_kirpich", 35)
                mortar_cost = mortar * 3500  # руб/м³ раствора
                work_cost = area * PRICES.get("walls_brick", 2500)
                
                total_cost = bricks_cost + mortar_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Кирпичные стены",
                    "parameters": {
                        "Периметр": f"{perimeter} м",
                        "Высота": f"{height} м",
                        "Толщина": f"{thickness} м",
                        "Площадь": f"{area:.1f} м²"
                    },
                    "materials": {
                        "Кирпич М150": f"{bricks:.0f} шт",
                        "Раствор М100": f"{mortar:.1f} м³"
                    },
                    "cost": {
                        "Кирпич": f"{bricks_cost:,.0f} руб",
                        "Раствор": f"{mortar_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "Кол-во = S × 102 × (Т/0.51), где 102 - кирпичей в м² при толщине 510 мм"
                }
                
            elif material == "дерево":
                # Брус 150×150 мм
                beam_length = perimeter * height / (0.15 * 0.15)  # м погонных
                beams_count = beam_length / 6  # 6м брусья
                
                # Материалы
                beams = beams_count
                insulation = area  # м² утеплителя
                windproof = area  # м² ветрозащиты
                
                # Стоимость
                beams_cost = beams * 6000  # руб/брус 6м
                insulation_cost = insulation * 350  # руб/м²
                work_cost = area * PRICES.get("walls_wood", 3000)
                
                total_cost = beams_cost + insulation_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Деревянные стены (брус)",
                    "parameters": {
                        "Периметр": f"{perimeter} м",
                        "Высота": f"{height} м",
                        "Толщина": f"{thickness} м",
                        "Площадь": f"{area:.1f} м²"
                    },
                    "materials": {
                        "Брус 150×150×6000": f"{beams:.0f} шт",
                        "Утеплитель 150 мм": f"{insulation:.0f} м²",
                        "Ветрозащита": f"{windproof:.0f} м²"
                    },
                    "cost": {
                        "Брус": f"{beams_cost:,.0f} руб",
                        "Утеплитель": f"{insulation_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "Кол-во = (П × В) / (0.15×0.15) / 6, где 0.15 - сечение бруса, 6 - длина бруса"
                }
                
            else:
                return {"error": f"Неизвестный материал: {material}. Доступно: газобетон, кирпич, дерево"}
                
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_roof(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор крыши
        Формат: длина ширина уклон материал
        Пример: 10 8 30 металлочерепица
        """
        if len(params) < 4:
            return {"error": "Недостаточно параметров. Формат: длина ширина уклон материал"}
        
        try:
            length = float(params[0])  # м
            width = float(params[1])   # м
            angle = float(params[2])   # градусы
            material = params[3].lower()  # материал
            
            # Расчет площади крыши с учетом уклона
            roof_length = width / (2 * math.cos(math.radians(angle)))  # длина ската
            area = length * roof_length * 2  # площадь двух скатов
            
            # Расчет материалов кровли
            if material == "металлочерепица":
                # Материалы
                roofing = area * 1.1  # +10% на нахлест
                waterproofing = area  # м²
                insulation = area  # м² утеплителя
                battens = area * 1.2  # м² обрешетки
                
                # Стоимость
                roofing_cost = roofing * PRICES.get("roof_metal", 450)
                waterproofing_cost = waterproofing * 40  # руб/м²
                insulation_cost = insulation * 350  # руб/м²
                work_cost = area * 800  # руб/м²
                
                total_cost = roofing_cost + waterproofing_cost + insulation_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Крыша из металлочерепицы",
                    "parameters": {
                        "Длина": f"{length} м",
                        "Ширина": f"{width} м",
                        "Уклон": f"{angle}°",
                        "Площадь крыши": f"{area:.1f} м²",
                        "Длина ската": f"{roof_length:.1f} м"
                    },
                    "materials": {
                        "Металлочерепица": f"{roofing:.1f} м²",
                        "Гидроизоляция": f"{waterproofing:.1f} м²",
                        "Утеплитель 200 мм": f"{insulation:.1f} м²",
                        "Обрешетка": f"{battens:.1f} м²"
                    },
                    "cost": {
                        "Металлочерепица": f"{roofing_cost:,.0f} руб",
                        "Гидроизоляция": f"{waterproofing_cost:,.0f} руб",
                        "Утеплитель": f"{insulation_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "S = Д × (Ш / (2 × cos(α))) × 2, где α - угол уклона"
                }
                
            elif material == "мягкая":
                # Для мягкой кровли
                roofing = area * 1.15  # +15% на нахлест
                osb = area  # м² ОСП
                insulation = area  # м² утеплителя
                
                # Стоимость
                roofing_cost = roofing * PRICES.get("roof_soft", 550)
                osb_cost = osb * 500  # руб/м²
                insulation_cost = insulation * 350
                work_cost = area * 1000  # руб/м²
                
                total_cost = roofing_cost + osb_cost + insulation_cost + work_cost
                
                return {
                    "success": True,
                    "type": "Мягкая кровля (битумная черепица)",
                    "parameters": {
                        "Длина": f"{length} м",
                        "Ширина": f"{width} м",
                        "Уклон": f"{angle}°",
                        "Площадь крыши": f"{area:.1f} м²"
                    },
                    "materials": {
                        "Битумная черепица": f"{roofing:.1f} м²",
                        "ОСП-3 9мм": f"{osb:.1f} м²",
                        "Утеплитель": f"{insulation:.1f} м²"
                    },
                    "cost": {
                        "Черепица": f"{roofing_cost:,.0f} руб",
                        "ОСП": f"{osb_cost:,.0f} руб",
                        "Утеплитель": f"{insulation_cost:,.0f} руб",
                        "Работа": f"{work_cost:,.0f} руб",
                        "Итого": f"{total_cost:,.0f} руб"
                    },
                    "formula": "Мягкая кровля требует сплошного основания из ОСП"
                }
                
            else:
                return {"error": f"Неизвестный материал: {material}. Доступно: металлочерепица, мягкая"}
                
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_heat_loss(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор теплопотерь
        Формат: площадь этажи регион утепление
        Пример: 150 2 москва хорошее
        """
        if len(params) < 4:
            return {"error": "Недостаточно параметров. Формат: площадь этажи регион утепление"}
        
        try:
            area = float(params[0])  # м²
            floors = int(params[1])  # этажи
            region = params[2].lower()  # регион
            insulation = params[3].lower()  # качество утепления
            
            # Коэффициенты для регионов (Вт/м²·°C)
            region_coefficients = {
                "москва": 45,  # разница температур зимой
                "спб": 43,
                "екатеринбург": 47,
                "новосибирск": 50,
                "сочи": 30,
                "краснодар": 35
            }
            
            # Коэффициенты утепления
            insulation_coefficients = {
                "нет": 2.0,
                "слабое": 1.5,
                "среднее": 1.2,
                "хорошее": 0.9,
                "отличное": 0.7
            }
            
            # Расчет
            delta_t = region_coefficients.get(region, 45)  # разница температур
            k = insulation_coefficients.get(insulation, 1.2)  # коэффициент теплопотерь
            
            # Общая площадь ограждающих конструкций
            # Приблизительно: стены = периметр × высота × этажи
            # Для упрощения: умножаем площадь на коэффициент
            envelope_area = area * 3.5  # примерный коэффициент
            
            # Теплопотери
            heat_loss = envelope_area * delta_t * k / 1000  # кВт
            
            # Мощность котла с запасом 20%
            boiler_power = heat_loss * 1.2
            
            # Расчет стоимости утепления
            insulation_cost = 0
            if insulation == "хорошее":
                insulation_cost = area * PRICES.get("heat_loss", 1500)
            elif insulation == "отличное":
                insulation_cost = area * 2000
            
            return {
                "success": True,
                "type": "Расчет теплопотерь",
                "parameters": {
                    "Площадь дома": f"{area} м²",
                    "Этажи": floors,
                    "Регион": region.capitalize(),
                    "Качество утепления": insulation,
                    "ΔT (разница температур)": f"{delta_t}°C",
                    "Коэффициент k": k
                },
                "results": {
                    "Теплопотери дома": f"{heat_loss:.1f} кВт",
                    "Рекомендуемая мощность котла": f"{boiler_power:.1f} кВт",
                    "Стоимость утепления": f"{insulation_cost:,.0f} руб" if insulation_cost > 0 else "Не требуется"
                },
                "recommendations": [
                    f"Для дома {area} м² в {region} рекомендуется котел {math.ceil(boiler_power)} кВт",
                    f"Ежемесячные затраты на отопление: ~{heat_loss * 0.1 * 720 * 30 / 1000:,.0f} руб/мес (газ)",
                    "Установите терморегуляторы для экономии 10-15%"
                ],
                "formula": "Q = S × ΔT × k / 1000, где Q - теплопотери (кВт), S - площадь (м²), ΔT - разница температур, k - коэффициент"
            }
            
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_cost(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор стоимости работ
        Формат: работа площадь материал качество
        Пример: фундамент 100 ленточный стандарт
        """
        if len(params) < 4:
            return {"error": "Недостаточно параметров. Формат: работа площадь материал качество"}
        
        work = params[0].lower()
        area = float(params[1])
        material = params[2].lower()
        quality = params[3].lower()
        
        # Коэффициенты качества
        quality_coefficients = {
            "эконом": 0.7,
            "стандарт": 1.0,
            "премиум": 1.5
        }
        
        quality_coef = quality_coefficients.get(quality, 1.0)
        
        if work == "фундамент":
            if material == "ленточный":
                base_price = PRICES.get("fundament_lenta", 3500)
            elif material == "плитный":
                base_price = PRICES.get("fundament_plita", 4500)
            else:
                return {"error": f"Неизвестный тип фундамента: {material}"}
            
            total_cost = area * base_price * quality_coef
            
            return {
                "success": True,
                "type": f"Стоимость {work} ({material})",
                "parameters": {
                    "Площадь/объем": f"{area} м²/м³",
                    "Материал": material,
                    "Качество": quality,
                    "Коэффициент": quality_coef
                },
                "cost": {
                    "Базовая цена": f"{base_price} руб/ед.",
                    "Общая стоимость": f"{total_cost:,.0f} руб",
                    "Стоимость с материалами": f"{total_cost * 1.5:,.0f} руб (материалы + работа)"
                }
            }
        
        elif work == "стены":
            if material == "кирпич":
                base_price = PRICES.get("walls_brick", 2500)
            elif material == "газобетон":
                base_price = PRICES.get("walls_gas", 1800)
            elif material == "дерево":
                base_price = PRICES.get("walls_wood", 3000)
            else:
                return {"error": f"Неизвестный материал стен: {material}"}
            
            total_cost = area * base_price * quality_coef
            
            return {
                "success": True,
                "type": f"Стоимость {work} ({material})",
                "parameters": {
                    "Площадь стен": f"{area} м²",
                    "Материал": material,
                    "Качество": quality
                },
                "cost": {
                    "Базовая цена": f"{base_price} руб/м²",
                    "Работа": f"{total_cost:,.0f} руб",
                    "Материалы": f"{total_cost * 1.8:,.0f} руб",
                    "Итого": f"{total_cost * 2.8:,.0f} руб"
                }
            }
        
        elif work == "крыша":
            if material == "металлочерепица":
                base_price = 1300  # работа + материалы
            elif material == "мягкая":
                base_price = 1700
            else:
                return {"error": f"Неизвестный материал кровли: {material}"}
            
            total_cost = area * base_price * quality_coef
            
            return {
                "success": True,
                "type": f"Стоимость {work} ({material})",
                "parameters": {
                    "Площадь крыши": f"{area} м²",
                    "Материал": material,
                    "Качество": quality
                },
                "cost": {
                    "Работа + материалы": f"{total_cost:,.0f} руб",
                    "Стропильная система": f"{area * 800:,.0f} руб",
                    "Утепление": f"{area * 500:,.0f} руб",
                    "Итого": f"{total_cost + area * 1300:,.0f} руб"
                }
            }
        
        elif work == "отделка":
            if quality == "эконом":
                base_price = 2000
            elif quality == "стандарт":
                base_price = 3500
            elif quality == "премиум":
                base_price = 6000
            else:
                base_price = 3500
            
            total_cost = area * base_price
            
            return {
                "success": True,
                "type": f"Стоимость {work} ({quality})",
                "parameters": {
                    "Площадь": f"{area} м²",
                    "Качество": quality
                },
                "cost": {
                    "Черновая отделка": f"{area * 1500:,.0f} руб",
                    "Чистовая отделка": f"{total_cost:,.0f} руб",
                    "Сантехника": f"{area * 1000:,.0f} руб",
                    "Электрика": f"{area * 800:,.0f} руб",
                    "Итого": f"{total_cost + area * 3300:,.0f} руб"
                }
            }
        
        else:
            return {"error": f"Неизвестный тип работ: {work}. Доступно: фундамент, стены, крыша, отделка"}
    
    @staticmethod
    def calculate_area_volume(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор площади и объема
        Формат: фигура параметры
        Примеры: 
          прямоугольник 10 5
          треугольник 6 4  
          круг 3
          параллелепипед 5 4 3
          цилиндр 2 5
        """
        if len(params) < 2:
            return {"error": "Недостаточно параметров. Формат: фигура параметры"}
        
        shape = params[0].lower()
        
        try:
            if shape == "прямоугольник":
                if len(params) < 3:
                    return {"error": "Для прямоугольника нужны длина и ширина"}
                
                a = float(params[1])
                b = float(params[2])
                area = a * b
                perimeter = (a + b) * 2
                
                return {
                    "success": True,
                    "type": "Прямоугольник",
                    "parameters": {
                        "Длина": f"{a} м",
                        "Ширина": f"{b} м"
                    },
                    "results": {
                        "Площадь": f"{area} м²",
                        "Периметр": f"{perimeter} м"
                    },
                    "formula": "S = a × b, P = (a + b) × 2"
                }
            
            elif shape == "треугольник":
                if len(params) < 3:
                    return {"error": "Для треугольника нужны основание и высота"}
                
                a = float(params[1])  # основание
                h = float(params[2])  # высота
                area = (a * h) / 2
                
                return {
                    "success": True,
                    "type": "Треугольник",
                    "parameters": {
                        "Основание": f"{a} м",
                        "Высота": f"{h} м"
                    },
                    "results": {
                        "Площадь": f"{area} м²"
                    },
                    "formula": "S = (a × h) / 2"
                }
            
            elif shape == "круг":
                r = float(params[1])
                area = math.pi * r ** 2
                circumference = 2 * math.pi * r
                
                return {
                    "success": True,
                    "type": "Круг",
                    "parameters": {
                        "Радиус": f"{r} м"
                    },
                    "results": {
                        "Площадь": f"{area:.2f} м²",
                        "Длина окружности": f"{circumference:.2f} м"
                    },
                    "formula": "S = π × r², C = 2 × π × r"
                }
            
            elif shape == "параллелепипед":
                if len(params) < 4:
                    return {"error": "Для параллелепипеда нужны длина, ширина и высота"}
                
                a = float(params[1])
                b = float(params[2])
                c = float(params[3])
                volume = a * b * c
                surface_area = 2 * (a*b + a*c + b*c)
                
                return {
                    "success": True,
                    "type": "Параллелепипед (прямоугольный)",
                    "parameters": {
                        "Длина": f"{a} м",
                        "Ширина": f"{b} м",
                        "Высота": f"{c} м"
                    },
                    "results": {
                        "Объем": f"{volume} м³",
                        "Площадь поверхности": f"{surface_area} м²"
                    },
                    "formula": "V = a × b × c, S = 2 × (ab + ac + bc)"
                }
            
            elif shape == "цилиндр":
                if len(params) < 3:
                    return {"error": "Для цилиндра нужны радиус и высота"}
                
                r = float(params[1])
                h = float(params[2])
                volume = math.pi * r ** 2 * h
                surface_area = 2 * math.pi * r * (r + h)
                
                return {
                    "success": True,
                    "type": "Цилиндр",
                    "parameters": {
                        "Радиус": f"{r} м",
                        "Высота": f"{h} м"
                    },
                    "results": {
                        "Объем": f"{volume:.2f} м³",
                        "Площадь поверхности": f"{surface_area:.2f} м²"
                    },
                    "formula": "V = π × r² × h, S = 2 × π × r × (r + h)"
                }
            
            else:
                return {"error": f"Неизвестная фигура: {shape}. Доступно: прямоугольник, треугольник, круг, параллелепипед, цилиндр"}
                
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_water_supply(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор водоснабжения
        Формат: люди сантехника расход
        Пример: 4 ванна+душ 200
        """
        if len(params) < 3:
            return {"error": "Недостаточно параметров. Формат: люди сантехника расход"}
        
        try:
            people = int(params[0])
            plumbing = params[1].lower()
            daily_use = float(params[2])  # л/сутки на человека
            
            # Расчет потребления
            total_daily = people * daily_use  # л/сутки
            
            # Расчет септика
            # Объем септика = суточный расход × 3 дня отстоя
            septic_volume = total_daily * 3 / 1000  # м³
            
            # Расчет водонагревателя
            # Для семьи 4 человек: 80-100 литров
            boiler_volume = max(50, people * 20)  # литров
            
            # Стоимость
            septic_cost = septic_volume * 30000  # 30 тыс руб/м³
            boiler_cost = boiler_volume * 50  # 50 руб/литр
            piping_cost = people * 15000  # разводка труб
            
            total_cost = septic_cost + boiler_cost + piping_cost
            
            return {
                "success": True,
                "type": "Расчет водоснабжения и канализации",
                "parameters": {
                    "Количество человек": people,
                    "Сантехника": plumbing,
                    "Норма расхода": f"{daily_use} л/чел/сутки"
                },
                "results": {
                    "Суточное потребление": f"{total_daily} л/сутки",
                    "Объем септика": f"{septic_volume:.1f} м³",
                    "Объем водонагревателя": f"{boiler_volume} л",
                    "Рекомендуемый насос": "Насосная станция 60-80 Вт" if people <= 4 else "Насосная станция 100-150 Вт"
                },
                "cost": {
                    "Септик": f"{septic_cost:,.0f} руб",
                    "Водонагреватель": f"{boiler_cost:,.0f} руб",
                    "Разводка труб": f"{piping_cost:,.0f} руб",
                    "Итого": f"{total_cost:,.0f} руб"
                },
                "recommendations": [
                    f"Для {people} человек рекомендуем септик объемом {math.ceil(septic_volume)} м³",
                    f"Водонагреватель на {boiler_volume} л (электрический или газовый)",
                    "Установите фильтры грубой и тонкой очистки"
                ]
            }
            
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_electric(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор электрики
        Формат: мощность напряжение фазы
        Пример: 15 220 1
        """
        if len(params) < 3:
            return {"error": "Недостаточно параметров. Формат: мощность напряжение фазы"}
        
        try:
            power = float(params[0])  # кВт
            voltage = float(params[1])  # В
            phases = int(params[2])  # 1 или 3
            
            # Расчет тока
            if phases == 1:
                # Однофазная сеть: I = P / (U × cosφ)
                cos_phi = 0.9  # коэффициент мощности
                current = (power * 1000) / (voltage * cos_phi)  # А
            else:
                # Трехфазная сеть: I = P / (√3 × U × cosφ)
                cos_phi = 0.85
                current = (power * 1000) / (1.732 * voltage * cos_phi)
            
            # Выбор сечения провода по току
            if current <= 16:
                cable = "3×1.5 мм²"
                breaker = "10А" if current <= 10 else "16А"
            elif current <= 25:
                cable = "3×2.5 мм²"
                breaker = "16А" if current <= 16 else "20А"
            elif current <= 32:
                cable = "3×4 мм²"
                breaker = "25А" if current <= 25 else "32А"
            elif current <= 40:
                cable = "3×6 мм²"
                breaker = "32А"
            else:
                cable = "3×10 мм²"
                breaker = "40А"
            
            # Стоимость
            cable_cost = power * 800  # руб/кВт
            panel_cost = power * 600  # руб/кВт
            work_cost = power * 400   # руб/кВт
            
            total_cost = cable_cost + panel_cost + work_cost
            
            return {
                "success": True,
                "type": "Расчет электрики",
                "parameters": {
                    "Мощность": f"{power} кВт",
                    "Напряжение": f"{voltage} В",
                    "Фаз": phases
                },
                "results": {
                    "Расчетный ток": f"{current:.1f} А",
                    "Сечение кабеля": cable,
                    "Автоматический выключатель": breaker,
                    "Рекомендуемый счетчик": f"{power * 1.5:.0f} А"
                },
                "cost": {
                    "Кабели и провода": f"{cable_cost:,.0f} руб",
                    "Щиток и автоматы": f"{panel_cost:,.0f} руб",
                    "Работа": f"{work_cost:,.0f} руб",
                    "Итого": f"{total_cost:,.0f} руб"
                },
                "formula": "I = P / (U × cosφ) для 1 фазы, I = P / (√3 × U × cosφ) для 3 фаз"
            }
            
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_concrete(params: List[str]) -> Dict[str, any]:
        """
        Калькулятор бетона
        Формат: объем марка добавки
        Пример: 10 М300 пластификатор
        """
        if len(params) < 2:
            return {"error": "Недостаточно параметров. Формат: объем марка [добавки]"}
        
        try:
            volume = float(params[0])  # м³
            grade = params[1].upper()  # М100, М200, М300
            additives = params[2] if len(params) > 2 else None
            
            # Состав бетона на 1 м³
            compositions = {
                "М100": {"цемент": 180, "песок": 840, "щебень": 1050, "вода": 210},
                "М150": {"цемент": 220, "песок": 780, "щебень": 1080, "вода": 190},
                "М200": {"цемент": 280, "песок": 740, "щебень": 1100, "вода": 180},
                "М250": {"цемент": 330, "песок": 700, "щебень": 1120, "вода": 170},
                "М300": {"цемент": 380, "песок": 645, "щебень": 1080, "вода": 190},
                "М350": {"цемент": 420, "песок": 590, "щебень": 1090, "вода": 180}
            }
            
            if grade not in compositions:
                return {"error": f"Неизвестная марка бетона: {grade}. Доступно: {', '.join(compositions.keys())}"}
            
            comp = compositions[grade]
            
            # Расчет материалов
            cement = comp["цемент"] * volume
            sand = comp["песок"] * volume
            gravel = comp["щебень"] * volume
            water = comp["вода"] * volume
            
            # Стоимость
            cement_cost = cement * 12.5  # 12.5 руб/кг
            sand_cost = sand * 0.8  # 0.8 руб/кг
            gravel_cost = gravel * 1.2  # 1.2 руб/кг
            additives_cost = 0
            
            if additives:
                if "пластификатор" in additives.lower():
                    additives_cost = volume * 500  # руб/м³
                elif "противоморозный" in additives.lower():
                    additives_cost = volume * 800
            
            material_cost = cement_cost + sand_cost + gravel_cost + additives_cost
            work_cost = volume * 1500  # руб/м³ работы
            
            total_cost = material_cost + work_cost
            
            return {
                "success": True,
                "type": f"Расчет бетона {grade}",
                "parameters": {
                    "Объем": f"{volume} м³",
                    "Марка": grade,
                    "Добавки": additives if additives else "нет"
                },
                "materials": {
                    "Цемент М500": f"{cement:.0f} кг",
                    "Песок": f"{sand:.0f} кг",
                    "Щебень 20-40": f"{gravel:.0f} кг",
                    "Вода": f"{water:.0f} л"
                },
                "cost": {
                    "Цемент": f"{cement_cost:,.0f} руб",
                    "Песок": f"{sand_cost:,.0f} руб",
                    "Щебень": f"{gravel_cost:,.0f} руб",
                    "Добавки": f"{additives_cost:,.0f} руб" if additives_cost > 0 else "0 руб",
                    "Работа": f"{work_cost:,.0f} руб",
                    "Итого": f"{total_cost:,.0f} руб",
                    "Цена за м³": f"{total_cost/volume:,.0f} руб"
                },
                "notes": [
                    "Все пропорции указаны в кг на 1 м³ готового бетона",
                    "Для точного расчета нужны лабораторные испытания",
                    "Готовый товарный бетон стоит 4500-5500 руб/м³"
                ]
            }
            
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def calculate_materials(params: List[str]) -> Dict[str, any]:
        """
        Универсальный калькулятор материалов
        Формат: материал площадь/объем толщина
        Примеры: 
          бетон 30 м³ фундамент
          кирпич 100 м² стена
          утеплитель 50 м² 100 мм
        """
        if len(params) < 3:
            return {"error": "Недостаточно параметров. Формат: материал количество единица [толщина]"}
        
        material = params[0].lower()
        quantity = float(params[1])
        unit = params[2].lower()
        
        try:
            if material == "бетон":
                # Бетон в м³
                if unit != "м³":
                    return {"error": "Для бетона используйте м³"}
                
                cement = quantity * 380  # кг
                sand = quantity * 645    # кг
                gravel = quantity * 1080 # кг
                
                return {
                    "success": True,
                    "type": "Расчет материалов для бетона М300",
                    "parameters": {
                        "Объем": f"{quantity} м³",
                        "Марка": "М300"
                    },
                    "materials": {
                        "Цемент М500": f"{cement:.0f} кг",
                        "Песок": f"{sand:.0f} кг", 
                        "Щебень 20-40": f"{gravel:.0f} кг",
                        "Вода": f"{quantity * 190:.0f} л"
                    },
                    "cost": {
                        "Материалы": f"{quantity * 2500:,.0f} руб",
                        "Работа": f"{quantity * 1500:,.0f} руб",
                        "Итого": f"{quantity * 4000:,.0f} руб"
                    }
                }
            
            elif material == "кирпич":
                # Кирпич для стен
                if unit != "м²":
                    return {"error": "Для кирпича используйте м²"}
                
                # Кирпичей в м² при толщине 510 мм (2 кирпича)
                bricks = quantity * 102
                mortar = quantity * 0.05  # м³ раствора
                
                return {
                    "success": True,
                    "type": "Расчет кирпича для стен",
                    "parameters": {
                        "Площадь стен": f"{quantity} м²",
                        "Толщина": "510 мм (2 кирпича)"
                    },
                    "materials": {
                        "Кирпич М150": f"{bricks:.0f} шт",
                        "Раствор М100": f"{mortar:.2f} м³"
                    },
                    "cost": {
                        "Кирпич": f"{bricks * 30:,.0f} руб",
                        "Раствор": f"{mortar * 3500:,.0f} руб",
                        "Итого": f"{bricks * 30 + mortar * 3500:,.0f} руб"
                    }
                }
            
            elif material == "утеплитель":
                # Утеплитель
                if unit != "м²":
                    return {"error": "Для утеплителя используйте м²"}
                
                if len(params) < 4:
                    return {"error": "Для утеплителя укажите толщину (мм)"}
                
                thickness = float(params[3])  # мм
                volume = quantity * thickness / 1000  # м³ утеплителя
                
                # Для минваты плотностью 30 кг/м³
                weight = volume * 30  # кг
                
                return {
                    "success": True,
                    "type": "Расчет утеплителя",
                    "parameters": {
                        "Площадь": f"{quantity} м²",
                        "Толщина": f"{thickness} мм",
                        "Объем": f"{volume:.2f} м³"
                    },
                    "materials": {
                        "Минеральная вата": f"{weight:.0f} кг",
                        "Пароизоляция": f"{quantity:.0f} м²",
                        "Крепеж": f"{quantity * 6:.0f} шт дюбелей"
                    },
                    "cost": {
                        "Утеплитель": f"{quantity * 350:,.0f} руб",
                        "Пароизоляция": f"{quantity * 40:,.0f} руб",
                        "Работа": f"{quantity * 250:,.0f} руб",
                        "Итого": f"{quantity * 640:,.0f} руб"
                    }
                }
            
            elif material == "краска":
                # Краска для стен
                if unit != "м²":
                    return {"error": "Для краски используйте м²"}
                
                # Расход краски 1 л на 10 м² в 2 слоя
                paint = quantity * 0.2  # литров
                
                return {
                    "success": True,
                    "type": "Расчет краски для стен",
                    "parameters": {
                        "Площадь": f"{quantity} м²",
                        "Слоев": "2"
                    },
                    "materials": {
                        "Водоэмульсионная краска": f"{paint:.1f} л",
                        "Грунтовка": f"{quantity * 0.1:.1f} л",
                        "Валики, кисти": "1 набор"
                    },
                    "cost": {
                        "Краска": f"{paint * 300:,.0f} руб",
                        "Грунтовка": f"{quantity * 0.1 * 150:,.0f} руб",
                        "Итого": f"{paint * 300 + quantity * 15:,.0f} руб"
                    }
                }
            
            else:
                return {"error": f"Неизвестный материал: {material}. Доступно: бетон, кирпич, утеплитель, краска"}
                
        except ValueError:
            return {"error": "Некорректные числовые значения"}
    
    @staticmethod
    def parse_calc_command(text: str) -> Tuple[str, List[str], Optional[Dict]]:
        """
        Парсит команду калькулятора и возвращает результат
        """
        parts = text.strip().split()
        
        if not parts:
            return "empty", [], {"error": "Введите команду для калькулятора"}
        
        calc_type = parts[0].lower()
        params = parts[1:] if len(parts) > 1 else []
        
        calculators = {
            "фундамент": ConstructionCalculators.calculate_foundation,
            "стены": ConstructionCalculators.calculate_walls,
            "крыша": ConstructionCalculators.calculate_roof,
            "теплопотери": ConstructionCalculators.calculate_heat_loss,
            "стоимость": ConstructionCalculators.calculate_cost,
            "площадь": ConstructionCalculators.calculate_area_volume,
            "водоснабжение": ConstructionCalculators.calculate_water_supply,
            "электрика": ConstructionCalculators.calculate_electric,
            "бетон": ConstructionCalculators.calculate_concrete,
            "материалы": ConstructionCalculators.calculate_materials,
            "фундамент": ConstructionCalculators.calculate_foundation,
            "крыша": ConstructionCalculators.calculate_roof,
            "тепло": ConstructionCalculators.calculate_heat_loss,
            "цена": ConstructionCalculators.calculate_cost,
            "вода": ConstructionCalculators.calculate_water_supply,
            "электрика": ConstructionCalculators.calculate_electric,
            "бетон": ConstructionCalculators.calculate_concrete
        }
        
        if calc_type in calculators:
            result = calculators[calc_type](params)
            return calc_type, params, result
        else:
            # Пробуем определить тип калькулятора по параметрам
            if any(word in text.lower() for word in ['длина', 'ширина', 'глубина', 'периметр']):
                if any(word in text.lower() for word in ['фундамент', 'бетон']):
                    result = ConstructionCalculators.calculate_foundation(params)
                    return "фундамент", params, result
                elif any(word in text.lower() for word in ['стен', 'кирпич', 'газобетон']):
                    result = ConstructionCalculators.calculate_walls(params)
                    return "стены", params, result
            
            return "unknown", params, {"error": f"Неизвестный калькулятор: {calc_type}. Используйте: фундамент, стены, крыша, теплопотери, стоимость, площадь, водоснабжение, электрика, бетон, материалы"}
    
    @staticmethod
    def format_result(calc_type: str, result: Dict) -> str:
        """Форматирует результат расчета в читаемый текст"""
        if "error" in result:
            return f"❌ *Ошибка:* {result['error']}"
        
        if not result.get("success", False):
            return "❌ *Ошибка расчета*"
        
        response = f"🧮 *Результат расчета ({result.get('type', calc_type)})*\n\n"
        
        # Параметры
        if "parameters" in result:
            response += "*Параметры:*\n"
            for key, value in result["parameters"].items():
                response += f"• {key}: {value}\n"
            response += "\n"
        
        # Материалы
        if "materials" in result:
            response += "*Материалы:*\n"
            for material, amount in result["materials"].items():
                response += f"• {material}: {amount}\n"
            response += "\n"
        
        # Стоимость
        if "cost" in result:
            response += "*Стоимость:*\n"
            for item, cost in result["cost"].items():
                response += f"• {item}: {cost}\n"
            response += "\n"
        
        # Результаты
        if "results" in result:
            response += "*Результаты:*\n"
            for key, value in result["results"].items():
                response += f"• {key}: {value}\n"
            response += "\n"
        
        # Рекомендации
        if "recommendations" in result:
            response += "*Рекомендации:*\n"
            for i, rec in enumerate(result["recommendations"], 1):
                response += f"{i}. {rec}\n"
            response += "\n"
        
        # Формула
        if "formula" in result:
            response += f"*Формула:* {result['formula']}\n"
        
        # Примечания
        if "notes" in result:
            response += "\n*Примечания:*\n"
            for note in result["notes"]:
                response += f"• {note}\n"
        
        return response
    
    @staticmethod
    def get_calc_help(calc_type: str = None) -> str:
        """Возвращает справку по калькуляторам"""
        if calc_type:
            helps = {
                "фундамент": "🧱 *Калькулятор фундамента*\nФормат: `длина ширина глубина тип`\nПример: `10 8 1.5 ленточный`\nТипы: ленточный, плитный",
                "стены": "🏠 *Калькулятор стен*\nФормат: `периметр высота толщина материал`\nПример: `40 3 0.4 газобетон`\nМатериалы: газобетон, кирпич, дерево",
                "крыша": "🏠 *Калькулятор крыши*\nФормат: `длина ширина уклон материал`\nПример: `10 8 30 металлочерепица`\nМатериалы: металлочерепица, мягкая",
                "теплопотери": "🔥 *Калькулятор теплопотерь*\nФормат: `площадь этажи регион утепление`\nПример: `150 2 москва хорошее`\nРегионы: москва, спб, екатеринбург",
                "стоимость": "💰 *Калькулятор стоимости*\nФормат: `работа площадь материал качество`\nПример: `фундамент 100 ленточный стандарт`\nКачество: эконом, стандарт, премиум",
                "площадь": "📏 *Калькулятор площади/объема*\nФормат: `фигура параметры`\nПримеры:\n`прямоугольник 10 5`\n`круг 3`\n`параллелепипед 5 4 3`",
                "водоснабжение": "💧 *Калькулятор водоснабжения*\nФормат: `люди сантехника расход`\nПример: `4 ванна+душ 200`",
                "электрика": "⚡ *Калькулятор электрики*\nФормат: `мощность напряжение фазы`\nПример: `15 220 1`",
                "бетон": "🧱 *Калькулятор бетона*\nФормат: `объем марка добавки`\nПример: `10 М300 пластификатор`",
                "материалы": "📦 *Калькулятор материалов*\nФормат: `материал площадь/объем толщина`\nПримеры:\n`бетон 30 м³`\n`кирпич 100 м²`\n`утеплитель 50 м² 100`"
            }
            
            return helps.get(calc_type, f"Справка по калькулятору '{calc_type}' не найдена")
        
        # Общая справка
        help_text = """
🧮 *ПОМОЩЬ ПО КАЛЬКУЛЯТОРАМ*

*Доступные калькуляторы:*

1. 🧱 *Фундамент* - расчет материалов и стоимости
   Команда: `фундамент 10 8 1.5 ленточный`

2. 🏠 *Стены* - расчет кирпича, газобетона, бруса
   Команда: `стены 40 3 0.4 газобетон`

3. 🏠 *Крыша* - расчет кровельных материалов
   Команда: `крыша 10 8 30 металлочерепица`

4. 🔥 *Теплопотери* - расчет мощности котла
   Команда: `теплопотери 150 2 москва хорошее`

5. 💰 *Стоимость* - расчет стоимости работ
   Команда: `стоимость фундамент 100 ленточный стандарт`

6. 📏 *Площадь/объем* - расчет геометрических фигур
   Команда: `площадь прямоугольник 10 5`

7. 💧 *Водоснабжение* - расчет септика, водонагревателя
   Команда: `водоснабжение 4 ванна+душ 200`

8. ⚡ *Электрика* - расчет сечения проводов
   Команда: `электрика 15 220 1`

9. 🧱 *Бетон* - расчет состава бетона
   Команда: `бетон 10 М300 пластификатор`

10. 📦 *Материалы* - расчет количества материалов
    Команда: `материалы бетон 30 м³`

*Примечание:*
• Все расчеты приблизительные
• Для точных расчетов нужен проект
• Цены указаны для средней полосы России
• Учитывайте региональные коэффициенты

*Пример полного расчета дома 100 м²:*
фундамент 10 10 1.5 ленточный
стены 40 3 0.4 газобетон
крыша 10 10 30 металлочерепица
теплопотери 100 1 москва хорошее
"""
        return help_text