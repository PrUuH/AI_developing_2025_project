import random
from typing import List, Dict, Tuple

class AuctionSimulator:
    """
    Симулятор аукциона, возвращающий только данные:
    - финальную цену,
    - множитель,
    - уровень конкуренции.
    Не содержит print(), time.sleep() или Streamlit-кода.
    """

    def calculate_multiplier(self, nda_count: int) -> float:
        if nda_count <= 1:
            return 1.0
        elif nda_count <= 3:
            return round(random.uniform(1.10, 1.25), 2)
        else:
            return round(random.uniform(1.30, 1.40), 2)

    def simulate(self, base_price: float, interested_buyers: List[Dict]) -> dict:
        nda_count = sum(1 for b in interested_buyers if b.get("response") == "NDA_requested")
        multiplier = self.calculate_multiplier(nda_count)
        final_price = base_price * multiplier

        # Определяем уровень конкуренции для UI
        if nda_count >= 4:
            competition_level = "high"
            message = "Высокая конкуренция: 4+ покупателей"
        elif nda_count >= 2:
            competition_level = "medium"
            message = "Конкуренция: 2–3 покупателя"
        elif nda_count == 1:
            competition_level = "low"
            message = "Один заинтересованный покупатель"
        else:
            competition_level = "none"
            message = "Нет заинтересованных покупателей"

        return {
            "nda_count": nda_count,
            "final_price": final_price,
            "multiplier": multiplier,
            "competition_level": competition_level,
            "message": message
        }