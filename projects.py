"""
МЕНЕДЖЕР ПРОЕКТОВ v12.0
"""

from typing import List, Dict, Optional
from datetime import datetime

class ProjectsManager:
    """Класс для работы с проектами"""
    
    def __init__(self, db):
        self.db = db
    
    def create_project_with_steps(self, user_id: int, name: str, project_type: str, 
                                 area: float, budget: float, description: str = "") -> Dict:
        """Создать проект с автоматическим расчетом этапов"""
        project_id = self.db.create_project(user_id, name, project_type, area, budget, description)
        
        # Создаем этапы проекта в зависимости от типа
        stages = self._get_project_stages(project_type)
        
        return {
            "project_id": project_id,
            "name": name,
            "type": project_type,
            "area": area,
            "budget": budget,
            "stages": stages,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    def _get_project_stages(self, project_type: str) -> List[Dict]:
        """Получить этапы проекта по типу"""
        stages_templates = {
            "дом": [
                {"name": "Проектирование", "duration": 30, "cost_percent": 5, "order": 1},
                {"name": "Фундамент", "duration": 45, "cost_percent": 20, "order": 2},
                {"name": "Стены и перекрытия", "duration": 60, "cost_percent": 25, "order": 3},
                {"name": "Кровля", "duration": 30, "cost_percent": 15, "order": 4},
                {"name": "Инженерные системы", "duration": 45, "cost_percent": 20, "order": 5},
                {"name": "Отделка", "duration": 60, "cost_percent": 15, "order": 6}
            ],
            "дача": [
                {"name": "Проектирование", "duration": 20, "cost_percent": 5, "order": 1},
                {"name": "Фундамент", "duration": 30, "cost_percent": 25, "order": 2},
                {"name": "Стены", "duration": 40, "cost_percent": 35, "order": 3},
                {"name": "Кровля", "duration": 20, "cost_percent": 15, "order": 4},
                {"name": "Инженерка", "duration": 25, "cost_percent": 15, "order": 5},
                {"name": "Отделка", "duration": 30, "cost_percent": 5, "order": 6}
            ],
            "баня": [
                {"name": "Фундамент", "duration": 20, "cost_percent": 20, "order": 1},
                {"name": "Стены", "duration": 25, "cost_percent": 30, "order": 2},
                {"name": "Кровля", "duration": 15, "cost_percent": 15, "order": 3},
                {"name": "Печь и дымоход", "duration": 10, "cost_percent": 20, "order": 4},
                {"name": "Отделка и полки", "duration": 20, "cost_percent": 15, "order": 5}
            ],
            "гараж": [
                {"name": "Фундамент", "duration": 15, "cost_percent": 30, "order": 1},
                {"name": "Стены", "duration": 20, "cost_percent": 40, "order": 2},
                {"name": "Кровля", "duration": 10, "cost_percent": 15, "order": 3},
                {"name": "Ворота и электрика", "duration": 10, "cost_percent": 15, "order": 4}
            ],
            "ремонт": [
                {"name": "Демонтаж", "duration": 10, "cost_percent": 5, "order": 1},
                {"name": "Черновая отделка", "duration": 20, "cost_percent": 30, "order": 2},
                {"name": "Инженерные системы", "duration": 15, "cost_percent": 25, "order": 3},
                {"name": "Чистовая отделка", "duration": 25, "cost_percent": 40, "order": 4}
            ]
        }
        
        return stages_templates.get(project_type.lower(), stages_templates["ремонт"])
    
    def calculate_project_cost(self, project_id: int) -> Dict:
        """Рассчитать детальную смету проекта"""
        project = self.db.cursor.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        
        if not project:
            return {"error": "Проект не найден"}
        
        project = dict(project)
        area = project['area']
        project_type = project['type']
        
        # Расчет стоимости по типу проекта
        cost_per_m2 = {
            "дом": 35000,      # руб/м²
            "дача": 25000,
            "баня": 40000,
            "гараж": 20000,
            "ремонт": 15000,
            "квартира": 20000
        }
        
        base_cost = area * cost_per_m2.get(project_type.lower(), 25000)
        
        # Детализация по категориям
        categories = {
            "Фундамент": 0.2,
            "Стены и перекрытия": 0.25,
            "Кровля": 0.15,
            "Инженерные системы": 0.2,
            "Отделка": 0.15,
            "Прочие расходы": 0.05
        }
        
        detailed_cost = {}
        for category, percent in categories.items():
            detailed_cost[category] = base_cost * percent
        
        return {
            "project": project,
            "base_cost_per_m2": cost_per_m2.get(project_type.lower(), 25000),
            "total_estimated": base_cost,
            "detailed": detailed_cost,
            "difference": project['budget'] - base_cost if project['budget'] else 0
        }
    
    def update_project_progress(self, project_id: int, stage: str, progress: int) -> bool:
        """Обновить прогресс проекта"""
        project = self.db.cursor.execute(
            "SELECT progress FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        
        if not project:
            return False
        
        current_progress = project['progress']
        new_progress = min(100, max(0, progress))
        
        return self.db.update_project(project_id, progress=new_progress)
    
    def get_project_timeline(self, project_id: int) -> Dict:
        """Получить временную шкалу проекта"""
        project = self.db.cursor.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        
        if not project:
            return {"error": "Проект не найден"}
        
        project = dict(project)
        stages = self._get_project_stages(project['type'])
        
        # Расчет дат
        start_date = datetime.strptime(project['created_at'][:10], "%Y-%m-%d")
        timeline = []
        
        current_date = start_date
        for stage in stages:
            end_date = current_date + timedelta(days=stage['duration'])
            timeline.append({
                "stage": stage['name'],
                "start": current_date.strftime("%d.%m.%Y"),
                "end": end_date.strftime("%d.%m.%Y"),
                "duration": stage['duration'],
                "cost_percent": stage['cost_percent']
            })
            current_date = end_date
        
        return {
            "project": project,
            "timeline": timeline,
            "total_duration": sum(s['duration'] for s in stages),
            "start_date": start_date.strftime("%d.%m.%Y"),
            "end_date": current_date.strftime("%d.%m.%Y")
        }
    
    def export_project(self, project_id: int, format: str = "txt") -> str:
        """Экспорт проекта в указанном формате"""
        project = self.db.cursor.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        
        if not project:
            return "Проект не найден"
        
        project = dict(project)
        cost_estimate = self.calculate_project_cost(project_id)
        timeline = self.get_project_timeline(project_id)
        
        if format == "txt":
            export_text = f"""
ПРОЕКТ: {project['name']}
Тип: {project['type']}
Площадь: {project['area']} м²
Бюджет: {project['budget']:,.0f} руб
Статус: {project['status']}
Прогресс: {project['progress']}%

РАСЧЕТНАЯ СТОИМОСТЬ:
Общая: {cost_estimate.get('total_estimated', 0):,.0f} руб
Цена за м²: {cost_estimate.get('base_cost_per_m2', 0):,.0f} руб/м²

ДЕТАЛИЗАЦИЯ:
"""
            if 'detailed' in cost_estimate:
                for category, amount in cost_estimate['detailed'].items():
                    export_text += f"{category}: {amount:,.0f} руб\n"
            
            if 'timeline' in timeline:
                export_text += "\nСРОКИ:\n"
                for stage in timeline['timeline']:
                    export_text += f"{stage['stage']}: {stage['start']} - {stage['end']} ({stage['duration']} дней)\n"
            
            export_text += f"\nСоздан: {project['created_at'][:10]}\n"
            export_text += f"Обновлен: {project['updated_at'][:10] if project['updated_at'] else project['created_at'][:10]}"
            
            return export_text
        
        else:
            return "Формат экспорта не поддерживается"