from enum import Enum


# ---------- Unit of Measure ----------
class UnitOfMeasure(str, Enum):
    """
    This class identificates
    Base unit of measure for product
    """

    __slots__ = ()

    PIECE = 'pc'
    KILOGRAM = 'kg'
    GRAM = 'g'
    LITER = 'l'
    MILLILITER = 'ml'
    METER = 'm'
    CENTIMETER = 'cm'
    SQUARE_METER = 'm2'
    CUBIC_METER = 'm3'
    BOX = 'box'
    PALLET = 'pal'
    SET = 'set'


# ---------- Products Physical State Types ---------
class ProductPhysicalState(str, Enum):
    """
    This class identificates main state
    Product Physical State Type
    """

    __slots__ = ()

    SOLID = 'solid'
    BULK = 'bulk'
    LIQUID = 'liquid'
    GAS = 'gas'


# ---------- Products Storage Condition ---------
class ProductStorageCondition(str, Enum):
    """
    This class identificates
    Product Storage Condition
    """

    __slots__ = ()

    PERISHABLE = 'perishable'
    HAZARDOUS = 'hazardous'
    ELECTRONICS = 'electronics'
    MEDICINE = 'medicine'
    # Additional
    TEMPERATURE_CONTROLLED = 'temperature_controlled'
    VENTILATED = 'ventilated'
    ODOR_SENSITIVE = 'odor_sensitive'
    FOOD_SAFE = 'food_safe'


# ---------- Products Size Type ---------
class ProductSizeType(str, Enum):
    """
    This class identificates
    Product Size Type
    """

    __slots__ = ()

    OVERSIZED = 'oversized'
    HEAVY = 'heavy'
    MEDIUM = 'medium'
    SMALL_PARTS = 'small parts'
    # Additional
    BULKY = 'bulky'  # Need more space but not too heavy
    LIGHT = 'light'
    STANDARD = 'standard'


# ---------- Products Moving Type ---------
class ProductMovingType(str, Enum):
    """
    This class identificates
    Product Moving Type
    """

    __slots__ = ()

    FAST_MOVING = 'fast moving'
    NORMAL_MOVING = 'normal moving'
    SLOW_MOVING = 'slow moving'
    HIGH_VALUE = 'high value'
    # Additional
    SEASONAL = 'seasonal'
    PROMOTIONAL = 'promotional'


# ---------- Products Tracking Type ---------
class ProductTrackingType(str, Enum):
    """
    This class identificates
    Product Tracking Type
    """

    __slots__ = ()

    PIECE = 'piece'
    WEIGHT_BASED = 'weight_based'
    KIT = 'kit'
    # Additional
    SERIALIZED = 'serialized'  # track by serialized
    LOT_TRACKED = 'lot_tracked'  # track by lot
    EXPIRY_TRACKED = 'expiry_tracked'  # track expiry date


# ---------- Products Role in Production Type ---------
class ProductRoleType(str, Enum):
    """
    This class identificates
    Product Role in Production Type
    """

    __slots__ = ()

    RAW_MATERIAL = 'raw material'
    COMPONENTS = 'components'
    FINISHED_GOOD = 'finished good'
    RETURNS = 'returns'
    # Additional
    WORK_IN_PROGRESS = 'work in progress'
    PACKAGING = 'packaging'
    CONSUMABLE = 'consumable'
    TOOL = 'tool'
    SPARE_PART = 'spare part'
    SCRAP = 'scrap'
    SAMPLE = 'sample'


# ---------- Hazardous Class (if hazardous) ----------
class HazardClass(str, Enum):
    """
    This class identificates
    Hazard class according to international standards (e.g., ADR)
    """

    __slots__ = ()

    CLASS_1 = '1'  # Explosive
    CLASS_2 = '2'  # Gas
    CLASS_3 = '3'  # Flammable liquid
    CLASS_4 = '4'  # Flammable solid
    CLASS_5 = '5'  # Oxidizing
    CLASS_6 = '6'  # Toxic
    CLASS_7 = '7'  # Radioactive
    CLASS_8 = '8'  # Corrosive
    CLASS_9 = '9'  # Miscellaneous


# ---------- Temperature Regime ----------
class TemperatureRegime(str, Enum):
    """
    This class identificates
    Required temperature regime for storage
    """

    __slots__ = ()

    FROZEN = 'frozen'  # -18°C and below
    DEEP_FROZEN = 'deep_frozen'  # -30°C and below
    CHILLED = 'chilled'  # 0°C to +5°C
    COOL = 'cool'  # +10°C to +15°C
    AMBIENT = 'ambient'  # room temperature
    WARM = 'warm'  # +20°C to +25°C
    CONTROLLED = 'controlled'  # specific range defined separately


# ---------- ABC Classification (for inventory optimization) ----------
class ABCCategory(str, Enum):
    """
    This class identificates
    ABC analysis category based on value and turnover
    """

    __slots__ = ()

    A = 'A'  # high value, fast moving
    B = 'B'  # medium value/medium moving
    C = 'C'  # low value, slow moving
    D = 'D'  # obsolete, very slow


# ---------- Packaging Type ----------
class PackagingType(str, Enum):
    """
    This class identificates
    Type of packaging used for storage/shipping
    """

    __slots__ = ()

    BAG = 'bag'
    BOX = 'box'
    CRATE = 'crate'
    DRUM = 'drum'
    PALLET = 'pallet'
    IBC = 'ibc'  # intermediate bulk container
    TOTE = 'tote'
    CYLINDER = 'cylinder'
    CARDBOARD = 'cardboard'
    SHRINK_WRAP = 'shrink_wrap'
    NONE = 'none'  # unpackaged / loose


# ---------- Product Status (Lifecycle) ----------
class ProductStatus(str, Enum):
    """
    This class identificates
    Current lifecycle status of the product
    """

    __slots__ = ()

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DISCONTINUED = 'discontinued'
    COMING_SOON = 'coming_soon'
    PENDING_APPROVAL = 'pending_approval'
    UNDER_REVIEW = 'under_review'
    RETURNED = 'returned'
    DAMAGED = 'damaged'
    QUARANTINED = 'quarantined'
