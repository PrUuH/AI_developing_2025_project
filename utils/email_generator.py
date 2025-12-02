import random
from typing import Dict, List

class EmailGenerator:
    """
    Генератор персонализированных email-предложений для M&A-рассылки.
    """

    def __init__(self):
        # Шаблоны можно вынести в JSON или конфиг позже
        self._templates = {
            "strategic": [
                "Уважаемая компания «{name}», мы заметили, что вы активно расширяете своё присутствие в {geo_context}. "
                "У нас есть уникальная возможность приобрести успешный бизнес в сфере {industry_context}, который идеально дополнит вашу сеть.",

                "Здравствуйте, команда «{name}»! Учитывая вашу экспансию в регион {geo_context} и фокус на {industry_context}, "
                "мы хотели бы предложить вам рассмотреть приобретение высокомаржинального актива с доказанной прибыльностью.",

                "Уважаемые коллеги из «{name}», ваша стратегия развития в {industry_context} в регионе {geo_context} впечатляет. "
                "Мы представляем бизнес, который может стать естественным продолжением вашего портфеля."
            ],
            "financial": [
                "Уважаемый фонд «{name}», мы представляем стабильный бизнес в сфере {industry_context} с предсказуемыми денежными потоками, "
                "что идеально соответствует вашей инвестиционной стратегии в регионе {geo_context}.",

                "Здравствуйте, команда «{name}»! У нас есть привлекательный актив в {industry_context} ({geo_context}) с высокой рентабельностью и лояльной клиентской базой — "
                "отличная возможность для диверсификации вашего портфеля.",

                "Уважаемые инвесторы из «{name}», бизнес, которым мы представляем, демонстрирует устойчивый рост в секторе {industry_context} в {geo_context}. "
                "Высокая маржинальность и низкие операционные риски делают его идеальным кандидатом для инвестиций."
            ],
            "entrepreneur": [
                "Уважаемый(ая) {name}, вы ищете готовый бизнес для управления и роста? У нас есть превосходный актив в сфере {industry_context} в {geo_context} — "
                "с устоявшейся клиентской базой и возможностью масштабирования.",

                "Здравствуйте, {name}! Если вы рассматриваете вход в сектор {industry_context}, у нас есть уникальное предложение в {geo_context}: "
                "готовый к работе бизнес с сильной репутацией и стабильным доходом.",

                "Уважаемый(ая) {name}, ваш интерес к бизнесу в {geo_context} не остался незамеченным. "
                "Мы предлагаем вам рассмотреть приобретение успешной компании в сфере {industry_context} с потенциалом для личного управления и роста."
            ]
        }

    def generate(self, buyer_profile: Dict, seller_profile: Dict) -> str:
        """
        Генерирует персонализированное письмо.

        Параметры:
            buyer_profile (dict): профиль покупателя
            seller_profile (dict): профиль продавца

        Возвращает:
            str — текст email
        """
        buyer_type = buyer_profile.get("type", "other")
        name = buyer_profile["name"]

        # Определяем контекст персонализации
        industry_context = self._get_context(
            seller_profile["industry"],
            buyer_profile["industry_focus"]
        )
        geo_context = self._get_context(
            seller_profile["geography"],
            buyer_profile["target_geography"]
        )

        # Выбираем шаблон
        if buyer_type in self._templates:
            template = random.choice(self._templates[buyer_type])
            return template.format(
                name=name,
                industry_context=industry_context,
                geo_context=geo_context
            )
        else:
            return (
                f"Уважаемые представители «{name}», у нас есть привлекательный бизнес "
                f"в сфере {seller_profile['industry']} в {seller_profile['geography']}. "
                f"Свяжитесь с нами для получения дополнительной информации."
            )

    def _get_context(self, seller_value: str, buyer_list: List[str]) -> str:
        """Возвращает релевантное значение из предпочтений покупателя или случайный выбор."""
        if seller_value in buyer_list:
            return seller_value
        return random.choice(buyer_list) if buyer_list else seller_value


# === Пример использования ===
if __name__ == "__main__":
    generator = EmailGenerator()

    buyer = {
        "name": "MedInvest GmbH",
        "type": "financial",
        "industry_focus": ["Стоматологические клиники", "Частные медицинские центры"],
        "target_geography": ["Берлин", "Мюнхен"]
    }

    seller = {
        "industry": "Стоматологические клиники",
        "geography": "Берлин",
        "revenue": 8.2,
        "usp": "Единственная круглосуточная клиника в районе"
    }

    email = generator.generate(buyer, seller)
    print(email)