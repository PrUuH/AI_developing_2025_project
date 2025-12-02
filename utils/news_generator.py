import random

def generate_synthetic_news(industry: str, geography: str, buyer_name: str) -> str:
    templates = [
        f"Компания «{buyer_name}» приобрела успешную {industry.lower()} в {geography}.",
        f"Инвесторы из «{buyer_name}» расширяют присутствие в секторе {industry.lower()} через покупку актива в {geography}.",
        f"«{buyer_name}» завершила сделку по покупке бизнеса в сфере {industry.lower()} в регионе {geography}."
    ]
    return random.choice(templates)

def generate_all_news(db_path: str):
    """Генерирует 50 синтетических новостей и сохраняет в базу (таблица `news`)."""
    import sqlite3
    from .data_loader import BuyerDataLoader
    loader = BuyerDataLoader(db_path)
    buyers = loader.load_buyers()
    
    news_items = []
    for _ in range(50):
        buyer = buyers.sample(1).iloc[0]
        industry = random.choice([
            "Стоматологические клиники", "Аптеки", "Частные медицинские центры"
        ])
        geography = random.choice([
            "Берлин", "Мюнхен", "Москва", "Санкт-Петербург"
        ])
        text = generate_synthetic_news(industry, geography, buyer["name"])
        news_items.append((text, industry, geography, buyer["company_id"]))
    
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS news")
    conn.execute("""
        CREATE TABLE news (
            id INTEGER PRIMARY KEY,
            text TEXT,
            extracted_industry TEXT,
            extracted_geography TEXT,
            buyer_id TEXT
        )
    """)
    conn.executemany("INSERT INTO news VALUES (?,?,?,?,?)", [(i, *item) for i, item in enumerate(news_items)])
    conn.commit()
    conn.close()
    print("Сгенерировано 50 синтетических новостей.")