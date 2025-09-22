from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urljoin

import requests
from flask import Flask
from flask import render_template_string
from starlette.applications import Starlette
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.routing import Mount

from gw2tp.helper import host_url

from frontend.html_template import HTML_PAGE
from frontend.plotting import get_date_plot


api_base = host_url()
api_base = os.environ.get("BACKEND_URL", api_base)
flask_app = Flask(__name__)
FILE_DIR = Path(__file__).parent


@flask_app.route("/")
def index() -> str:
    return render_template_string(HTML_PAGE)


def history_base(
    item_name: str,
    full_name: str,
) -> str:
    print(os.environ)
    api_url = urljoin(api_base, f"/api/history?item_name={item_name}")
    response = requests.get(api_url, timeout=10.0)
    if response.status_code != 200:
        return f"Error fetching data: {response.text}"

    data = response.json()
    plot = get_date_plot(data=data)
    content = (FILE_DIR / "./templates/plot.html").read_text(encoding="utf-8")
    style = (FILE_DIR / "./static/style.css").read_text(encoding="utf-8")
    return render_template_string(
        content,
        item_name=full_name,
        history=data,
        plot=plot,
        style=style,
    )


@flask_app.route("/scholar_rune_history")
def history_scholar() -> str:
    return history_base("scholar_rune", "Scholar Rune")


@flask_app.route("/guardian_rune_history")
def history_guardian() -> str:
    return history_base("guardian_rune", "Guardian Rune")


@flask_app.route("/dragonhunter_rune_history")
def history_dragonhunter() -> str:
    return history_base("dragonhunter_rune", "Dragonhunter Rune")


@flask_app.route("/relic_of_fireworks_history")
def history_fireworks() -> str:
    return history_base("relic_of_fireworks", "Relic of Fireworks")


@flask_app.route("/relic_of_thief_history")
def history_thief() -> str:
    return history_base("relic_of_thief", "Relic of Thief")


@flask_app.route("/relic_of_aristocracy_history")
def history_aristocracy() -> str:
    return history_base("relic_of_aristocracy", "Relic of Aristocracy")


app = Starlette(
    routes=[
        Mount("/", app=WSGIMiddleware(flask_app)),
    ],
)
