import os

from gw2tp.constants import API


def is_running_on_railway() -> bool:
    return "RAILWAY_STATIC_URL" in os.environ


def host_url() -> str:
    uses_server = is_running_on_railway()
    if uses_server:
        return API.PRODUCTION_API_URL
    return API.DEV_API_URL


def copper_to_gsc(
    copper: float,
) -> tuple[float, float, float]:
    negative = False
    if copper < 0:
        negative = True
        copper = abs(copper)

    gold = int(copper // 10_000)
    silver = int((copper % 10_000) // 100)
    copper_rest = int(copper % 100)

    if negative:
        gold = -gold
        silver = -silver
        copper_rest = -copper_rest

    return gold, silver, copper_rest


def gsc_to_copper(
    gold: float,
    silver: float,
    copper: float,
) -> float:
    return gold * 10_000 + silver * 100 + copper


def gsc_dict_to_copper(
    dct: dict[str, float],
) -> float:
    return dct["profit_g"] * 10_000 + dct["profit_s"] * 100 + dct["profit_c"]
