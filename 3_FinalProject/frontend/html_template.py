# ruff: noqa: E501
from pathlib import Path

from gw2tp.constants import ItemIDs
from gw2tp.helper import host_url
from gw2tp.helper import is_running_on_railway


FILE_DIR = Path(__file__).parent
uses_server = is_running_on_railway()
api_base = host_url()

TABLE_HEADER = """
<tr>
    <th></th>
    <th>Gold</th>
    <th>Silver</th>
    <th>Copper</th>
</tr>
"""


def get_table_header_html(hidden_name: str = "") -> str:
    if hidden_name:
        style = 'style="cursor: pointer; color: transparent; text-shadow: 0 0 8px rgba(0,0,0,0.5);"'
        onclick = f'onclick="navigator.clipboard.writeText(\'{hidden_name}\')" title="Click to copy"'
        first_row = f"<th {style} {onclick}>{hidden_name}</th>"
    else:
        first_row = "<th></th>"
    return f"""
<tr>
    {first_row}
    <th>Gold</th>
    <th>Silver</th>
    <th>Copper</th>
</tr>
"""


def get_price_rows_html(
    price_names: list[str],
    category_name: str,
    /,
    clipboard_copy: bool = False,
) -> str:
    rows_str = ""
    for price_name in price_names:
        rows_str += get_price_row_html(
            price_name,
            category_name,
            clipboard_copy=clipboard_copy,
        )
    return rows_str


def get_table_html(
    price_names: list[str],
    category_name: str,
    hidden_name: str = "",
    clipboard_copy: bool = False,
) -> str:
    return f"""
<table>
    {get_table_header_html(hidden_name=hidden_name)}
    {get_price_rows_html(price_names, category_name, clipboard_copy=clipboard_copy)}
</table>
"""


def get_price_row_html(
    item_id: str,
    name: str,
    /,
    clipboard_copy: bool = False,
) -> str:
    words = [word.capitalize() for word in item_id.split("_")]
    row_content = " ".join(words)
    if clipboard_copy:
        first_col = f"""
    <td onclick="navigator.clipboard.writeText('{row_content}')" style="cursor: pointer;" title="Click to copy">{row_content}</td>
"""
    else:
        first_col = f"<td>{row_content}</td>"
    return f"""
<tr>
    {first_col}
    <td id="{item_id}_g##{name}">-</td>
    <td id="{item_id}_s##{name}">-</td>
    <td id="{item_id}_c##{name}">-</td>
</tr>"""


def get_flip_table_html(item_id: int) -> str:
    return f"""<table>
        {get_table_header_html()}
        <tr>
            <td>Buy Order</td>
            <td id="{item_id}_buy_g">-</td>
            <td id="{item_id}_buy_s">-</td>
            <td id="{item_id}_buy_c">-</td>
        </tr>
        <tr>
            <td>Sell Order</td>
            <td id="{item_id}_sell_g">-</td>
            <td id="{item_id}_sell_s">-</td>
            <td id="{item_id}_sell_c">-</td>
        </tr>
        <tr>
            <td>Flip Profit</td>
            <td id="{item_id}_flip_g">-</td>
            <td id="{item_id}_flip_s">-</td>
            <td id="{item_id}_flip_c">-</td>
        </tr>
    </table>"""


ECTO_TABLE = get_flip_table_html(ItemIDs.ECTOPLASM)
RARE_GEAR_TABLE = get_flip_table_html(ItemIDs.RARE_UNID_GEAR)

RARE_GEAR_NAMES = [
    "stack_buy",
    "salvage_costs",
    "mats_value_after_tax",
    "profit_stack",
]
RARE_GEAR_SALVAGE = get_table_html(
    price_names=RARE_GEAR_NAMES,
    category_name="rare_gear_salvage",
    hidden_name="Rare Gear",
)

