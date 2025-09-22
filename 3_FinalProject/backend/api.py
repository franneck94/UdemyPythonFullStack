from __future__ import annotations

import datetime
from typing import Any
from typing import Dict

import httpx
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from gw2tp.constants import API
from gw2tp.constants import TAX_RATE
from gw2tp.constants import ItemIDs
from gw2tp.constants import Kits
from gw2tp.db_schema import get_db_data
from gw2tp.helper import copper_to_gsc
from gw2tp.helper import gsc_dict_to_copper
from gw2tp.helper import host_url

from backend.db import db
from backend.scheduler import start_scheduler


api_base = host_url()
fastapi_app = FastAPI()


def get_sub_dct(
    item_name: str,
    copper_price: float,
) -> Dict[str, Any]:
    g, s, c = copper_to_gsc(copper_price)
    return {
        f"{item_name}_g": g,
        f"{item_name}_s": s,
        f"{item_name}_c": c,
    }


def fetch_tp_prices(
    item_ids: list[int],
) -> dict[int, dict[str, Any]]:
    params = {"ids": ",".join(str(i) for i in item_ids)}
    with httpx.Client() as client:
        response = client.get(
            API.GW2_COMMERCE_API_URL,
            params=params,
            timeout=10.0,
        )
    response.raise_for_status()
    data: list[dict[str, Any]] = response.json()
    if len(data) == 0:
        raise RuntimeError("No items found")

    fetched_data: dict[int, dict[str, Any]] = {}
    for item in data:
        item_id = int(item["id"])
        buy_price = int(item["buys"]["unit_price"])
        sell_price = int(item["sells"]["unit_price"])
        flip_profit = int(round(sell_price * TAX_RATE, 6) - buy_price)
        buy_g, buy_s, buy_c = copper_to_gsc(buy_price)
        sell_g, sell_s, sell_c = copper_to_gsc(sell_price)
        flip_g, flip_s, flip_c = copper_to_gsc(flip_profit)

        fetched_data[item_id] = {
            "buy": buy_price,
            "sell": sell_price,
            "buy_g": buy_g,
            "buy_s": buy_s,
            "buy_c": buy_c,
            "sell_g": sell_g,
            "sell_s": sell_s,
            "sell_c": sell_c,
            "flip_g": flip_g,
            "flip_s": flip_s,
            "flip_c": flip_c,
            "sell_after_tax_g": int(sell_price * TAX_RATE // 10_000),
            "sell_after_tax_s": int((sell_price * TAX_RATE % 10_000) // 100),
            "sell_after_tax_c": int(sell_price * TAX_RATE % 100),
        }
    return fetched_data


def get_unid_gear_data(
    gear_id: int,
) -> dict[int, dict[str, float]] | None:
    try:
        fetched_data = fetch_tp_prices(
            [
                gear_id,
                ItemIDs.ECTOPLASM,
                ItemIDs.LUCENT_MOTE,
                ItemIDs.MIRTHIL,
                ItemIDs.ELDER_WOOD,
                ItemIDs.THICK_LEATHER,
                ItemIDs.GOSSAMER_SCRAP,
                ItemIDs.SILK_SCRAP,
                ItemIDs.HARDENED_LEATHER,
                ItemIDs.ANCIENT_WOOD_LOG,
                ItemIDs.SYMBOL_OF_ENH,
                ItemIDs.SYMBOL_OF_PAIN,
                ItemIDs.ORICHALCUM_ORE,
                ItemIDs.SYMBOL_OF_CONTROL,
                ItemIDs.CHARM_OF_BRILLIANCE,
                ItemIDs.CHARM_OF_POTENCE,
                ItemIDs.CHARM_OF_SKILL,
                ItemIDs.COMMON_GEAR,
            ],
        )
    except Exception:
        return None

    return fetched_data


@fastapi_app.get("/history")
async def get_item_history(
    item_name: str,
) -> JSONResponse:
    end_datetime = datetime.datetime.now(
        tz=datetime.timezone(datetime.timedelta(hours=2), "UTC")
    )
    start_datetime = end_datetime - datetime.timedelta(hours=24)
    try:
        data = get_db_data(
            db,
            item_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        return JSONResponse(content=jsonable_encoder(data))
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500,
        )


@fastapi_app.get("/price")
async def get_price(
    item_id: int,
) -> JSONResponse:
    try:
        # with flask_app.app_context():
        data = fetch_tp_prices([item_id])
        return JSONResponse(content=jsonable_encoder(data[item_id]))
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))


