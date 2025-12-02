import sqlite3
import pandas as pd
import networkx as nx
import ast
import matplotlib.pyplot as plt
from typing import Dict, List

class CompanyConnectionGraph:
    NEARBY_ZONES = {
        "Берлин": ["Потсдам", "Лейпциг", "Гамбург"],
        "Мюнхен": ["Нюрнберг", "Аугсбург"],
        "Москва": ["Санкт-Петербург", "Подольск"],
        "Санкт-Петербург": ["Москва", "Новгород"],
        "Стокгольм": ["Мальмё"]
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.Graph()
        self.seller_id = "SELLER"

    def _cities_are_close(self, c1: str, c2: str) -> bool:
        return c1 == c2 or c2 in self.NEARBY_ZONES.get(c1, [])

    def _load_and_parse(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM buyers", conn)
        conn.close()
        for col in ["industry_focus", "target_geography", "past_acquisitions"]:
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        return df

    def build(self, seller: Dict) -> 'CompanyConnectionGraph':
        self.graph.clear()
        df = self._load_and_parse()

        # Узел продавца (без поля "type")
        seller_attrs = {k: v for k, v in seller.items() if k != "type"}
        self.graph.add_node(self.seller_id, **seller_attrs)

        for _, buyer in df.iterrows():
            buyer_dict = buyer.to_dict()
            # Убираем "type", чтобы избежать конфликта с NetworkX
            buyer_attrs = {k: v for k, v in buyer_dict.items() if k != "type"}
            buyer_id = buyer["company_id"]
            self.graph.add_node(buyer_id, **buyer_attrs)

            strength = 0.0
            if seller["industry"] in buyer["industry_focus"]:
                strength += 2.0
            if seller["geography"] in buyer["target_geography"]:
                strength += 2.0
            else:
                for geo in buyer["target_geography"]:
                    if self._cities_are_close(seller["geography"], geo):
                        strength += 1.5
                        break
            for acq in buyer["past_acquisitions"]:
                if isinstance(acq, dict):
                    if acq.get("industry") == seller["industry"]:
                        strength += 1.5
                    acq_geo = acq.get("geography")
                    if acq_geo and self._cities_are_close(seller["geography"], acq_geo):
                        strength += 1.0
            if strength > 0:
                self.graph.add_edge(self.seller_id, buyer_id, weight=strength)

        return self

    def get_plot_figure(self, top_n: int = 5):
        edges = [
            {"buyer_id": v, "weight": d["weight"]}
            for u, v, d in self.graph.edges(data=True) if u == self.seller_id
        ]
        edges.sort(key=lambda x: x["weight"], reverse=True)
        top_edges = edges[:top_n]
        if not top_edges:
            return None

        nodes = [self.seller_id] + [e["buyer_id"] for e in top_edges]
        subg = self.graph.subgraph(nodes)
        fig, ax = plt.subplots(figsize=(12, 7))
        pos = nx.spring_layout(subg, seed=42)
        colors = ["lightgreen" if n == self.seller_id else "lightblue" for n in subg.nodes()]
        nx.draw(subg, pos, node_color=colors, node_size=3000, with_labels=False, ax=ax)

        labels = {}
        for node in subg.nodes():
            if node == self.seller_id:
                labels[node] = "SELLER"
            else:
                labels[node] = self.graph.nodes[node].get("name", str(node))
        nx.draw_networkx_labels(subg, pos, labels, font_size=9, ax=ax)

        elabels = {(self.seller_id, e["buyer_id"]): f"{e['weight']:.1f}" for e in top_edges}
        nx.draw_networkx_edge_labels(subg, pos, elabels, font_color="red", ax=ax)

        ax.set_title(f"Топ-{top_n} скрытых связей", fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        return fig