GEAR_SALVAGE_NAMES = [
    "stack_buy",
    "salvage_costs",
    "mats_value_after_tax",
    "profit_stack",
]
GEAR_SALVAGE_TABLE = get_table_html(
    price_names=GEAR_SALVAGE_NAMES,
    category_name="gear_salvage",
    hidden_name="Unidentified Gear",
)

T5_MATS_BUY_NAMES = [
    "large_claw",
    "potent_blood",
    "large_bone",
    "intricate_totem",
    "large_fang",
    "potent_venom",
    "large_scale",
]
T5_MATS_BUY_TABLE = get_table_html(
    price_names=T5_MATS_BUY_NAMES,
    category_name="t5_mats_buy",
    clipboard_copy=True,
)

MATS_CRAFTING_COMPARE_NAMES = [
    "mithril_ore_to_ingot",
    "mithril_ingot_buy",
    "elder_wood_log_to_plank",
    "elder_wood_plank_buy",
    "lucent_mote_to_crystal",
    "lucent_crystal_buy",
]
MATS_CRAFTING_COMPARE_TABLE = get_table_html(
    price_names=MATS_CRAFTING_COMPARE_NAMES,
    category_name="mats_crafting_compare",
)

COMMON_GEAR_NAMES = [
    "stack_buy",
    "salvage_costs",
    "mats_value_after_tax",
    "profit_stack",
]
COMMON_GEAR_SALVAGE_TABLE = get_table_html(
    price_names=COMMON_GEAR_NAMES,
    category_name="common_gear_salvage",
    hidden_name="Common Gear",
)

LOADSTONE_NAMES = [
    "onyx",
    "charged",
    "corrupted",
    "destroyer",
]
LOADSTONE_TABLE = get_table_html(
    price_names=LOADSTONE_NAMES,
    category_name="loadstone_forge",
    clipboard_copy=True,
)

SCHOLAR_RUNE_NAMES = [
    "crafting_cost",
    "sell",
    "profit",
]
SCHOLAR_RUNE_TABLE = get_table_html(
    price_names=SCHOLAR_RUNE_NAMES,
    category_name="scholar_rune",
    hidden_name="Scholar Rune",
)

GUARDIAN_RUNE_NAMES = [
    "crafting_cost",
    "sell",
    "profit",
]
GUARDIAN_RUNE_TABLE = get_table_html(
    price_names=GUARDIAN_RUNE_NAMES,
    category_name="guardian_rune",
    hidden_name="Guardian Rune",
)

DRAGONHUNTER_RUNE_NAMES = [
    "crafting_cost",
    "sell",
    "profit",
]
DRAGONHUNTER_RUNE_TABLE = get_table_html(
    price_names=DRAGONHUNTER_RUNE_NAMES,
    category_name="dragonhunter_rune",
    hidden_name="Dragonhunter Rune",
)

FIREWORKS_NAMES = [
    "crafting_cost",
    "sell",
    "flip",
    "profit",
]
FIREWORKS_TABLE = get_table_html(
    price_names=FIREWORKS_NAMES,
    category_name="relic_of_fireworks",
    hidden_name="Relic of Fireworks",
)

THIEF_NAMES = [
    "crafting_cost",
    "sell",
    "flip",
    "profit",
]
THIEF_TABLE = get_table_html(
    price_names=FIREWORKS_NAMES,
    category_name="relic_of_thief",
    hidden_name="Relic of Thief",
)

ARISTOCRACY_NAMES = [
    "crafting_cost",
    "sell",
    "flip",
    "profit",
]
ARISTOCRACY_TABLE = get_table_html(
    price_names=ARISTOCRACY_NAMES,
    category_name="relic_of_aristocracy",
    hidden_name="Relic of Aristocracy",
)

THESIS_NAMES = [
    "crafting_cost",
    "sell",
    "flip",
    "profit",
]
THESIS_TABLE = get_table_html(
    price_names=THESIS_NAMES,
    category_name="thesis_on_masterful_malice",
    hidden_name="Thesis on Masterful Malice",
)

