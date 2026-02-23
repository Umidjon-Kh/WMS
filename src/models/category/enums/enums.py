from enum import Enum


class PutawayStrategy(str, Enum):
    FIFO = 'fifo'  # First In First Out
    FEFO = 'fefo'  # First Expired First Out
    LIFO = 'lifo'  # Last In First Out
    FIXED = 'fixed'  # Fixed location
    BULK = 'bulk'  # Bulk storage (anywhere)
    DYNAMIC = 'dynamic'  # Dynamic allocation


class ReplenishmentMethod(str, Enum):
    PALLET = 'pallet'  # Whole pallet
    CASE = 'case'  # Case / box
    EACH = 'each'  # Each piece
    BULK = 'bulk'  # Bulk (e.g., by weight)


class CycleCountFrequency(str, Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'
    CUSTOM = 'custom'  # custom days
