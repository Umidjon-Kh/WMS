import pytest
from datetime import date, timedelta
from src.models import (
    BaseProduct,
    # Dimensions,
    # HandlingAttributes,
    # StorageRequirements,
    # Classification,
    Traceability,
    UnitOfMeasure,
    ProductPhysicalState,
    ProductRoleType,
    ProductStatus,
    ProductTrackingType,
    ProductStorageCondition,
    ProductSizeType,
    ProductMovingType,
    ABCCategory,
    PackagingType,
    TemperatureRegime,
    HazardClass,
)
from src.models.product.constants import (
    HEAVY_MIN_KG,
    LIGHT_MAX_KG,
    OVERSIZED_MIN_CM,
    SMALL_PARTS_MAX_CM,
)