RARE_WEAPON_CRAFT_NAMES = [
    "crafting_cost",
    "ecto_sell_after_tax",
    "profit",
]
RARE_WEAPON_CRAFT_TABLE = get_table_html(
    price_names=RARE_WEAPON_CRAFT_NAMES,
    category_name="rare_weapon_craft",
)

FORGE_ENH_NAMES = [
    "cost",
    "profit_per_try",
    "profit_per_shard",
]
FORGE_ENH_TABLE = get_table_html(
    price_names=FORGE_ENH_NAMES,
    category_name="symbol_enh_forge",
    hidden_name="Symbol of Enhancement",
)

CHARM_BRILLIANCE_FORGE_NAMES = [
    "cost",
    "profit_per_try",
    "profit_per_shard",
]
CHARM_BRILLIANCE_FORGE_TABLE = get_table_html(
    price_names=CHARM_BRILLIANCE_FORGE_NAMES,
    category_name="charm_brilliance_forge",
    hidden_name="Charm of Brilliance",
)

with (FILE_DIR / "static" / "style.css").open() as f:
    CSS_CONTENT = f.read()
STYLE = f"<style>{CSS_CONTENT}</style>"


PROFIT_CALCULATION_HTML = """
<h3 style="text-align: center;">Profit Calculator</h3>
<div style="display: flex; justify-content: center; align-items: flex-end; gap: 16px; margin-bottom: 24px;">
    <div style="display: flex; flex-direction: column; align-items: center;">
        <label for="manual-buy-g">Buy Price:</label>
        <div style="display: flex; gap: 4px;">
            <input id="manual-buy-g" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="G" style="width: 40px;">
            <input id="manual-buy-s" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="S" style="width: 40px;">
            <input id="manual-buy-c" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="C" style="width: 40px;">
        </div>
    </div>
    <div style="display: flex; flex-direction: column; align-items: center;">
        <label for="manual-sell-g">Sell Price:</label>
        <div style="display: flex; gap: 4px;">
            <input id="manual-sell-g" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="G" style="width: 40px;">
            <input id="manual-sell-s" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="S" style="width: 40px;">
            <input id="manual-sell-c" type="text" inputmode="numeric" pattern="[0-9]*" placeholder="C" style="width: 40px;">
        </div>
    </div>
    <div style="align-self: flex-end;">
        <button onclick="calculateManualProfit()">Calculate</button>
    </div>
</div>
<div style="text-align: center; margin-bottom: 24px;">
    <span id="manual-profit-result" style="font-size: 18px;">Profit: 0g 0s 0c</span>
</div>
"""


def get_fetch_price_html(item_id: int) -> str:
    api_endpoint = f"price?item_id={item_id}"
    return f"""
const response = await fetch('{api_base}{api_endpoint}');
const data = await response.json();
if (data.error) {{
    alert(data.error);
    return;
}}

document.getElementById('{item_id}_buy_g').innerText = data.buy_g;
document.getElementById('{item_id}_buy_s').innerText = data.buy_s;
document.getElementById('{item_id}_buy_c').innerText = data.buy_c;

document.getElementById('{item_id}_sell_g').innerText = data.sell_g;
document.getElementById('{item_id}_sell_s').innerText = data.sell_s;
document.getElementById('{item_id}_sell_c').innerText = data.sell_c;

document.getElementById('{item_id}_flip_g').innerText = data.flip_g;
document.getElementById('{item_id}_flip_s').innerText = data.flip_s;
document.getElementById('{item_id}_flip_c').innerText = data.flip_c;
"""


def get_all_fetch_price_html(
    api_endpoint: str,
) -> str:
    return f"""
try {{
    const response = await fetch('{api_base}{api_endpoint}');
    const data = await response.json();

    for (const [key, value] of Object.entries(data)) {{
        document.getElementById(key + '##' + `{api_endpoint}`).innerText = value;
    }}
}} catch (error) {{
    console.error('Error fetching prices:', error);
}}
"""


with (FILE_DIR / "static" / "scripts.js").open() as f:
    SCRIPT_FUNCTIONS = f.read()

