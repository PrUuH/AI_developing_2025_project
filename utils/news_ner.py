import re

# Списки для простого NER
INDUSTRIES = ["стоматолог", "аптек", "медицин", "клиник", "здоровь", "фармацевт"]
GEOGRAPHIES = ["Берлин", "Мюнхен", "Москва", "Санкт-Петербург", "Гамбург", "Новосибирск"]

def extract_entities(text: str):
    """Извлекает отрасль и географию из текста без ML (правила)."""
    industry = None
    geography = None
    
    text_lower = text.lower()
    for word in INDUSTRIES:
        if word in text_lower:
            industry = "Стоматологические клиники" 
            break
    
    for city in GEOGRAPHIES:
        if city in text:
            geography = city
            break
    
    return {"industry": industry, "geography": geography}