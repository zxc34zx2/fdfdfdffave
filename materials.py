"""
МЕНЕДЖЕР МАТЕРИАЛОВ v12.0
"""

from typing import List, Dict, Optional
from config import MATERIAL_CATEGORIES

class MaterialsManager:
    """Класс для работы с материалами"""
    
    def __init__(self, db):
        self.db = db
    
    def search_materials_advanced(self, query: str, category: str = None, 
                                 price_min: float = None, price_max: float = None,
                                 limit: int = 20) -> List[Dict]:
        """Расширенный поиск материалов"""
        conditions = []
        params = []
        
        if query:
            conditions.append("(name LIKE ? OR properties LIKE ? OR applications LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if category:
            conditions.append("category LIKE ?")
            params.append(f"%{category}%")
        
        if price_min is not None:
            conditions.append("price_avg >= ?")
            params.append(price_min)
        
        if price_max is not None:
            conditions.append("price_avg <= ?")
            params.append(price_max)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query_sql = f"""
        SELECT * FROM materials 
        WHERE {where_clause}
        ORDER BY popularity DESC, price_avg
        LIMIT ?
        """
        
        params.append(limit)
        
        self.db.cursor.execute(query_sql, params)
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def compare_materials(self, material_ids: List[int]) -> List[Dict]:
        """Сравнение нескольких материалов"""
        if not material_ids:
            return []
        
        placeholders = ','.join(['?' for _ in material_ids])
        query = f"""
        SELECT * FROM materials 
        WHERE id IN ({placeholders})
        ORDER BY price_avg
        """
        
        self.db.cursor.execute(query, material_ids)
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def get_material_suppliers(self, material_id: int) -> List[str]:
        """Получить поставщиков материала"""
        material = self.db.cursor.execute(
            "SELECT suppliers FROM materials WHERE id = ?", (material_id,)
        ).fetchone()
        
        if material and material['suppliers']:
            return [s.strip() for s in material['suppliers'].split(',')]
        return []
    
    def calculate_material_quantity(self, material_id: int, area: float, 
                                   thickness: float = None) -> Dict[str, any]:
        """Расчет количества материала для площади"""
        material = self.db.cursor.execute(
            "SELECT * FROM materials WHERE id = ?", (material_id,)
        ).fetchone()
        
        if not material:
            return {"error": "Материал не найден"}
        
        result = {
            "material": dict(material),
            "area": area,
            "thickness": thickness,
            "calculations": {}
        }
        
        # Расчет в зависимости от единицы измерения
        unit = material['unit']
        
        if unit == "м²":
            quantity = area
            if thickness and material.get('density'):
                # Для утеплителей и т.п.
                volume = area * thickness / 1000  # м³
                weight = volume * material['density']  # кг
                result['calculations']['volume'] = f"{volume:.2f} м³"
                result['calculations']['weight'] = f"{weight:.0f} кг"
        
        elif unit == "м³":
            if thickness:
                volume = area * thickness / 1000
                quantity = volume
            else:
                quantity = area  # предполагаем, что area уже в м³
        
        elif unit == "шт":
            # Для кирпича, блоков и т.п.
            if "кирпич" in material['name'].lower():
                # 102 шт/м² при толщине 510 мм
                quantity = area * 102
            elif "газоблок" in material['name'].lower():
                # 8.33 шт/м² для блоков 600×300×200
                quantity = area * 8.33
            else:
                quantity = area  # по умолчанию
        
        elif unit == "кг":
            if material.get('density') and thickness:
                volume = area * thickness / 1000
                quantity = volume * material['density']
            else:
                quantity = area  # по умолчанию
        
        else:
            quantity = area
        
        result['calculations']['quantity'] = f"{quantity:.2f} {unit}"
        
        # Расчет стоимости
        avg_price = (material['price_min'] + material['price_max']) / 2
        total_cost = quantity * avg_price
        result['calculations']['cost_min'] = f"{quantity * material['price_min']:,.0f} руб"
        result['calculations']['cost_avg'] = f"{total_cost:,.0f} руб"
        result['calculations']['cost_max'] = f"{quantity * material['price_max']:,.0f} руб"
        
        return result
    
    def get_popular_materials(self, limit: int = 10) -> List[Dict]:
        """Получить популярные материалы"""
        self.db.cursor.execute('''
        SELECT * FROM materials 
        ORDER BY popularity DESC, price_avg
        LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in self.db.cursor.fetchall()]
    
    def get_materials_by_application(self, application: str, limit: int = 10) -> List[Dict]:
        """Получить материалы по применению"""
        self.db.cursor.execute('''
        SELECT * FROM materials 
        WHERE applications LIKE ?
        ORDER BY popularity DESC
        LIMIT ?
        ''', (f"%{application}%", limit))
        
        return [dict(row) for row in self.db.cursor.fetchall()]