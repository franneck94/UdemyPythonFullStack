from typing import Final


class ItemIDs:
    # Gear
    RARE_UNID_GEAR: int = 83008
    COMMON_UNID_GEAR: int = 85016
    UNID_GEAR: int = 84731
    COMMON_GEAR: int = 85016
    # T6 Mats
    THICK_LEATHER: int = 19729
    GOSSAMER_SCRAP: int = 19745
    GOSSAMER_THREAD: int = 19790
    SILK_SCRAP: int = 19748
    HARDENED_LEATHER: int = 19732
    ANCIENT_WOOD_LOG: int = 19725
    CURED_HARDENED_LEATHER_SQUARE: int = 19737
    ORICHALCUM_ORE: int = 19701
    ECTOPLASM: int = 19721
    ELABORATE_TOTEM: int = 24300
    CRYSTALINE_DUST: int = 24277
    # T5 Mats
    MITHRIL_INGOT: int = 19684
    MITHRIL_ORE: int = 19700
    ELDER_WOOD_PLANK: int = 19709
    ELDER_WOOD_LOG: int = 19722
    MIRTHIL: int = 19700
    ELDER_WOOD: int = 19722
    LARGE_CLAW: int = 24350
    POTENT_BLOOD: int = 24294
    LARGE_BONE: int = 24341
    INTRICATE_TOTEM: int = 24299
    LARGE_FANG: int = 24356
    POTENT_VENOM_SAC: int = 24282
    LARGE_SCALE: int = 24288
    # Other
    PILE_OF_LUCENT_CRYSTAL: int = 89271
    BARBED_THORN: int = 74202
    LUCENT_MOTE: int = 89140
    # Runes
    SCHOLAR_RUNE: int = 24836
    GUARD_RUNE: int = 24824
    DRAGONHUNTER_RUNE: int = 74978
    # Relics
    RELIC_OF_FIREWORKS: int = 100947
    RELIC_OF_ARISTOCRACY: int = 100849
    RELIC_OF_THIEF: int = 100916
    # Charms
    SYMBOL_OF_ENH: int = 89141
    SYMBOL_OF_PAIN: int = 89182
    SYMBOL_OF_CONTROL: int = 89098
    CHARM_OF_BRILLIANCE: int = 89103
    CHARM_OF_POTENCE: int = 89258
    CHARM_OF_SKILL: int = 89216
    # Loadstones
    EVERGREEN_LOADSTONE: int = 68942
    CHARGED_LOADSTONE: int = 24305
    CORRUPTED_LOADSTONE: int = 24340
    DESTROYER_LOADSTONE: int = 24325
    ONYX_LOADSTONE: int = 24310
    # Cores
    ONYX_CORE: int = 24309
    DESTROYER_CORE: int = 24324
    CORRUPTED_CORE: int = 24339
    CHARGED_CORE: int = 24304
    # Other
    WRIT_MASTERFUL_MALICE: int = 72510
    THESIS_MASTERFUL_MALICE: int = 76738
    POUCH_OF_BLACK_PIGMENTS: int = 70426
    POUCH_OF_WHITE_PIGMENTS: int = 75862
    JUG_OF_WATER: int = 12156


class Kits:
    COPPER_FED: float = 3.0
    RUNECRAFTER: float = 30.0
    SILVER_FED: float = 60.0


TAX_RATE: float = 0.85


class API:
    GW2_COMMERCE_API_URL: str = "https://api.guildwars2.com/v2/commerce/prices"
    PRODUCTION_API_URL: str = "https://gw2tp-production.up.railway.app/api/"
    DEV_API_URL: str = "http://localhost:8000/api/"
    COMMAND_PREFIX: str = "/gw2tp"
    COMMANDS_LIST: Final[set[str]] = {
        # runes
        "scholar_rune",
        "dragonhunter_rune",
        "guardian_rune",
        # relics
        "relic_of_fireworks",
        "relic_of_aristocracy",
        "relic_of_thief",
        # rare / ecto
        "rare_weapon_craft",
        "rare_gear_salvage",
        "ecto",
        # gear
        "gear_salvage",
        "common_gear_salvage",
        # t5
        "t5_mats_buy",
        "mats_crafting_compare",
        # general
        "profits",
        "get_price",
        "thesis_on_masterful_malice",
        # forge
        "symbol_enh_forge",
        "charm_brilliance_forge",
        "loadstone_forge",
    }
    CRAFTS: Final[set[str]] = {
        "dragonhunter_rune",
        "guardian_rune",
        "scholar_rune",
        "relic_of_fireworks",
        "relic_of_thief",
        "relic_of_aristocracy",
        "rare_weapon_craft",
    }
