import os
import random
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Dict, List

class TeaserGenerator:
    """
    Генератор анонимных teaser-описаний для продажи бизнеса.
    Использует языковую модель (ruGPT) с fallback на шаблоны.
    """

    def __init__(self, templates_path: Optional[str] = None, device: str = "auto"):
        """
        Инициализация генератора.
        
        :param templates_path: путь к JSON с шаблонами (по умолчанию — рядом с файлом)
        :param device: "cuda", "cpu" или "auto"
        """
        self.templates_path = templates_path or os.path.join(os.path.dirname(__file__), "teaser_templates.json")
        self.templates = self._load_templates()
        self.model = None
        self.tokenizer = None
        self.device = (
            "cuda" if device == "auto" and torch.cuda.is_available() else
            "cpu" if device == "auto" else device
        )

    def _load_templates(self) -> Dict[str, List[str]]:
        """Загружает шаблоны из JSON-файла."""
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить шаблоны из {self.templates_path}: {e}")
            return {}

    def _load_model(self):
        """Ленивая загрузка модели и токенизатора."""
        if self.model is None:
            print("Загрузка ruGPT-3-small...")
            model_name = "ai-forever/rugpt3small_based_on_gpt2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model.eval()
            self.model.to(self.device)
            print(f"Модель загружена на {self.device.upper()}")

    def _generate_with_model(self, seller_profile: Dict[str, any], max_new_tokens: int = 80) -> Optional[str]:
        """Генерирует teaser с помощью Hugging Face модели."""
        try:
            self._load_model()

            # Few-shot примеры из шаблонов
            examples = self.templates.get(seller_profile["industry"], [])
            if examples:
                selected = random.sample(examples, k=min(2, len(examples)))
                examples_text = "\n".join(f"- {ex}" for ex in selected)
            else:
                examples_text = (
                    "- Растущая стоматологическая клиника в Берлине с выручкой €8 млн. Высокая лояльность клиентов.\n"
                    "- Популярный фитнес-клуб в Москве с выручкой €12 млн. Уникальная подписная модель."
                )

            prompt = (
                "Ты — профессиональный M&A-консультант. Напиши краткий, анонимный и привлекательный teaser для продажи бизнеса. "
                "Не указывай название компании, адрес или контакты. Используй деловой, но убедительный тон. "
                "Teaser должен быть на русском языке, 1–2 предложения, заканчиваться точкой.\n\n"
                "Примеры успешных teaser'ов:\n"
                f"{examples_text}\n\n"
                "Теперь создай teaser для следующего бизнеса:\n"
                f"- Отрасль: {seller_profile['industry']}\n"
                f"- Город: {seller_profile['geography']}\n"
                f"- Выручка: {seller_profile['revenue']} млн долларов\n"
                f"- УТП: {seller_profile.get('usp', 'Стабильный кэш-флоу и лояльная клиентская база')}\n\n"
                "Teaser:"
            )

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.95,
                    top_p=0.9,
                    repetition_penalty=1.15,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            teaser = generated.split("Teaser:", 1)[-1].strip()
            teaser = teaser.split('\n')[0].split('###')[0].split('Примеры')[0].strip()

            if teaser and not teaser.endswith('.'):
                teaser += '.'

            # Валидация
            keywords = ["выручк", "потенциал", "лояльн", "стабильн", "бизнес", "клиент"]
            if len(teaser) >= 30 and any(kw in teaser for kw in keywords):
                return teaser
            return None

        except Exception as e:
            print(f"Ошибка генерации модели: {e}")
            return None

    def _generate_fallback(self, seller_profile: Dict[str, any]) -> str:
        """Генерирует teaser из шаблонов (fallback)."""
        industry = seller_profile["industry"]
        geography = seller_profile["geography"]
        revenue = seller_profile["revenue"]
        usp = seller_profile.get("usp", "Высокая операционная эффективность и стабильный кэш-флоу.")

        templates = self.templates.get(industry, [
            "Бизнес в сфере {industry} в {geography} с выручкой €{revenue} млн. {usp}. Сильная рыночная позиция и потенциал роста."
        ])
        template = random.choice(templates)

        return template.format(
            industry=industry.lower(),
            geography=geography,
            revenue=f"{revenue:.1f}".rstrip('0').rstrip('.'),
            usp=usp.rstrip('. ') + '.'
        )

    def generate(self, seller_profile: Dict[str, any]) -> str:
        """
        Генерирует teaser: сначала пытается через модель, при неудаче — через шаблоны.
        
        :param seller_profile: словарь с ключами: industry, geography, revenue, usp
        :return: строка с teaser'ом
        """
        teaser = self._generate_with_model(seller_profile)
        if teaser:
            return teaser
        return self._generate_fallback(seller_profile)


# === Пример использования ===
if __name__ == "__main__":
    seller = {
        "industry": "Фитнес-клубы",
        "geography": "Москва",
        "revenue": 1,
        "usp": "Клуб с самым высоким retention rate в регионе (78%)"
    }

    generator = TeaserGenerator()
    teaser = generator.generate(seller)
    print(teaser)