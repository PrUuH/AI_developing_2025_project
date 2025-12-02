import random
from typing import List, Dict


class BuyerResponseSimulator:
    """
    Класс для симуляции ответов потенциальных покупателей на сделку
    на основе их профиля, позиции в ранжировании и соответствия профилю продавца.
    """

    def __init__(self, base_nda_probs: Dict[int, float] = None):
        """
        Инициализация симулятора.

        :param base_nda_probs: Базовые вероятности NDA по рангам (по умолчанию — встроенные)
        """
        self.base_nda_probs = base_nda_probs or {
            'top': 0.70,   # rank <= 3
            'mid': 0.30,   # rank <= 8
            'low': 0.05    # rank > 8
        }

    def _calculate_personalization_score(self, buyer_profile: Dict, seller_profile: Dict) -> float:
        """
        Рассчитывает степень соответствия профиля покупателя профилю продавца.

        :param buyer_profile: Профиль покупателя
        :param seller_profile: Профиль продавца
        :return: Оценка соответствия (0.0 – 1.0)
        """
        score = 0.0
        if seller_profile["industry"] in buyer_profile["industry_focus"]:
            score += 1.0
        if seller_profile["geography"] in buyer_profile["target_geography"]:
            score += 1.0
        return min(1.0, score / 2.0)

    def _get_base_nda_probability(self, rank: int) -> float:
        """
        Определяет базовую вероятность запроса NDA по рангу.

        :param rank: Ранг покупателя
        :return: Базовая вероятность
        """
        if rank <= 3:
            return self.base_nda_probs['top']
        elif rank <= 8:
            return self.base_nda_probs['mid']
        else:
            return self.base_nda_probs['low']

    def simulate(self, ranked_buyers: List[Dict], buyer_profiles: Dict, seller_profile: Dict) -> List[Dict]:
        """
        Симулирует ответы покупателей на предложение о сделке.

        :param ranked_buyers: Список покупателей с полями "rank", "company_id"
        :param buyer_profiles: Словарь профилей покупателей по company_id
        :param seller_profile: Профиль продавца
        :return: Список словарей с исходными данными и добавленным "response"
        """
        results = []

        for buyer in ranked_buyers:
            rank = buyer["rank"]
            buyer_id = buyer["company_id"]
            buyer_profile = buyer_profiles.get(buyer_id)

            if not buyer_profile:
                # На случай отсутствия профиля
                response = "no_interest"
            else:
                # Базовая вероятность NDA по рангу
                p_nda = self._get_base_nda_probability(rank)

                # Увеличение вероятности на основе персонализации
                personalization = self._calculate_personalization_score(buyer_profile, seller_profile)
                p_nda = min(0.95, p_nda + 0.2 * personalization)

                # Определяем ответ случайным образом
                rand = random.random()
                if rand < p_nda:
                    response = "NDA_requested"
                elif rand < p_nda + 0.2:
                    response = "viewed_only"
                else:
                    response = "no_interest"

            results.append({**buyer, "response": response})

        return results


# === Тестовые данные ===
seller_profile = {
    "industry": "Стоматологические клиники",
    "geography": "Берлин",
    "revenue": 8.2,
    "usp": "Единственная круглосуточная клиника в районе"
}

ranked_buyers = [
    {"rank": 1, "name": "MedInvest GmbH", "type": "financial", "probability": 0.92, "company_id": "b_1"},
    {"rank": 2, "name": "Berlin Dental Group", "type": "strategic", "probability": 0.87, "company_id": "b_2"},
    {"rank": 3, "name": "HealthCap", "type": "financial", "probability": 0.81, "company_id": "b_3"},
    {"rank": 4, "name": "Family Office Schmidt", "type": "entrepreneur", "probability": 0.65, "company_id": "b_4"},
    {"rank": 5, "name": "MedGrowth Fund", "type": "financial", "probability": 0.60, "company_id": "b_5"},
    {"rank": 6, "name": "Nordic Health Partners", "type": "strategic", "probability": 0.55, "company_id": "b_6"},
    {"rank": 7, "name": "Alpha Capital", "type": "financial", "probability": 0.48, "company_id": "b_7"},
    {"rank": 8, "name": "Dr. Müller", "type": "entrepreneur", "probability": 0.42, "company_id": "b_8"},
    {"rank": 9, "name": "Global Med Invest", "type": "financial", "probability": 0.35, "company_id": "b_9"},
    {"rank": 10, "name": "Svensk Healthcare", "type": "strategic", "probability": 0.28, "company_id": "b_10"},
]

buyer_profiles = {
    "b_1": {"name": "MedInvest GmbH", "type": "financial", "industry_focus": ["Стоматологические клиники", "Аптеки"], "target_geography": ["Берлин", "Мюнхен"]},
    "b_2": {"name": "Berlin Dental Group", "type": "strategic", "industry_focus": ["Стоматологические клиники"], "target_geography": ["Берлин"]},
    "b_3": {"name": "HealthCap", "type": "financial", "industry_focus": ["Частные медицинские центры", "Стоматологические клиники"], "target_geography": ["Берлин", "Гамбург"]},
    "b_4": {"name": "Family Office Schmidt", "type": "entrepreneur", "industry_focus": ["Фитнес-клубы", "Розничная торговля"], "target_geography": ["Франкфурт", "Кёльн"]},
    "b_5": {"name": "MedGrowth Fund", "type": "financial", "industry_focus": ["Стоматологические клиники"], "target_geography": ["Мюнхен", "Штутгарт"]},
    "b_6": {"name": "Nordic Health Partners", "type": "strategic", "industry_focus": ["Стоматологические клиники", "Оптика"], "target_geography": ["Стокгольм", "Мальмё"]},
    "b_7": {"name": "Alpha Capital", "type": "financial", "industry_focus": ["IT-аутсорсинг", "Автосервисы"], "target_geography": ["Москва", "Санкт-Петербург"]},
    "b_8": {"name": "Dr. Müller", "type": "entrepreneur", "industry_focus": ["Стоматологические клиники"], "target_geography": ["Берлин"]},
    "b_9": {"name": "Global Med Invest", "type": "financial", "industry_focus": ["Аптеки"], "target_geography": ["Москва", "Екатеринбург"]},
    "b_10": {"name": "Svensk Healthcare", "type": "strategic", "industry_focus": ["Частные медицинские центры"], "target_geography": ["Стокгольм", "Гётеборг"]},
}

# === Запуск ===
if __name__ == "__main__":
    simulator = BuyerResponseSimulator()
    responses = simulator.simulate(ranked_buyers, buyer_profiles, seller_profile)
    for b in responses:
        print(f"{b['rank']}. {b['name']} → {b['response']}")
