from datetime import datetime
from typing import Sequence

import matplotlib as mpl
import plotly.graph_objs as go
from plotly.offline import plot


mpl.use("Agg")


def _get_plot_data(
    data: Sequence[dict],
) -> tuple[list[str], list[float], list[float]]:
    timestamps = [
        datetime.fromisoformat(e["timestamp"]).strftime("%d %b %H:%M")
        for e in data
    ]
    sell_price = [
        (e["sell_g"] + e["sell_s"] / 100 + e["sell_c"] / 10_000) for e in data
    ]
    crafting_price = [
        (
            e["crafting_cost_g"]
            + e["crafting_cost_s"] / 100
            + e["crafting_cost_c"] / 10_000
        )
        for e in data
    ]
    return timestamps, sell_price, crafting_price


def get_date_plot(
    data: Sequence[dict],
    *,
    plot_mean: bool = False,
) -> str:
    if len(data) == 0:
        return ""

    timestamps, sell_price, crafting_price = _get_plot_data(data)

    traces = [
        go.Scatter(
            x=timestamps,
            y=sell_price,
            mode="lines+markers",
            name="Sell Price",
        ),
        go.Scatter(
            x=timestamps,
            y=crafting_price,
            mode="lines+markers",
            name="Crafting Price",
        ),
    ]

    if plot_mean:
        mean_sell = sum(sell_price) / len(sell_price)
        mean_crafting = sum(crafting_price) / len(crafting_price)

        traces.extend(
            go.Scatter(
                x=timestamps,
                y=[mean_sell] * len(timestamps),
                mode="lines",
                name="Mean Sell Price",
                line={"dash": "dash", "color": "orange"},
            )
        )
        traces.extend(
            go.Scatter(
                x=timestamps,
                y=[mean_crafting] * len(timestamps),
                mode="lines",
                name="Mean Crafting Price",
                line={"dash": "dash", "color": "cyan"},
            )
        )

    layout = go.Layout(
        xaxis={"title": "Time (UTC+2)", "tickangle": 50},
        yaxis={"title": "Price in Gold", "tickformat": ".2f"},
        template="plotly_dark",
        legend={"x": 0.5, "y": 1.15, "orientation": "h", "xanchor": "center"},
        margin={"l": 40, "r": 40, "t": 60, "b": 80},
    )

    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(height=700)
    config = {
        "displayModeBar": True,
        "modeBarButtonsToAdd": [],
        "scrollZoom": True,
        "modeBarButtons": [
            [
                "zoom2d",
                "pan2d",
                "zoomIn2d",
                "zoomOut2d",
                "resetScale2d",
                "autoScale2d",
            ]
        ],
    }
    return plot(
        fig,
        output_type="div",
        include_plotlyjs="cdn",
        config=config,
    )
