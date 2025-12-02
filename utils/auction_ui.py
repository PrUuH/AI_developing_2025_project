import streamlit as st
import time

def run_auction_ui(base_price: float, nda_count: int):
    placeholder = st.empty()
    delay = 1.0

    placeholder.info(f"Старт аукциона! Начальная цена: ${base_price:.1f} млн")
    time.sleep(delay)

    if nda_count == 0:
        placeholder.error("Нет заинтересованных покупателей.")
        return base_price

    placeholder.success(f"{nda_count} покупателей запросили NDA!")
    time.sleep(delay)

    placeholder.warning(f"Уже {nda_count} изучают досье — дедлайн через 10 дней!")
    time.sleep(delay)

    if nda_count >= 2:
        placeholder.warning("Появился второй покупатель — начинается конкуренция!")
        time.sleep(delay)
    if nda_count >= 4:
        placeholder.warning("Цена растёт — 3+ инвестора в сделке!")
        time.sleep(delay)

    if nda_count <= 1:
        multiplier = 1.0
    elif nda_count <= 3:
        multiplier = 1.2
    else:
        multiplier = 1.35

    final_price = base_price * multiplier
    placeholder.success(f"**Финальная цена**: ${final_price:.1f} млн (**+{(multiplier - 1) * 100:.0f}%**)")
    return final_price