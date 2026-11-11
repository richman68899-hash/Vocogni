"""Stable enums shared by Streak Garden rules, models, and UI."""
from enum import Enum, IntEnum


class GrowthStage(IntEnum):
    SEEDLING = 1
    SAPLING = 2
    MATURE = 3


class TreeStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"


class WalletReason(str, Enum):
    DAILY_WATER = "daily_water"
    TREE_PLANTED = "tree_planted"
    TREE_GROWTH = "tree_growth"
    TREE_SALE = "tree_sale"