FETCH_PRICES = f"""
async function _fetchPrices() {{
    await Promise.all([
        (async () => {{ {get_fetch_price_html(ItemIDs.RARE_UNID_GEAR)} }})(),
        (async () => {{ {get_fetch_price_html(ItemIDs.ECTOPLASM)} }})(),
        (async () => {{ {get_all_fetch_price_html("rare_gear_salvage")} }})(),
        (async () => {{ {get_all_fetch_price_html("gear_salvage")} }})(),
        (async () => {{ {get_all_fetch_price_html("guardian_rune")} }})(),
        (async () => {{ {get_all_fetch_price_html("scholar_rune")} }})(),
        (async () => {{ {get_all_fetch_price_html("dragonhunter_rune")} }})(),
        (async () => {{ {get_all_fetch_price_html("relic_of_fireworks")} }})(),
        (async () => {{ {get_all_fetch_price_html("relic_of_thief")} }})(),
        (async () => {{ {get_all_fetch_price_html("relic_of_aristocracy")} }})(),
        (async () => {{ {get_all_fetch_price_html("rare_weapon_craft")} }})(),
        (async () => {{ {get_all_fetch_price_html("t5_mats_buy")} }})(),
        (async () => {{ {get_all_fetch_price_html("mats_crafting_compare")} }})(),
        (async () => {{ {get_all_fetch_price_html("common_gear_salvage")} }})(),
        (async () => {{ {get_all_fetch_price_html("symbol_enh_forge")} }})(),
        (async () => {{ {get_all_fetch_price_html("charm_brilliance_forge")} }})(),
        (async () => {{ {get_all_fetch_price_html("loadstone_forge")} }})(),
        (async () => {{ {get_all_fetch_price_html("thesis_on_masterful_malice")} }})(),
    ]);
}}
"""

SCRIPT = f"""
<script>
    {FETCH_PRICES}
    {SCRIPT_FUNCTIONS}
    window.addEventListener('DOMContentLoaded', () => {{
        fetchPrices();
        updateLastUpdated();
    }});
</script>
"""

FAVICON_URL = FILE_DIR / "favicon.ico"
HTML_PAGE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GW2 TP King</title>
    <link rel="icon" href="{FAVICON_URL}" type="image/x-icon">
    {STYLE}
    {SCRIPT}
