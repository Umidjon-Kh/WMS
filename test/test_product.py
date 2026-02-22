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
    # ProductStorageCondition,
    # ProductSizeType,
    # ProductMovingType,
    # ABCCategory,
    # PackagingType,
    # TemperatureRegime,
    # HazardClass,
)


# ----------------------------------------------------------------------
# Helper function to create a minimal valid product
# ----------------------------------------------------------------------
def minimal_product(**kwargs):
    defaults = {
        'sku': 'TEST001',
        'name': 'Test Product',
        'unit_of_measure': UnitOfMeasure.PIECE,
        'physical_state': ProductPhysicalState.SOLID,
        'role_type': ProductRoleType.FINISHED_GOOD,
        'status': ProductStatus.ACTIVE,
        'traceability': Traceability(tracking_type=ProductTrackingType.PIECE),
    }
    defaults.update(kwargs)
    return BaseProduct(**defaults)


# ----------------------------------------------------------------------
# Testing minimal product creation
# ----------------------------------------------------------------------
def test_creation_min():
    product = minimal_product()
    assert product.sku == 'TEST001'


# ----------------------------------------------------------------------
# Testing Dimensions Volume calculation
# ----------------------------------------------------------------------
def test_dimensions_volume_calculation():
    product = minimal_product(
        dimensions={
            'width_cm': 100,
            'height_cm': 200,
            'depth_cm': 50,
        }
    )
    expected_volume = (100 * 200 * 50) / 1_000_000  # 1.0
    assert product.dimensions.volume_m3 == expected_volume


# ----------------------------------------------------------------------
# Testing Handling Fragile Product not get with stackable True
# ----------------------------------------------------------------------
def test_handling_fragile_not_stackable():
    with pytest.raises(ValueError, match='Fragile product can\'t be stackable'):
        minimal_product(handling={'is_fragile': True, 'is_stackable': True})


# ----------------------------------------------------------------------
# Testing Traceability expiry date not in the past
# ----------------------------------------------------------------------
def test_traceability_expiry_not_past():
    past_date = date.today() - timedelta(days=1)
    with pytest.raises(ValueError, match='expiry_date cannot be in the past'):
        minimal_product(
            traceability={
                'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
                'production_date': date.today() - timedelta(days=10),
                'expiry_date': past_date,
            }
        )


# ----------------------------------------------------------------------
# Testing Traceability prodution date not in the future
# ----------------------------------------------------------------------
def test_traceability_production_not_future():
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValueError, match="production_date cannot be in the future"):  # подставь точный текст ошибки
        minimal_product(
            traceability={
                "tracking_type": ProductTrackingType.EXPIRY_TRACKED,
                "production_date": future_date,
                "expiry_date": date.today() + timedelta(days=10),
            }
        )
