import streamlit as st
import pandas as pd
from utils.valuation import BusinessValuationEngine
from utils.ranking import BuyerRanker
from utils.teaser_generator_hf import TeaserGenerator
from utils.email_generator import EmailGenerator
from utils.buyer_response_simulator import BuyerResponseSimulator
from utils.auction_simulator import AuctionSimulator
from utils.company_graph import CompanyConnectionGraph
from utils.data_loader import BuyerDataLoader
from utils.document_access import DocumentAccessManager

DB_PATH = "m_and_a.db"

st.set_page_config(page_title="AI M&A Platform", layout="wide")
st.title("AI-Платформа для Продажи Бизнеса")

# === Ввод данных ===
INDUSTRIES = ["Стоматологические клиники", "Аптеки", "Фитнес-клубы", "IT-аутсорсинг"]
GEOGRAPHIES = ["Берлин", "Мюнхен", "Москва", "Санкт-Петербург"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    industry = st.selectbox("Отрасль", INDUSTRIES)
with col2:
    geography = st.selectbox("География", GEOGRAPHIES)
with col3:
    revenue = st.number_input("Выручка (млн $)", min_value=5.0, max_value=100.0, value=10.0, step=0.5)
with col4:
    ebitda = st.number_input("EBITDA (млн $, опционально)", min_value=0.0, value=0.0, step=0.1)

seller = {
    "industry": industry,
    "geography": geography,
    "revenue": revenue,
    "ebitda": ebitda if ebitda > 0 else None,
    "assets": "Современное оборудование и лояльная клиентская база",
    "num_customers": 5000,
    "usp": "Высокая маржинальность и стабильный кэш-флоу"
}

if st.button("Запустить анализ продажи", type="primary"):
    with st.spinner("Анализируем рынок..."):
        try:
            # --- 1. Оценка стоимости ---
            valuation_engine = BusinessValuationEngine(DB_PATH)
            valuation_result = valuation_engine.estimate(seller)
            if valuation_result["error"]:
                st.error(valuation_result["message"])
                st.stop()
            st.success(valuation_result["message"])
            st.divider()

            # --- 2. Ранжирование покупателей ---
            ranker = BuyerRanker(DB_PATH)
            ranker.fit()
            ranked_buyers = ranker.rank(seller, top_k=10)
            for i, b in enumerate(ranked_buyers, 1):
                b["rank"] = i

            df_buyers = pd.DataFrame(ranked_buyers)
            st.header("2. Топ-10 потенциальных покупателей")
            st.dataframe(
                df_buyers[["rank", "name", "type", "probability"]].rename(columns={
                    "rank": "Ранг",
                    "name": "Название покупателя",
                    "type": "Тип",
                    "probability": "Вероятность интереса"
                }).style.format({"Вероятность интереса": "{:.1%}"}),
                hide_index=True,
                use_container_width=True
            )
            st.divider()

            # --- 3. Teaser и email ---
            st.header("3. Teaser и коммуникация")
            teaser_gen = TeaserGenerator()
            email_gen = EmailGenerator()
            st.subheader("Teaser (публичный)")
            st.info(teaser_gen.generate(seller))

            # Загрузка профилей покупателей
            loader = BuyerDataLoader(DB_PATH)
            buyers_df = loader.load_buyers()
            buyer_profiles = {row["company_id"]: row.to_dict() for _, row in buyers_df.iterrows()}

            # Письмо для топ-1
            top_buyer = buyer_profiles[ranked_buyers[0]["company_id"]]
            st.subheader("Пример персонализированного письма")
            st.code(email_gen.generate(top_buyer, seller), language="text")
            st.divider()

            # --- 4. Симуляция откликов и аукцион ---
            simulator = BuyerResponseSimulator()
            responses = simulator.simulate(ranked_buyers, buyer_profiles, seller)
            nda_count = sum(1 for r in responses if r["response"] == "NDA_requested")

            # Аукцион
            auction = AuctionSimulator()
            auction_result = auction.simulate(valuation_result["estimated_value"], responses)

            # Отображение конкурентной среды
            st.header("4. Аукцион и конкуренция")
            if auction_result["competition_level"] == "high":
                st.success(f"{auction_result['message']} — цена повышена на 30–40%")
            elif auction_result["competition_level"] == "medium":
                st.warning(f"{auction_result['message']} — цена повышена на 10–25%")
            elif auction_result["competition_level"] == "low":
                st.info(f"{auction_result['message']} — базовая цена")
            else:
                st.error("Нет заинтересованных покупателей — сделка не состоится")

            # Метрики
            st.metric("Начальная цена", f"${valuation_result['estimated_value']:.1f} млн")
            st.metric("Финальная цена", f"${auction_result['final_price']:.1f} млн", 
                     delta=f"+{(auction_result['multiplier'] - 1) * 100:.0f}%")
            st.divider()

            # --- 5. Досье (только после NDA) ---
            doc_manager = DocumentAccessManager(seller)
            if nda_count >= 1:
                st.subheader("Полное досье (доступно после NDA)")
                dossier = doc_manager.get_full_dossier(nda_signed=True)
                st.json(dossier)
            else:
                st.info("Полное досье станет доступно, как только хотя бы один покупатель запросит NDA.")
            st.divider()

            # --- 6. Граф связей ---
            st.header("5. Скрытые связи (граф)")
            graph_builder = CompanyConnectionGraph(DB_PATH)
            graph_builder.build(seller)
            fig = graph_builder.get_plot_figure(top_n=8)
            if fig:
                st.pyplot(fig)
            else:
                st.write("Нет значимых связей для отображения.")

        except Exception as e:
            st.error(f"Ошибка: {e}")
else:

    st.info("Заполните данные о вашем бизнесе и нажмите «Запустить анализ продажи».")
