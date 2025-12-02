import sqlite3
import pandas as pd
import ast
from typing import List

class BuyerDataLoader:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @staticmethod
    def _safe_literal_eval(x) -> List:
        if pd.isna(x) or x in ("", "[]", "NULL", None):
            return []
        try:
            result = ast.literal_eval(x)
            return result if isinstance(result, list) else []
        except (ValueError, SyntaxError, TypeError):
            return []

    def load_buyers(self) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM buyers", conn)
        list_columns = ["industry_focus", "target_geography", "past_acquisitions"]
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._safe_literal_eval)
            else:
                df[col] = [[] for _ in range(len(df))]
        return df