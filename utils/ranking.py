import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import ast
from typing import List, Dict, Any
from .data_loader import BuyerDataLoader

class BuyerRanker:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model = None
        self._buyers_df = None

    def _safe_literal_eval(self, x):
        if pd.isna(x) or x == "":
            return []
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return []

    def _load_buyers(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM buyers", conn)
        conn.close()
        df["industry_focus"] = df["industry_focus"].apply(self._safe_literal_eval)
        df["target_geography"] = df["target_geography"].apply(self._safe_literal_eval)
        df["past_acquisitions"] = df["past_acquisitions"].apply(self._safe_literal_eval)
        self._buyers_df = df

    def _simulate_interest_label(self, seller: Dict[str, Any], buyer: Dict[str, Any]) -> int:
        score = 0.0
        if seller["industry"] in buyer["industry_focus"]:
            score += 0.3
        if seller["geography"] in buyer["target_geography"]:
            score += 0.3
        if buyer["preferred_revenue_min"] <= seller["revenue"] <= buyer["preferred_revenue_max"]:
            score += 0.3
        past_match = any(
            acq.get("industry") == seller["industry"] or acq.get("geography") == seller["geography"]
            for acq in buyer["past_acquisitions"]
        )
        if past_match:
            score += 0.1
        return 1 if score >= 0.7 else 0

    def _extract_features(self, seller: Dict[str, Any], buyer: Dict[str, Any]) -> List[float]:
        ind_match = 1 if seller["industry"] in buyer["industry_focus"] else 0
        geo_match = 1 if seller["geography"] in buyer["target_geography"] else 0
        rev_in_range = 1 if (buyer["preferred_revenue_min"] <= seller["revenue"] <= buyer["preferred_revenue_max"]) else 0
        past_match = any(
            acq.get("industry") == seller["industry"] or acq.get("geography") == seller["geography"]
            for acq in buyer["past_acquisitions"]
        )
        rev_center = (buyer["preferred_revenue_min"] + buyer["preferred_revenue_max"]) / 2
        rev_range = max(1.0, buyer["preferred_revenue_max"] - buyer["preferred_revenue_min"])
        rev_diff_norm = abs(seller["revenue"] - rev_center) / rev_range
        return [ind_match, geo_match, rev_in_range, int(past_match), rev_diff_norm]

    def fit(self):
        if self._buyers_df is None:
            self._load_buyers()
        X, y = [], []
        industries = ["Стоматологические клиники", "Аптеки", "Фитнес-клубы"]
        geographies = ["Берлин", "Москва"]
        for _ in range(300):
            fake_seller = {
                "industry": np.random.choice(industries),
                "geography": np.random.choice(geographies),
                "revenue": round(np.random.uniform(5, 100), 1)
            }
            sampled = self._buyers_df.sample(n=min(20, len(self._buyers_df)))
            for _, buyer_row in sampled.iterrows():
                buyer_dict = buyer_row.to_dict()
                label = self._simulate_interest_label(fake_seller, buyer_dict)
                features = self._extract_features(fake_seller, buyer_dict)
                X.append(features)
                y.append(label)
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)

    def rank(self, seller_profile: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        if self.model is None:
            raise RuntimeError("Модель не обучена")
        results = []
        for _, buyer_row in self._buyers_df.iterrows():
            buyer = buyer_row.to_dict()
            features = self._extract_features(seller_profile, buyer)
            prob = self.model.predict_proba([features])[0][1]
            results.append({
                "name": buyer["name"],
                "type": buyer["type"],
                "company_id": buyer["company_id"],
                "probability": float(prob)
            })
        results.sort(key=lambda x: x["probability"], reverse=True)
        return results[:top_k]