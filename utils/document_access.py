import json
from typing import Dict, Any, Optional
import pandas as pd

class DocumentAccessManager:
    """
    Управляет доступом к документам: teaser (публичный) и полное досье (только после NDA).
    """
    def __init__(self, seller_profile: Dict[str, Any]):
        self.seller_profile = seller_profile

    def get_teaser(self) -> str:
        return (
            f"Бизнес в сфере {self.seller_profile['industry']} в {self.seller_profile['geography']}. "
            f"{self.seller_profile.get('usp', 'Стабильный и прибыльный актив с потенциалом роста.')}"
        )

    def _safe_value(self, val, default="—"):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return val

    def get_full_dossier(self, nda_signed: bool = False) -> Dict[str, Any]:
        if not nda_signed:
            return {
                "error": "Доступ к полному досье возможен только после запроса NDA.",
                "teaser_only": self.get_teaser()
            }
        
        return {
            "business_summary": {
                "industry": self.seller_profile["industry"],
                "geography": self.seller_profile["geography"],
                "unique_selling_proposition": self._safe_value(self.seller_profile.get("usp"))
            },
            "financial_metrics": {
                "revenue_million_usd": self._safe_value(self.seller_profile.get("revenue")),
                "ebitda_million_usd": self._safe_value(self.seller_profile.get("ebitda")),
                "ebitda_margin_percent": self._safe_value(self._calculate_ebitda_margin())
            },
            "operational_details": {
                "key_assets": self._safe_value(self.seller_profile.get("assets")),
                "customer_base": self._safe_value(self.seller_profile.get("num_customers")),
                "confidentiality_level": "Internal – NDA Required"
            }
        }

    def _calculate_ebitda_margin(self) -> Optional[float]:
        revenue = self.seller_profile.get("revenue")
        ebitda = self.seller_profile.get("ebitda")
        if revenue and ebitda and revenue > 0:
            return round((ebitda / revenue) * 100, 1)
        return None

    def get_dossier_as_json(self, nda_signed: bool = False) -> str:
        dossier = self.get_full_dossier(nda_signed)
        return json.dumps(dossier, ensure_ascii=False, indent=2)