@fastapi_app.get("/rare_gear_salvage")
def get_rare_gear_salvage() -> JSONResponse:
    fetched_data = get_unid_gear_data(gear_id=ItemIDs.RARE_UNID_GEAR)
    if fetched_data is None:
        return JSONResponse(content=jsonable_encoder({"error"}))

    stack_buy = fetched_data[ItemIDs.RARE_UNID_GEAR]["buy"] * 250.0
    ecto_sell = fetched_data[ItemIDs.ECTOPLASM]["sell"]
    lucent_mote_sell = fetched_data[ItemIDs.LUCENT_MOTE]["sell"]
    mithril_sell = fetched_data[ItemIDs.MIRTHIL]["sell"]
    elder_wood_sell = fetched_data[ItemIDs.ELDER_WOOD]["sell"]
    thick_leather_sell = fetched_data[ItemIDs.THICK_LEATHER]["sell"]
    gossamer_scrap_sell = fetched_data[ItemIDs.GOSSAMER_SCRAP]["sell"]
    silk_scrap_sell = fetched_data[ItemIDs.SILK_SCRAP]["sell"]
    hardened_sell = fetched_data[ItemIDs.HARDENED_LEATHER]["sell"]
    ancient_wood_sell = fetched_data[ItemIDs.ANCIENT_WOOD_LOG]["sell"]
    symbol_of_enh_sell = fetched_data[ItemIDs.SYMBOL_OF_ENH]["sell"]
    symbol_of_pain_sell = fetched_data[ItemIDs.SYMBOL_OF_PAIN]["sell"]
    orichalcum_sell = fetched_data[ItemIDs.ORICHALCUM_ORE]["sell"]
    symbol_of_control_sell = fetched_data[ItemIDs.SYMBOL_OF_CONTROL]["sell"]
    charm_of_brilliance_sell = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["sell"]
    charm_of_potence_sell = fetched_data[ItemIDs.CHARM_OF_POTENCE]["sell"]
    charm_of_skill_sell = fetched_data[ItemIDs.CHARM_OF_SKILL]["sell"]

    mats_value_after_tax = (
        mithril_sell * (250.0 * 0.4879) * TAX_RATE
        + elder_wood_sell * (250.0 * 0.3175) * TAX_RATE
        + silk_scrap_sell * (250.0 * 0.3367) * TAX_RATE
        + thick_leather_sell * (250.0 * 0.3457) * TAX_RATE
        + orichalcum_sell * (250.0 * 0.041) * TAX_RATE
        + ancient_wood_sell * (250.0 * 0.0249) * TAX_RATE
        + gossamer_scrap_sell * (250.0 * 0.018) * TAX_RATE
        + hardened_sell * (250.0 * 0.0162) * TAX_RATE
        + ecto_sell * (250.0 * 0.87) * TAX_RATE  # lowered
        + lucent_mote_sell * (250.0 * 0.2387) * TAX_RATE
        + symbol_of_control_sell * (250.0 * 0.001) * TAX_RATE
        + symbol_of_enh_sell * (250.0 * 0.0003) * TAX_RATE
        + symbol_of_pain_sell * (250.0 * 0.0004) * TAX_RATE
        + charm_of_brilliance_sell * (250.0 * 0.0006) * TAX_RATE
        + charm_of_potence_sell * (250.0 * 0.0009) * TAX_RATE
        + charm_of_skill_sell * (250.0 * 0.0009) * TAX_RATE
    )

    salvage_costs = Kits.SILVER_FED * 250.0

    profit_stack = mats_value_after_tax - stack_buy - salvage_costs

    data = {
        **get_sub_dct("stack_buy", stack_buy),
        **get_sub_dct("salvage_costs", salvage_costs),
        **get_sub_dct("mats_value_after_tax", mats_value_after_tax),
        **get_sub_dct("profit_stack", profit_stack),
    }
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/rare_weapon_craft")
def get_rare_weapon_craft() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.ECTOPLASM,
                ItemIDs.MITHRIL_INGOT,
                ItemIDs.MITHRIL_ORE,
                ItemIDs.ELDER_WOOD_PLANK,
                ItemIDs.ELDER_WOOD_LOG,
                ItemIDs.LARGE_CLAW,
                ItemIDs.POTENT_BLOOD,
                ItemIDs.LARGE_BONE,
                ItemIDs.INTRICATE_TOTEM,
                ItemIDs.LARGE_FANG,
                ItemIDs.POTENT_VENOM_SAC,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    ecto_sell_after_tax = fetched_data[ItemIDs.ECTOPLASM]["sell"] * TAX_RATE
    mithril_ore_buy = fetched_data[ItemIDs.MITHRIL_ORE]["buy"]
    mithril_ingot_buy = fetched_data[ItemIDs.MITHRIL_INGOT]["buy"]
    elder_wood_log_buy = fetched_data[ItemIDs.ELDER_WOOD_LOG]["buy"]
    elder_wood_plank_buy = fetched_data[ItemIDs.ELDER_WOOD_PLANK]["buy"]
    large_claw_buy = fetched_data[ItemIDs.LARGE_CLAW]["buy"]
    potent_blood_buy = fetched_data[ItemIDs.POTENT_BLOOD]["buy"]
    large_bone_buy = fetched_data[ItemIDs.LARGE_BONE]["buy"]
    intricate_totem_buy = fetched_data[ItemIDs.INTRICATE_TOTEM]["buy"]
    large_fang_buy = fetched_data[ItemIDs.LARGE_FANG]["buy"]
    potent_sac_buy = fetched_data[ItemIDs.POTENT_VENOM_SAC]["buy"]

    lowest_t5_mat = min(
        large_claw_buy,
        potent_blood_buy,
        large_bone_buy,
        intricate_totem_buy,
        large_fang_buy,
        potent_sac_buy,
    )

    crafting_cost_ingot = (
        mithril_ingot_buy
        if mithril_ingot_buy < 2.0 * mithril_ore_buy
        else mithril_ore_buy * 2.0
    )
    crafting_cost_plank = (
        elder_wood_plank_buy
        if elder_wood_plank_buy < 3.0 * elder_wood_log_buy
        else elder_wood_log_buy * 3.0
    )

    crafting_cost_backing = 2.0 * crafting_cost_ingot
    crafting_cost_boss = 2.0 * crafting_cost_ingot
    crafting_cost_dowwl = 2.0 * crafting_cost_plank + 3.0 * crafting_cost_ingot
    crafting_cost_inscr = 15.0 * lowest_t5_mat + 2.0 * crafting_cost_dowwl

    crafting_cost_with_cheap_materials = (
        crafting_cost_inscr + crafting_cost_backing + crafting_cost_boss
    )
    rare_gear_craft_profit = (
        ecto_sell_after_tax * 0.9 - crafting_cost_with_cheap_materials
    )

    data = {
        **get_sub_dct("crafting_cost", crafting_cost_with_cheap_materials),
        **get_sub_dct("ecto_sell_after_tax", ecto_sell_after_tax),
        **get_sub_dct("profit", rare_gear_craft_profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/t5_mats_buy")
def get_t5_mats_buy() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.LARGE_CLAW,
                ItemIDs.POTENT_BLOOD,
                ItemIDs.LARGE_BONE,
                ItemIDs.INTRICATE_TOTEM,
                ItemIDs.LARGE_FANG,
                ItemIDs.POTENT_VENOM_SAC,
                ItemIDs.LARGE_SCALE,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    large_claw_buy = fetched_data[ItemIDs.LARGE_CLAW]["buy"]
    potent_blood_buy = fetched_data[ItemIDs.POTENT_BLOOD]["buy"]
    large_bone_buy = fetched_data[ItemIDs.LARGE_BONE]["buy"]
    intricate_totem_buy = fetched_data[ItemIDs.INTRICATE_TOTEM]["buy"]
    large_fang_buy = fetched_data[ItemIDs.LARGE_FANG]["buy"]
    venom_sac_buy = fetched_data[ItemIDs.POTENT_VENOM_SAC]["buy"]
    large_scale_buy = fetched_data[ItemIDs.LARGE_SCALE]["buy"]

    data = {
        **get_sub_dct("large_claw", large_claw_buy),
        **get_sub_dct("potent_blood", potent_blood_buy),
        **get_sub_dct("large_bone", large_bone_buy),
        **get_sub_dct("intricate_totem", intricate_totem_buy),
        **get_sub_dct("large_fang", large_fang_buy),
        **get_sub_dct("potent_venom", venom_sac_buy),
        **get_sub_dct("large_scale", large_scale_buy),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/mats_crafting_compare")
def get_mats_crafting_compare() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.MITHRIL_INGOT,
                ItemIDs.MITHRIL_ORE,
                ItemIDs.ELDER_WOOD_PLANK,
                ItemIDs.ELDER_WOOD_LOG,
                ItemIDs.LUCENT_MOTE,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    mithril_ore_buy = fetched_data[ItemIDs.MITHRIL_ORE]["buy"]
    mithril_ingot_buy = fetched_data[ItemIDs.MITHRIL_INGOT]["buy"]
    elder_wood_log_buy = fetched_data[ItemIDs.ELDER_WOOD_LOG]["buy"]
    elder_wood_plank_buy = fetched_data[ItemIDs.ELDER_WOOD_PLANK]["buy"]
    lucent_mote_buy = fetched_data[ItemIDs.LUCENT_MOTE]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]

    lucent_mote_to_crystal = lucent_mote_buy * 10.0

    data = {
        **get_sub_dct("mithril_ore_to_ingot", mithril_ore_buy * 2.0),
        **get_sub_dct("mithril_ingot_buy", mithril_ingot_buy),
        **get_sub_dct("elder_wood_log_to_plank", elder_wood_log_buy * 3.0),
        **get_sub_dct("elder_wood_plank_buy", elder_wood_plank_buy),
        **get_sub_dct("lucent_mote_to_crystal", lucent_mote_to_crystal),
        **get_sub_dct("lucent_crystal_buy", lucent_crystal_buy),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/scholar_rune")
def get_scholar_rune() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.ECTOPLASM,
                ItemIDs.ELABORATE_TOTEM,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
                ItemIDs.CHARM_OF_BRILLIANCE,
                ItemIDs.LUCENT_MOTE,
                ItemIDs.SCHOLAR_RUNE,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    ecto_buy = fetched_data[ItemIDs.ECTOPLASM]["buy"]
    totem_buy = fetched_data[ItemIDs.ELABORATE_TOTEM]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]
    charm_buy = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["buy"]
    lucent_mote_buy = fetched_data[ItemIDs.LUCENT_MOTE]["buy"]

    scholar_rune_sell = fetched_data[ItemIDs.SCHOLAR_RUNE]["sell"]

    crafting_cost = (
        ecto_buy * 5.0
        + totem_buy * 5.0
        + lucent_crystal_buy * 8.0
        + charm_buy * 2.0
    )
    crafting_cost2 = (
        ecto_buy * 5.0
        + totem_buy * 5.0
        + lucent_mote_buy * 80.0
        + charm_buy * 2.0
    )

    profit = scholar_rune_sell * TAX_RATE - crafting_cost
    profit2 = scholar_rune_sell * TAX_RATE - crafting_cost2

    cheap_crafting_cost = min(crafting_cost, crafting_cost2)
    highest_profit = max(profit, profit2)

    data = {
        **get_sub_dct("crafting_cost", cheap_crafting_cost),
        **get_sub_dct("sell", scholar_rune_sell),
        **get_sub_dct("profit", highest_profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/guardian_rune")
def get_guardian_rune() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.GUARD_RUNE,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
                ItemIDs.CHARGED_LOADSTONE,
                ItemIDs.CHARM_OF_POTENCE,
                ItemIDs.ECTOPLASM,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    rune_sell = fetched_data[ItemIDs.GUARD_RUNE]["sell"]
    charged_loadstone_sell = fetched_data[ItemIDs.CHARGED_LOADSTONE]["sell"]
    charm_buy = fetched_data[ItemIDs.CHARM_OF_POTENCE]["buy"]
    ecto_buy = fetched_data[ItemIDs.ECTOPLASM]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]

    crafting_cost = (
        charged_loadstone_sell
        + charm_buy
        + ecto_buy * 5.0
        + lucent_crystal_buy * 12.0
    )

    profit = rune_sell * TAX_RATE - crafting_cost

    data = {
        **get_sub_dct("crafting_cost", crafting_cost),
        **get_sub_dct("sell", rune_sell),
        **get_sub_dct("profit", profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/dragonhunter_rune")
def get_dragonhunter_rune() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.GUARD_RUNE,
                ItemIDs.DRAGONHUNTER_RUNE,
                ItemIDs.EVERGREEN_LOADSTONE,
                ItemIDs.BARBED_THORN,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
                ItemIDs.CHARGED_LOADSTONE,
                ItemIDs.CHARM_OF_POTENCE,
                ItemIDs.ECTOPLASM,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    rune_sell = fetched_data[ItemIDs.DRAGONHUNTER_RUNE]["sell"]
    charged_loadstone_sell = fetched_data[ItemIDs.CHARGED_LOADSTONE]["sell"]
    evergreen_loadstone_buy = fetched_data[ItemIDs.EVERGREEN_LOADSTONE]["buy"]
    thorns_buy = fetched_data[ItemIDs.BARBED_THORN]["buy"]
    charm_buy = fetched_data[ItemIDs.CHARM_OF_POTENCE]["buy"]
    ecto_buy = fetched_data[ItemIDs.ECTOPLASM]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]

    guardian_rune_cost = (
        charged_loadstone_sell
        + charm_buy
        + ecto_buy * 5.0
        + lucent_crystal_buy * 12.0
    )

    crafting_cost = (
        guardian_rune_cost * 1.0
        + evergreen_loadstone_buy * 1.0
        + thorns_buy * 10.0
    )

    profit = rune_sell * TAX_RATE - crafting_cost

    data = {
        **get_sub_dct("crafting_cost", crafting_cost),
        **get_sub_dct("sell", rune_sell),
        **get_sub_dct("profit", profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


def _get_relic_profits(
    crafting_cost_base: float,
    lucent_mote_buy: float,
    lucent_crystal_buy: float,
) -> tuple[float, float]:
    crafting_cost = crafting_cost_base + lucent_crystal_buy * 48.0
    crafting_cost2 = crafting_cost_base + lucent_mote_buy * 480.0
    return crafting_cost, crafting_cost2


@fastapi_app.get("/relic_of_fireworks")
def get_relic_of_fireworks() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.ECTOPLASM,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
                ItemIDs.CHARM_OF_SKILL,
                ItemIDs.LUCENT_MOTE,
                ItemIDs.RELIC_OF_FIREWORKS,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    ecto_buy = fetched_data[ItemIDs.ECTOPLASM]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]
    charm_buy = fetched_data[ItemIDs.CHARM_OF_SKILL]["buy"]
    lucent_mote_buy = fetched_data[ItemIDs.LUCENT_MOTE]["buy"]
    relic_sell = fetched_data[ItemIDs.RELIC_OF_FIREWORKS]["sell"]
    relic_buy = fetched_data[ItemIDs.RELIC_OF_FIREWORKS]["buy"]

    crafting_cost_base = ecto_buy * 15.0 + charm_buy * 3.0
    crafting_cost, crafting_cost2 = _get_relic_profits(
        crafting_cost_base,
        lucent_mote_buy,
        lucent_crystal_buy,
    )

    profit = relic_sell * TAX_RATE - crafting_cost
    profit2 = relic_sell * TAX_RATE - crafting_cost2

    cheap_crafting_cost = min(
        crafting_cost,
        crafting_cost2,
    )
    highest_profit = max(profit, profit2)
    relic_of_fireworks_flip = (relic_sell * TAX_RATE) - relic_buy

    data = {
        **get_sub_dct("crafting_cost", cheap_crafting_cost),
        **get_sub_dct("sell", relic_sell),
        **get_sub_dct("flip", relic_of_fireworks_flip),
        **get_sub_dct("profit", highest_profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/relic_of_thief")
def get_relic_of_thief() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.ECTOPLASM,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
                ItemIDs.LUCENT_MOTE,
                ItemIDs.CHARM_OF_SKILL,
                ItemIDs.CURED_HARDENED_LEATHER_SQUARE,
                ItemIDs.RELIC_OF_THIEF,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    ecto_buy = fetched_data[ItemIDs.ECTOPLASM]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]
    charm_buy = fetched_data[ItemIDs.CHARM_OF_SKILL]["buy"]
    lucent_mote_buy = fetched_data[ItemIDs.LUCENT_MOTE]["buy"]
    leather_buy = fetched_data[ItemIDs.CURED_HARDENED_LEATHER_SQUARE]["buy"]
    relic_sell = fetched_data[ItemIDs.RELIC_OF_THIEF]["sell"]
    relic_buy = fetched_data[ItemIDs.RELIC_OF_THIEF]["buy"]

    crafting_cost_base = ecto_buy * 15.0 + charm_buy * 3.0 + leather_buy * 5.0
    crafting_cost, crafting_cost2 = _get_relic_profits(
        crafting_cost_base,
        lucent_mote_buy,
        lucent_crystal_buy,
    )

    profit = relic_sell * TAX_RATE - crafting_cost
    profit2 = relic_sell * TAX_RATE - crafting_cost2

    cheap_crafting_cost = min(
        crafting_cost,
        crafting_cost2,
    )
    highest_profit = max(profit, profit2)
    relic_of_fireworks_flip = (relic_sell * TAX_RATE) - relic_buy

    data = {
        **get_sub_dct("crafting_cost", cheap_crafting_cost),
        **get_sub_dct("sell", relic_sell),
        **get_sub_dct("flip", relic_of_fireworks_flip),
        **get_sub_dct("profit", highest_profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/relic_of_aristocracy")
def get_relic_of_aristocracy() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.ECTOPLASM,
                ItemIDs.PILE_OF_LUCENT_CRYSTAL,
                ItemIDs.LUCENT_MOTE,
                ItemIDs.CHARM_OF_BRILLIANCE,
                ItemIDs.RELIC_OF_ARISTOCRACY,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    ecto_buy = fetched_data[ItemIDs.ECTOPLASM]["buy"]
    lucent_crystal_buy = fetched_data[ItemIDs.PILE_OF_LUCENT_CRYSTAL]["buy"]
    charm_buy = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["buy"]
    lucent_mote_buy = fetched_data[ItemIDs.LUCENT_MOTE]["buy"]
    bottle_elonian_wine_buy = 2504.0
    relic_sell = fetched_data[ItemIDs.RELIC_OF_ARISTOCRACY]["sell"]
    relic_buy = fetched_data[ItemIDs.RELIC_OF_ARISTOCRACY]["buy"]

    crafting_cost_base = (
        ecto_buy * 15.0 + charm_buy * 3.0 + bottle_elonian_wine_buy * 3.0
    )
    crafting_cost, crafting_cost2 = _get_relic_profits(
        crafting_cost_base,
        lucent_mote_buy,
        lucent_crystal_buy,
    )

    profit = relic_sell * TAX_RATE - crafting_cost
    profit2 = relic_sell * TAX_RATE - crafting_cost2

    cheap_crafting_cost = min(
        crafting_cost,
        crafting_cost2,
    )
    highest_profit = max(profit, profit2)
    relic_of_fireworks_flip = (relic_sell * TAX_RATE) - relic_buy

    data = {
        **get_sub_dct("crafting_cost", cheap_crafting_cost),
        **get_sub_dct("sell", relic_sell),
        **get_sub_dct("flip", relic_of_fireworks_flip),
        **get_sub_dct("profit", highest_profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/common_gear_salvage")
def get_common_gear_salvage() -> JSONResponse:
    fetched_data = get_unid_gear_data(gear_id=ItemIDs.COMMON_GEAR)
    if fetched_data is None:
        return JSONResponse(content=jsonable_encoder({"error"}))

    stack_buy = fetched_data[ItemIDs.COMMON_GEAR]["buy"] * 250.0
    ecto_sell = fetched_data[ItemIDs.ECTOPLASM]["sell"]
    lucent_mote_sell = fetched_data[ItemIDs.LUCENT_MOTE]["sell"]
    mithril_sell = fetched_data[ItemIDs.MIRTHIL]["sell"]
    elder_wood_sell = fetched_data[ItemIDs.ELDER_WOOD]["sell"]
    thick_leather_sell = fetched_data[ItemIDs.THICK_LEATHER]["sell"]
    gossamer_scrap_sell = fetched_data[ItemIDs.GOSSAMER_SCRAP]["sell"]
    silk_scrap_sell = fetched_data[ItemIDs.SILK_SCRAP]["sell"]
    hardened_sell = fetched_data[ItemIDs.HARDENED_LEATHER]["sell"]
    ancient_wood_sell = fetched_data[ItemIDs.ANCIENT_WOOD_LOG]["sell"]
    symbol_of_enh_sell = fetched_data[ItemIDs.SYMBOL_OF_ENH]["sell"]
    symbol_of_pain_sell = fetched_data[ItemIDs.SYMBOL_OF_PAIN]["sell"]
    orichalcum_sell = fetched_data[ItemIDs.ORICHALCUM_ORE]["sell"]
    symbol_of_control_sell = fetched_data[ItemIDs.SYMBOL_OF_CONTROL]["sell"]
    charm_of_brilliance_sell = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["sell"]
    charm_of_potence_sell = fetched_data[ItemIDs.CHARM_OF_POTENCE]["sell"]
    charm_of_skill_sell = fetched_data[ItemIDs.CHARM_OF_SKILL]["sell"]

    mats_value_after_tax = (
        mithril_sell * (250.0 * 0.4291) * TAX_RATE
        + elder_wood_sell * (250.0 * 0.3884) * TAX_RATE
        + silk_scrap_sell * (250.0 * 0.3059) * TAX_RATE
        + thick_leather_sell * (250.0 * 0.25) * TAX_RATE  # lowered
        + orichalcum_sell * (250.0 * 0.0394) * TAX_RATE
        + ancient_wood_sell * (250.0 * 0.0305) * TAX_RATE
        + gossamer_scrap_sell * (250.0 * 0.0153) * TAX_RATE
        + hardened_sell * (250.0 * 0.0143) * TAX_RATE
        + ecto_sell * (250.0 * 0.007) * TAX_RATE  # lowered
        + lucent_mote_sell * (250.0 * 0.1075) * TAX_RATE  # lowered
        + symbol_of_control_sell * (250.0 * 0.0002) * TAX_RATE
        + symbol_of_enh_sell * (250.0 * 0.0006) * TAX_RATE
        + symbol_of_pain_sell * (250.0 * 0.0005) * TAX_RATE
        + charm_of_brilliance_sell * (250.0 * 0.0004) * TAX_RATE
        + charm_of_potence_sell * (250.0 * 0.0003) * TAX_RATE
        + charm_of_skill_sell * (250.0 * 0.0003) * TAX_RATE
    )

    salvage_costs = (
        Kits.COPPER_FED * 223.0
        + Kits.RUNECRAFTER * 25.0
        + Kits.SILVER_FED * 2.0
    )

    profit_stack = mats_value_after_tax - stack_buy - salvage_costs

    data = {
        **get_sub_dct("stack_buy", stack_buy),
        **get_sub_dct("salvage_costs", salvage_costs),
        **get_sub_dct("mats_value_after_tax", mats_value_after_tax),
        **get_sub_dct("profit_stack", profit_stack),
    }
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/gear_salvage")
def get_gear_salvage() -> JSONResponse:
    fetched_data = get_unid_gear_data(gear_id=ItemIDs.UNID_GEAR)
    if fetched_data is None:
        return JSONResponse(content=jsonable_encoder({"error"}))

    stack_buy = fetched_data[ItemIDs.UNID_GEAR]["buy"] * 250.0
    ecto_sell = fetched_data[ItemIDs.ECTOPLASM]["sell"]
    lucent_mote_sell = fetched_data[ItemIDs.LUCENT_MOTE]["sell"]
    mithril_sell = fetched_data[ItemIDs.MIRTHIL]["sell"]
    elder_wood_sell = fetched_data[ItemIDs.ELDER_WOOD]["sell"]
    thick_leather_sell = fetched_data[ItemIDs.THICK_LEATHER]["sell"]
    gossamer_scrap_sell = fetched_data[ItemIDs.GOSSAMER_SCRAP]["sell"]
    silk_scrap_sell = fetched_data[ItemIDs.SILK_SCRAP]["sell"]
    hardened_sell = fetched_data[ItemIDs.HARDENED_LEATHER]["sell"]
    ancient_wood_sell = fetched_data[ItemIDs.ANCIENT_WOOD_LOG]["sell"]
    symbol_of_enh_sell = fetched_data[ItemIDs.SYMBOL_OF_ENH]["sell"]
    symbol_of_pain_sell = fetched_data[ItemIDs.SYMBOL_OF_PAIN]["sell"]
    orichalcum_sell = fetched_data[ItemIDs.ORICHALCUM_ORE]["sell"]
    symbol_of_control_sell = fetched_data[ItemIDs.SYMBOL_OF_CONTROL]["sell"]
    charm_of_brilliance_sell = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["sell"]
    charm_of_potence_sell = fetched_data[ItemIDs.CHARM_OF_POTENCE]["sell"]
    charm_of_skill_sell = fetched_data[ItemIDs.CHARM_OF_SKILL]["sell"]

    mats_value_after_tax = (
        mithril_sell * (250.0 * 0.4299) * TAX_RATE
        + elder_wood_sell * (250.0 * 0.3564) * TAX_RATE
        + silk_scrap_sell * (250.0 * 0.3521) * TAX_RATE
        + thick_leather_sell * (250.0 * 0.2673) * TAX_RATE
        + orichalcum_sell * (250.0 * 0.0387) * TAX_RATE
        + ancient_wood_sell * (250.0 * 0.0287) * TAX_RATE
        + gossamer_scrap_sell * (250.0 * 0.018) * TAX_RATE
        + hardened_sell * (250.0 * 0.0164) * TAX_RATE  # lowered
        + ecto_sell * (250.0 * 0.0291) * TAX_RATE  # lowered
        + lucent_mote_sell * (250.0 * 0.98) * TAX_RATE
        + symbol_of_control_sell * (250.0 * 0.0018) * TAX_RATE
        + symbol_of_enh_sell * (250.0 * 0.001) * TAX_RATE
        + symbol_of_pain_sell * (250.0 * 0.0006) * TAX_RATE
        + charm_of_brilliance_sell * (250.0 * 0.0042) * TAX_RATE
        + charm_of_potence_sell * (250.0 * 0.0029) * TAX_RATE
        + charm_of_skill_sell * (250.0 * 0.0028) * TAX_RATE
    )

    salvage_costs = Kits.RUNECRAFTER * 245 + Kits.SILVER_FED * 5

    profit_stack = mats_value_after_tax - stack_buy - salvage_costs

    data = {
        **get_sub_dct("stack_buy", stack_buy),
        **get_sub_dct("salvage_costs", salvage_costs),
        **get_sub_dct("mats_value_after_tax", mats_value_after_tax),
        **get_sub_dct("profit_stack", profit_stack),
    }
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/profits")
def get_profits() -> JSONResponse:
    data = {}
    try:
        for craft in API.CRAFTS:
            response = httpx.Client().get(
                f"{api_base}{craft}",
            )
            data_ = response.json()
            profit = gsc_dict_to_copper(data_)
            data = {**data, **get_sub_dct(f"{craft}_profit", profit)}
    except Exception:  # noqa: S110
        pass
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/symbol_enh_forge")
def get_symbol_enh_forge() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.SYMBOL_OF_ENH,
                ItemIDs.SYMBOL_OF_PAIN,
                ItemIDs.SYMBOL_OF_CONTROL,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    enh_buy = fetched_data[ItemIDs.SYMBOL_OF_ENH]["buy"]
    enh_sell = fetched_data[ItemIDs.SYMBOL_OF_ENH]["sell"]
    pain_sell = fetched_data[ItemIDs.SYMBOL_OF_PAIN]["sell"]
    control_sell = fetched_data[ItemIDs.SYMBOL_OF_CONTROL]["sell"]

    cost = enh_buy * 3.0
    reward = enh_sell * 0.2 + pain_sell * 0.4 + control_sell * 0.4
    profit = (reward * TAX_RATE) - cost

    data = {
        **get_sub_dct("cost", cost),
        **get_sub_dct("profit_per_try", profit),
        **get_sub_dct("profit_per_shard", profit * 10.0),
    }
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/charm_brilliance_forge")
def get_charm_brilliance_forge() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.CHARM_OF_BRILLIANCE,
                ItemIDs.CHARM_OF_POTENCE,
                ItemIDs.CHARM_OF_SKILL,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    charm_brilliance_buy = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["buy"]
    charm_brilliance_sell = fetched_data[ItemIDs.CHARM_OF_BRILLIANCE]["sell"]
    charm_potence_sell = fetched_data[ItemIDs.CHARM_OF_POTENCE]["sell"]
    charm_skill_sell = fetched_data[ItemIDs.CHARM_OF_SKILL]["sell"]

    cost = charm_brilliance_buy * 3.0
    reward = (
        charm_brilliance_sell * 0.2
        + charm_potence_sell * 0.4
        + charm_skill_sell * 0.4
    )
    profit = (reward * TAX_RATE) - cost

    data = {
        **get_sub_dct("cost", cost),
        **get_sub_dct("profit_per_try", profit),
        **get_sub_dct("profit_per_shard", profit * 10.0),
    }
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/loadstone_forge")
def get_loadstone_forge() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.ONYX_LOADSTONE,
                ItemIDs.CHARGED_LOADSTONE,
                ItemIDs.CORRUPTED_LOADSTONE,
                ItemIDs.DESTROYER_LOADSTONE,
                ItemIDs.CRYSTALINE_DUST,
                ItemIDs.ONYX_CORE,
                ItemIDs.DESTROYER_CORE,
                ItemIDs.CORRUPTED_CORE,
                ItemIDs.CHARGED_CORE,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    onyx_sell = fetched_data[ItemIDs.ONYX_LOADSTONE]["buy"]
    charged_sell = fetched_data[ItemIDs.CHARGED_LOADSTONE]["sell"]
    corrupted_sell = fetched_data[ItemIDs.CORRUPTED_LOADSTONE]["sell"]
    destroyer_sell = fetched_data[ItemIDs.DESTROYER_LOADSTONE]["sell"]
    crystal_dust_buy = fetched_data[ItemIDs.CRYSTALINE_DUST]["buy"]
    onyx_core_cost = fetched_data[ItemIDs.ONYX_CORE]["buy"]
    charged_core_cost = fetched_data[ItemIDs.CHARGED_CORE]["buy"]
    corrupted_core_cost = fetched_data[ItemIDs.CORRUPTED_CORE]["buy"]
    destroyer_core_cost = fetched_data[ItemIDs.DESTROYER_CORE]["buy"]

    elonian_cost = 2_500

    onyx_cost = onyx_core_cost * 2 + crystal_dust_buy + elonian_cost
    onyx_profit = (onyx_sell * 0.85) - onyx_cost

    charged_cost = charged_core_cost * 2 + crystal_dust_buy + elonian_cost
    charged_profit = (charged_sell * 0.85) - charged_cost

    corrupted_cost = corrupted_core_cost * 2 + crystal_dust_buy + elonian_cost
    corrupted_profit = (corrupted_sell * 0.85) - corrupted_cost

    destroyer_cost = destroyer_core_cost * 2 + crystal_dust_buy + elonian_cost
    destroyer_profit = (destroyer_sell * 0.85) - destroyer_cost

    data = {
        **get_sub_dct("onyx", onyx_profit),
        **get_sub_dct("charged", charged_profit),
        **get_sub_dct("corrupted", corrupted_profit),
        **get_sub_dct("destroyer", destroyer_profit),
    }
    return JSONResponse(content=jsonable_encoder(data))


@fastapi_app.get("/thesis_on_masterful_malice")
def get_thesis_on_masterful_malice() -> JSONResponse:
    try:
        fetched_data = fetch_tp_prices(
            [
                ItemIDs.THESIS_MASTERFUL_MALICE,
                ItemIDs.WRIT_MASTERFUL_MALICE,
                ItemIDs.CRYSTALINE_DUST,
                ItemIDs.ANCIENT_WOOD_LOG,
                ItemIDs.HARDENED_LEATHER,
                ItemIDs.ORICHALCUM_ORE,
                ItemIDs.GOSSAMER_SCRAP,
                ItemIDs.GOSSAMER_THREAD,
                ItemIDs.POUCH_OF_BLACK_PIGMENTS,
                ItemIDs.POUCH_OF_WHITE_PIGMENTS,
                ItemIDs.JUG_OF_WATER,
            ],
        )
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"error": str(e)}))

    masterful_malice_data = fetched_data[ItemIDs.THESIS_MASTERFUL_MALICE]
    masterful_malice_buy = fetched_data[ItemIDs.WRIT_MASTERFUL_MALICE]["buy"]
    crystal_dust_buy = fetched_data[ItemIDs.CRYSTALINE_DUST]["buy"]
    ancient_wood_log_buy = fetched_data[ItemIDs.ANCIENT_WOOD_LOG]["buy"]
    hardened_leather_buy = fetched_data[ItemIDs.HARDENED_LEATHER]["buy"]
    orichalcum_buy = fetched_data[ItemIDs.ORICHALCUM_ORE]["buy"]
    gossamer_scrap_buy = fetched_data[ItemIDs.GOSSAMER_SCRAP]["buy"]
    gossamer_thread_buy = fetched_data[ItemIDs.GOSSAMER_THREAD]["buy"]
    pouch_of_black_buy = fetched_data[ItemIDs.POUCH_OF_BLACK_PIGMENTS]["buy"]
    pouch_of_white_buy = fetched_data[ItemIDs.POUCH_OF_WHITE_PIGMENTS]["buy"]
    jug_of_water = fetched_data[ItemIDs.JUG_OF_WATER]["buy"]

    crafting_cost = (
        masterful_malice_buy * 3.0
        + crystal_dust_buy * 5.0
        + ancient_wood_log_buy * 48.0
        + hardened_leather_buy * 10.0
        + orichalcum_buy * 12.0
        + gossamer_scrap_buy * 20.0
        + gossamer_thread_buy * 10.0
        + pouch_of_black_buy * 3.0
        + pouch_of_white_buy * 3.0
        + jug_of_water * 20.0
    )

    sell = masterful_malice_data["sell"]
    flip = (sell * TAX_RATE) - masterful_malice_buy
    profit = (sell * TAX_RATE) - crafting_cost

    data = {
        **get_sub_dct("crafting_cost", crafting_cost),
        **get_sub_dct("sell", sell),
        **get_sub_dct("flip", flip),
        **get_sub_dct("profit", profit),
    }

    return JSONResponse(content=jsonable_encoder(data))


middleware = [Middleware(CORSMiddleware, allow_origins=["*"])]
app = Starlette(
    routes=[
        Mount("/api", app=fastapi_app),
    ],
    middleware=middleware,
)

start_scheduler()
