import pandas as pd
import random
import uuid
from faker import Faker
from typing import List, Dict, Any


class MADatasetGenerator:
    """
    Класс для генерации синтетических данных о продавцах, покупателях и сделках (M&A).
    Поддерживает мультиязычность (немецкие и русские города/названия).
    """

    def __init__(self):
        # Фейкер для генерации имён и описаний
        self.fake_ru = Faker('ru_RU')
        self.fake_de = Faker('de_DE')

        # Настройки можно переопределить через параметры
        self.INDUSTRIES = [
            "Стоматологические клиники",
            "Частные медицинские центры",
            "Аптеки",
            "Оптика",
            "Фитнес-клубы",
            "Розничная торговля продуктами",
            "Автосервисы",
            "IT-аутсорсинг"
        ]

        self.GEOGRAPHIES = [
            "Берлин", "Мюнхен", "Гамбург", "Франкфурт", "Кёльн",
            "Москва", "Санкт-Петербург", "Екатеринбург", "Новосибирск"
        ]

        self.GERMAN_CITIES = {"Берлин", "Мюнхен", "Гамбург", "Франкфурт", "Кёльн"}
        self.RUSSIAN_CITIES = {"Москва", "Санкт-Петербург", "Екатеринбург", "Новосибирск"}

        self.BUYER_TYPES = ['strategic', 'financial', 'entrepreneur']

        self.USP_EXAMPLES = [
            "Единственная круглосуточная клиника в районе",
            "Премиум-обслуживание с гарантированным приёмом в течение 24 часов",
            "Клуб с самым высоким retention rate в регионе (78%)",
            "Уникальная локация у транспортного узла с пешим трафиком 20k/день",
            "Сервис с рейтингом 4.9 на Google и 95% повторных клиентов",
            "Единственные аптеки с доставкой в течение 30 минут в районе",
            "Партнёрство с ведущими офтальмологическими клиниками города",
            "Специализация на защите данных для медицинских учреждений",
        ]

        # Сгенерированные DataFrame
        self.df_sellers = pd.DataFrame()
        self.df_buyers = pd.DataFrame()
        self.df_deals = pd.DataFrame()

    def set_config(self, num_sellers: int = 8, num_buyers: int = 150, num_deals: int = 70):
        """
        Настраивает параметры генерации.
        """
        self.NUM_SELLERS = num_sellers
        self.NUM_BUYERS = num_buyers
        self.NUM_DEALS = num_deals
        return self

    def _safe_sql_escape(self, val: Any) -> str:
        """
        Безопасно экранирует значение для вставки в SQL (поддерживает строки, списки, числа).
        """
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return 'NULL'
        if isinstance(val, str):
            clean_val = str(val).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            escaped = clean_val.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(val, (list, dict)):
            str_val = str(val).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            escaped = str_val.replace("'", "''")
            return f"'{escaped}'"
        else:
            return str(val)

    def generate_sellers(self) -> 'MADatasetGenerator':
        """Генерирует данные о продавцах."""
        sellers = []
        for i in range(self.NUM_SELLERS):
            geography = random.choice(self.GEOGRAPHIES)
            rev = round(random.uniform(5, 100), 1)
            ebitda = round(rev * random.uniform(0.1, 0.3), 1)
            assets_desc = self.fake_de.sentence(nb_words=6) if geography in self.GERMAN_CITIES \
                else self.fake_ru.sentence(nb_words=6)

            sellers.append({
                "seller_id": f"s_{i + 1}",
                "industry": random.choice(self.INDUSTRIES),
                "geography": geography,
                "revenue": rev,
                "ebitda": ebitda,
                "assets": assets_desc,
                "num_customers": random.randint(500, 100000),
                "usp": random.choice(self.USP_EXAMPLES)
            })

        self.df_sellers = pd.DataFrame(sellers)
        return self

    def generate_buyers(self) -> 'MADatasetGenerator':
        """Генерирует данные о покупателях."""
        buyers = []
        for i in range(self.NUM_BUYERS):
            buyer_type = random.choice(self.BUYER_TYPES)
            geo_focus = random.sample(self.GEOGRAPHIES, k=random.randint(1, 3))
            ind_focus = random.sample(self.INDUSTRIES, k=random.randint(1, 3))
            rev_min = round(random.uniform(3, 50), 1)
            rev_max = round(rev_min + random.uniform(10, 80), 1)
            past_acq = [
                {"industry": random.choice(self.INDUSTRIES), "geography": random.choice(self.GEOGRAPHIES)}
                for _ in range(random.randint(0, 3))
            ]
            # Выбор языка на основе географии
            use_de = random.choice([True, False])
            if buyer_type != 'entrepreneur':
                name = self.fake_de.company() if use_de else self.fake_ru.company()
            else:
                name = self.fake_de.name() if use_de else self.fake_ru.name()

            buyers.append({
                "company_id": f"b_{i + 1}",
                "name": name,
                "type": buyer_type,
                "industry_focus": ind_focus,
                "target_geography": geo_focus,
                "preferred_revenue_min": rev_min,
                "preferred_revenue_max": rev_max,
                "past_acquisitions": past_acq,
                "financial_capacity": round(random.uniform(10, 200), 1)
            })

        self.df_buyers = pd.DataFrame(buyers)
        return self

    def generate_deals(self) -> 'MADatasetGenerator':
        """Генерирует данные о сделках."""
        deals = []
        for i in range(self.NUM_DEALS):
            buyer = self.df_buyers.sample(1).iloc[0]  # случайный покупатель
            industry = random.choice(self.INDUSTRIES)
            geography = random.choice(self.GEOGRAPHIES)
            target_revenue = round(random.uniform(5, 90), 1)
            ebitda_margin = random.uniform(0.12, 0.28)
            target_ebitda = round(target_revenue * ebitda_margin, 1)
            ebitda_multiple = round(random.uniform(4, 9), 1)
            deal_size = round(target_ebitda * ebitda_multiple, 1)
            revenue_multiple = round(deal_size / target_revenue, 1) if target_revenue > 0 else 0.0

            deals.append({
                "deal_id": f"d_{i + 1}",
                "buyer_id": buyer["company_id"],
                "target_industry": industry,
                "target_geography": geography,
                "target_revenue": target_revenue,
                "target_ebitda": target_ebitda,
                "deal_size": deal_size,
                "revenue_multiple": revenue_multiple,
                "ebitda_multiple": ebitda_multiple
            })

        self.df_deals = pd.DataFrame(deals)
        return self

    def generate_all(self) -> 'MADatasetGenerator':
        """
        Генерирует все таблицы: sellers, buyers, deals.
        """
        self.generate_sellers()
        self.generate_buyers()
        self.generate_deals()
        return self

    def export_to_sql(self, filename: str = "m_and_a_sqlite_compatible.sql"):
        """
        Экспортирует сгенерированные данные в SQL-файл, совместимый с SQLite.

        :param filename: Имя выходного SQL-файла
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write("-- M&A Dataset for SQLite (DB Browser compatible)\n")
            f.write("-- Generated by MADatasetGenerator (OOP)\n\n")

            # === Схема таблиц ===
            f.write("CREATE TABLE IF NOT EXISTS sellers (\n")
            f.write("    seller_id TEXT PRIMARY KEY,\n")
            f.write("    industry TEXT NOT NULL,\n")
            f.write("    geography TEXT NOT NULL,\n")
            f.write("    revenue REAL NOT NULL,\n")
            f.write("    ebitda REAL NOT NULL,\n")
            f.write("    assets TEXT,\n")
            f.write("    num_customers INTEGER,\n")
            f.write("    usp TEXT\n);\n\n")

            f.write("CREATE TABLE IF NOT EXISTS buyers (\n")
            f.write("    company_id TEXT PRIMARY KEY,\n")
            f.write("    name TEXT NOT NULL,\n")
            f.write("    type TEXT CHECK(type IN ('strategic', 'financial', 'entrepreneur')),\n")
            f.write("    industry_focus TEXT,\n")
            f.write("    target_geography TEXT,\n")
            f.write("    preferred_revenue_min REAL,\n")
            f.write("    preferred_revenue_max REAL,\n")
            f.write("    past_acquisitions TEXT,\n")
            f.write("    financial_capacity REAL\n);\n\n")

            f.write("CREATE TABLE IF NOT EXISTS deals (\n")
            f.write("    deal_id TEXT PRIMARY KEY,\n")
            f.write("    buyer_id TEXT NOT NULL,\n")
            f.write("    target_industry TEXT NOT NULL,\n")
            f.write("    target_geography TEXT NOT NULL,\n")
            f.write("    target_revenue REAL NOT NULL,\n")
            f.write("    target_ebitda REAL NOT NULL,\n")
            f.write("    deal_size REAL NOT NULL,\n")
            f.write("    revenue_multiple REAL,\n")
            f.write("    ebitda_multiple REAL\n);\n\n")

            # === Вставка данных ===
            self._write_inserts(f, "sellers", self.df_sellers)
            self._write_inserts(f, "buyers", self.df_buyers)
            self._write_inserts(f, "deals", self.df_deals)

        print(f"Файл '{filename}' успешно создан — готов к импорту в DB Browser for SQLite.")

    def _write_inserts(self, f, table_name: str, df: pd.DataFrame):
        """Вспомогательный метод для записи INSERT-запросов."""
        if df.empty:
            return

        columns = ", ".join(df.columns)
        f.write(f"INSERT INTO {table_name} ({columns}) VALUES\n")
        rows = []
        for _, row in df.iterrows():
            values = ", ".join(self._safe_sql_escape(row[col]) for col in df.columns)
            rows.append(f"({values})")
        f.write(",\n".join(rows) + ";\n\n")


# === Пример использования ===
if __name__ == "__main__":
    generator = MADatasetGenerator()
    generator.set_config(num_sellers=8, num_buyers=150, num_deals=70)
    generator.generate_all()
    generator.export_to_sql("m_and_a_sqlite_compatible.sql")

    # Дополнительно: можно использовать DataFrame в памяти
    # print("\nПример данных о продавцах:")
    # print(generator.df_sellers.head())
