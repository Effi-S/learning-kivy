"""This module holds different plotting functions that are compatible kivy.

Building Notes:
    1) akivymd from:
        - run: pip install kivymd-extensions.akivymd (checked on version 1.2.6)
        - To buildozer.spec add: requirements = https://github.com/kivymd-extensions/akivymd/archive/main.zip
    2) Add matplotlib to requirements in buildozer.spec
        - run pip install matplotlib (checked on version 3.2.2)
        - To buildozer.spec add: requirements = matplotlib==3.2.2
    3) Get matplotlib backend package to kmplot folder
            - pip install kivy.garden / sudo apt-get install kivy_garden
            - garden install matplotlib
                (any issues see:  https://www.youtube.com/watch?v=ak6HwZyj1lM&ab_channel=SkSahil)
"""

from __future__ import annotations

from kivymd_extensions.akivymd.uix.charts import AKPieChart
from kmplot.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt


def plot_pie_chart(data: dict[str, float]) -> AKPieChart:
    """This function takes in a data dict name->quantity and returns a AKPieChart"""
    sum_values = sum(data.values()) or .0000001  # (delta to avoid zero devision)
    data = {k: (v / sum_values) * 100 for k, v in data.items()}
    sum_values = sum(data.values())
    leftover = 100 - sum_values
    data[list(data.keys())[-1]] += leftover
    print(data)

    chart = AKPieChart(
        items=[data],
    )
    return chart


def plot_graph(data: dict[str, float],
               x_label: str = None, y_label: str = 'Y',
               ) -> FigureCanvasKivyAgg:
    """Plot a graph of dates to values.
    e.g. plot_graph(data = {'2022-01-11': 100,
                            '2022-01-10': 100,
                            '2022-01-09': 300}, y_label='Calories')"""

    plt.rcParams.update({
        "figure.facecolor": (1.0, 0.0, 0.0, 0.0),  # red   with alpha = 30%
        "axes.facecolor": (0.0, 1.0, 0.0, 0.0),  # green with alpha = 0%
        "savefig.facecolor": (0.0, 0.0, 1.0, 0.2),  # blue  with alpha = 20%
        "figure.autolayout": True
    })
    data = {'-'.join(k.split('-')[1:]): v for k, v in data.items()}  # removing year
    if len(data) == 1:
        plt.bar(*zip(*data.items()), label=y_label)
    else:
        plt.plot(*zip(*data.items()), label=y_label)
    plt.legend()

    if x_label:
        plt.xlabel(x_label)

    ax = plt.gca()
    ax.grid(True)
    ax.yaxis.tick_right()
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', colors='green')
    ax.tick_params(axis='y', colors='green')

    plt.tight_layout()
    canvas = FigureCanvasKivyAgg(plt.gcf())
    plt.close()  # clearing memory of plt
    return canvas