</head>
<body>
    <div id="fetch-popup">Prices updated!</div>
    <h1 style="text-align: center;">
            Guild Wars 2 TP King
    </h1>
    <div style="display: flex; justify-content: center;">
        <button onclick="fetchPrices()" style="margin-bottom: 20px;">Refresh Prices</button>
    </div>
    <div style="font-size: 0.8em; color: #666; text-align: center; margin-bottom: 8px;">
        Last updated: <span id="last-updated">Loading...</span>
    </div>
    <div style="display: flex; justify-content: center; align-items: flex-start; gap: 40px; margin: 0 auto; max-width: 1400px;">
        <div style="flex: 1;">
            {PROFIT_CALCULATION_HTML}

            <h3 style="text-align: center;">Rare Unid. Gear</h3>
            {RARE_GEAR_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Piece_of_Rare_Unidentified_Gear/Salvage_Rate" target="_blank" style="color: inherit; text-decoration: none;">
                    Rare Gear Ident & Salvaging
                </a>
            </h3>
            {RARE_GEAR_SALVAGE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Piece_of_Unidentified_Gear/Salvage_Rate" target="_blank" style="color: inherit; text-decoration: none;">
                    Green Gear Ident & Salvaging
                </a>
            </h3>
            {GEAR_SALVAGE_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Piece_of_Common_Unidentified_Gear/Salvage_Rate" target="_blank" style="color: inherit; text-decoration: none;">
                    Common Gear Ident & Salvaging
                </a>
            </h3>
            {COMMON_GEAR_SALVAGE_TABLE}

            <h3 style="text-align: center;">
                <a href="https://fast.farming-community.eu/conversions/spirit-shard" target="_blank" style="color: inherit; text-decoration: none;">
                    Forge Loadstones Profit
                </a>
            </h3>
            {LOADSTONE_TABLE}

            <h3 style="text-align: center;">
                <a href="https://fast.farming-community.eu/conversions/spirit-shard/charm-of-brilliance" target="_blank" style="color: inherit; text-decoration: none;">
                    Forge Charm of Brilliance
                </a>
            </h3>
            {CHARM_BRILLIANCE_FORGE_TABLE}
        </div>
        <div style="flex: 1;">
            <h3 style="text-align: center;">Ectoplasm</h3>
            {ECTO_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Krait_Shell" target="_blank" style="color: inherit; text-decoration: none;">
                    Rare Weapon Craft
                </a>
            </h3>
            {RARE_WEAPON_CRAFT_TABLE}

            <h3 style="text-align: center;">Mats Crafting Compare</h3>
            {MATS_CRAFTING_COMPARE_TABLE}

            <h3 style="text-align: center;">T5 Mats Buy Order</h3>
            {T5_MATS_BUY_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Thesis_on_Masterful_Malice" target="_blank" style="color: inherit; text-decoration: none;">
                    Thesis on Masterful Malice
                </a>
            </h3>
            {THESIS_TABLE}

            <h3 style="text-align: center;">
                <a href="https://fast.farming-community.eu/conversions/spirit-shard/symbol-of-enhancement" target="_blank" style="color: inherit; text-decoration: none;">
                    Forge Symbol of Enhancement
                </a>
            </h3>
            {FORGE_ENH_TABLE}
        </div>
        <div style="flex: 1;">
            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Superior_Rune_of_the_Scholar" target="_blank" style="color: inherit; text-decoration: none;">
                    Scholar Runes
                </a>
                <button onclick="window.open('scholar_rune_history', '_blank')" style="margin-left:8px;" title="History">&#128279;</button>
            </h3>
            {SCHOLAR_RUNE_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Superior_Rune_of_the_Guardian" target="_blank" style="color: inherit; text-decoration: none;">
                    Guardian Runes
                </a>
                <button onclick="window.open('guardian_rune_history', '_blank')" style="margin-left:8px;" title="History">&#128279;</button>
            </h3>
            {GUARDIAN_RUNE_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Superior_Rune_of_the_Dragonhunter" target="_blank" style="color: inherit; text-decoration: none;">
                    Dragonhunter Runes
                </a>
                <button onclick="window.open('dragonhunter_rune_history', '_blank')" style="margin-left:8px;" title="History">&#128279;</button>
            </h3>
            {DRAGONHUNTER_RUNE_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Relic_of_Fireworks" target="_blank" style="color: inherit; text-decoration: none;">
                    Fireworks Relic
                </a>
                <button onclick="window.open('relic_of_fireworks_history', '_blank')" style="margin-left:8px;" title="History">&#128279;</button>
            </h3>
            {FIREWORKS_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Relic_of_the_Thief" target="_blank" style="color: inherit; text-decoration: none;">
                    Thief Relic
                </a>
                <button onclick="window.open('relic_of_thief_history', '_blank')" style="margin-left:8px;" title="History">&#128279;</button>
            </h3>
            {THIEF_TABLE}

            <h3 style="text-align: center;">
                <a href="https://wiki.guildwars2.com/wiki/Relic_of_the_Aristocracy" target="_blank" style="color: inherit; text-decoration: none;">
                    Aristocracy Relic
                </a>
                <button onclick="window.open('relic_of_aristocracy_history', '_blank')" style="margin-left:8px;" title="History">&#128279;</button>
            </h3>
            {ARISTOCRACY_TABLE}
        </div>
    </div>
</body>
</html>
"""

if not uses_server:
    index = FILE_DIR / "static" / "index.html"
    with index.open("w", encoding="utf-8") as f:
        f.write(HTML_PAGE)
