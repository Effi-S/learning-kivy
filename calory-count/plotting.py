from __future__ import annotations

from kivy.metrics import dp
from kivymd_extensions.akivymd.uix.charts import AKPieChart


def plot_pie_chart(data: dict[str, float],
                   pos_hint: dict = None) -> AKPieChart:
    """This function takes in a data dict name->quantity and returns a AKPieChart"""
    pos_hint = pos_hint or {"center_x": 0.5, "center_y": 0.5}
    sum_values = sum(data.values())
    data = {k: (v / sum_values) * 100 for k, v in data.items()}
    sum_values = sum(data.values())
    leftover = 100 - sum_values
    data[list(data.keys())[-1]] += leftover
    print(data)

    chart = AKPieChart(
        items=[data],
        size_hint=[None, None],
        size=(dp(300), dp(300)),
    )
    return chart


def plot_graph(data: dict[str, float],
               color: tuple = None,
               x_label: str = 'X', y_label: str = 'Y',
               ) -> int:
    pass
