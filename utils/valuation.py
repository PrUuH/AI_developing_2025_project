import sqlite3
import pandas as pd
from typing import Dict, Any, Union

class BusinessValuationEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _load_deals(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT target_industry, target_revenue, target_ebitda,
                   revenue_multiple, ebitda_multiple
            FROM deals
        """, conn)
        conn.close()
        return df

    def estimate(self, seller_profile: Dict[str, Any], top_n: int = 10) -> Dict[str, Union[str, float, None]]:
        try:
            df_deals = self._load_deals()
        except Exception as e:
            return {
                "error": f"Ошибка БД: {e}",
                "estimated_value": None,
                "method": None,
                "message": f"Ошибка подключения к базе: {e}"
            }

        industry = seller_profile["industry"]
        revenue = seller_profile["revenue"]
        ebitda = seller_profile.get("ebitda")

        comparable = df_deals[df_deals["target_industry"] == industry].copy()
        if comparable.empty:
            return {
                "error": "Нет сделок в отрасли",
                "estimated_value": None,
                "method": None,
                "message": "Не найдено сделок в вашей отрасли."
            }

        comparable["revenue_diff"] = (comparable["target_revenue"] - revenue).abs()
        comparable = comparable.nsmallest(top_n, "revenue_diff")
        if comparable.empty:
            return {
                "error": "Недостаточно данных",
                "estimated_value": None,
                "method": None,
                "message": "Недостаточно данных для оценки."
            }

        rev_mult = comparable["revenue_multiple"].median()
        ebitda_mult = comparable["ebitda_multiple"].median()

        if ebitda is not None and pd.notna(ebitda) and ebitda_mult > 0:
            value = ebitda * ebitda_mult
            method = f"мультипликатор EBITDA {ebitda_mult:.1f}x"
        elif rev_mult > 0:
            value = revenue * rev_mult
            method = f"мультипликатор выручки {rev_mult:.1f}x"
        else:
            return {
                "error": "Не удалось рассчитать",
                "estimated_value": None,
                "method": None,
                "message": "Не удалось рассчитать стоимость."
            }

        message = f"💰 Расчетная стоимость: ${value:.1f} млн ({method})"
        return {
            "error": None,
            "estimated_value": round(value, 2),
            "method": method,
            "message": message
        }