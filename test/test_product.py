import pytest
from datetime import date, timedelta
from src.models import (
    BaseProduct,
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
# 1. Basic creation
# ----------------------------------------------------------------------
def test_minimal_product_creation():
    product = minimal_product()
    assert product.sku == 'TEST001'
    assert product.name == 'Test Product'


# ----------------------------------------------------------------------
# 2. Dimensions composition
# ----------------------------------------------------------------------
def test_dimensions_volume_calculation():
    product = minimal_product(
        dimensions={
            'width_cm': 100,
            'height_cm': 200,
            'depth_cm': 50,
        }
    )
    expected_volume = (100 * 200 * 50) / 1_000_000
    assert product.dimensions.volume_m3 == expected_volume


def test_dimensions_no_volume_without_all_dims():
    product = minimal_product(
        dimensions={
            'width_cm': 100,
            'height_cm': 200,
            # depth missing
        }
    )
    assert product.dimensions.volume_m3 is None


def test_dimensions_explicit_volume_overrides_auto():
    product = minimal_product(
        dimensions={
            'width_cm': 100,
            'height_cm': 200,
            'depth_cm': 50,
            'volume_m3': 999.0,
        }
    )
    assert product.dimensions.volume_m3 == 999.0


# ----------------------------------------------------------------------
# 3. HandlingAttributes composition
# ----------------------------------------------------------------------
def test_handling_fragile_not_stackable():
    with pytest.raises(ValueError, match='Fragile product can\'t be stackable'):
        minimal_product(handling={'is_fragile': True, 'is_stackable': True})


def test_handling_odor_recommendation(capsys):
    product = minimal_product(handling={'is_odor_sensitive': True, 'requires_ventilation': False})
    captured = capsys.readouterr()
    assert 'Recomendation: For Odor sensitive products recommends ventailation True' in captured.out
    assert product


# ----------------------------------------------------------------------
# 4. Traceability composition
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


def test_traceability_production_not_future():
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValueError, match='production_date cannot be in the future'):
        minimal_product(
            traceability={
                'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
                'production_date': future_date,
                'expiry_date': date.today() + timedelta(days=10),
            }
        )


def test_traceability_expiry_tracking_requires_dates():
    # Missing production_date
    with pytest.raises(ValueError, match='production_date required for expiry tracked products'):
        minimal_product(
            traceability={
                'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
                'expiry_date': date.today() + timedelta(days=10),
            }
        )
    # Missing expiry_date
    with pytest.raises(ValueError, match='expiry_date required for expiry tracked products'):
        minimal_product(
            traceability={
                'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
                'production_date': date.today() - timedelta(days=10),
            }
        )


# ----------------------------------------------------------------------
# 5. StorageRequirements composition
# ----------------------------------------------------------------------
def test_storage_hazardous_requires_hazard_class():
    with pytest.raises(ValueError, match='hazard_class required for hazardous products'):
        minimal_product(storage_requirements={'storage_condition': ProductStorageCondition.HAZARDOUS})


def test_storage_hazard_class_only_with_hazardous():
    with pytest.raises(ValueError, match='hazard_class only allowed for hazardous products'):
        minimal_product(
            storage_requirements={
                'storage_condition': ProductStorageCondition.PERISHABLE,
                'hazard_class': HazardClass.CLASS_3,
            }
        )


def test_storage_perishable_requires_temperature():
    with pytest.raises(
        ValueError, match='temperature_regime required for perishable or temperature-controlled products'
    ):
        minimal_product(
            storage_requirements={'storage_condition': ProductStorageCondition.PERISHABLE},
            traceability={
                'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
                'production_date': date.today() - timedelta(days=5),
                'expiry_date': date.today() + timedelta(days=10),
            },
        )


def test_storage_medicine_requires_temperature():
    with pytest.raises(
        ValueError, match='temperature_regime required for perishable or temperature-controlled products'
    ):
        minimal_product(
            storage_requirements={'storage_condition': ProductStorageCondition.MEDICINE},
            traceability={
                'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
                'production_date': date.today() - timedelta(days=10),
                'expiry_date': date.today() + timedelta(days=20),
            },
        )


def test_storage_temperature_controlled_requires_temperature():
    with pytest.raises(
        ValueError, match='temperature_regime required for perishable or temperature-controlled products'
    ):
        minimal_product(
            storage_requirements={'storage_condition': ProductStorageCondition.TEMPERATURE_CONTROLLED},
            traceability={
                'tracking_type': ProductTrackingType.PIECE,
            },
        )


def test_storage_electronics_temperature_recommendation(capsys):
    product = minimal_product(
        storage_requirements={'storage_condition': ProductStorageCondition.ELECTRONICS},
        handling={'is_static_sensitive': True},
    )
    captured = capsys.readouterr()
    assert 'Recommendation: For product type Electronics recommendts temperature_regime' in captured.out
    assert product


# ----------------------------------------------------------------------
# 6. Classification composition
# ----------------------------------------------------------------------
def test_classification_heavy_not_fast_moving():
    with pytest.raises(ValueError, match='For Products with size_type Heavy and Over_sized moving_type cant be fast'):
        minimal_product(
            classification={
                'size_type': ProductSizeType.HEAVY,
                'moving_type': ProductMovingType.FAST_MOVING,
            }
        )


def test_classification_oversized_not_fast_moving():
    with pytest.raises(ValueError, match='For Products with size_type Heavy and Over_sized moving_type cant be fast'):
        minimal_product(
            classification={
                'size_type': ProductSizeType.OVERSIZED,
                'moving_type': ProductMovingType.FAST_MOVING,
            }
        )


def test_classification_abc_a_requires_fast_or_normal():
    with pytest.raises(
        ValueError, match='Products with ABC category A must have moving_type FAST_MOVING or NORMAL_MOVING'
    ):
        minimal_product(
            classification={
                'abc_category': ABCCategory.A,
                'moving_type': ProductMovingType.SLOW_MOVING,
            }
        )


# ----------------------------------------------------------------------
# 7. Cross‑validators in BaseProduct
# ----------------------------------------------------------------------
def test_perishable_and_medicine_require_expiry_tracking():
    for cond in (ProductStorageCondition.PERISHABLE, ProductStorageCondition.MEDICINE):
        with pytest.raises(
            ValueError, match='Perishable and Medicine products must have tracking_type = EXPIRY_TRACKED'
        ):
            minimal_product(
                storage_requirements={'storage_condition': cond, 'temperature_regime': TemperatureRegime.COOL},
                traceability={'tracking_type': ProductTrackingType.PIECE},
            )


def test_electronics_requires_static_sensitive():
    with pytest.raises(ValueError, match='Electronis products must be static sensitive'):
        minimal_product(
            storage_requirements={'storage_condition': ProductStorageCondition.ELECTRONICS},
            handling={'is_static_sensitive': False},
        )


def test_units_weight_based():
    # Valid case
    product = minimal_product(
        unit_of_measure=UnitOfMeasure.KILOGRAM,
        traceability={'tracking_type': ProductTrackingType.WEIGHT_BASED},
    )
    assert product.unit_of_measure == UnitOfMeasure.KILOGRAM

    # Invalid case
    with pytest.raises(
        ValueError,
        match='Weight-based tracking requires unit_of_measure in',
    ):
        minimal_product(
            unit_of_measure=UnitOfMeasure.PIECE,
            traceability={'tracking_type': ProductTrackingType.WEIGHT_BASED},
        )


def test_units_piece():
    # Valid case
    product = minimal_product(
        unit_of_measure=UnitOfMeasure.BOX,
        traceability={'tracking_type': ProductTrackingType.PIECE},
    )
    assert product.unit_of_measure == UnitOfMeasure.BOX

    # Invalid case
    with pytest.raises(ValueError, match='Piece tracking requires unit_of_measure in'):
        minimal_product(
            unit_of_measure=UnitOfMeasure.KILOGRAM,
            traceability={'tracking_type': ProductTrackingType.PIECE},
        )


def test_units_kit():
    # Valid cases
    for unit in (UnitOfMeasure.SET, UnitOfMeasure.PIECE):
        product = minimal_product(
            unit_of_measure=unit,
            traceability={'tracking_type': ProductTrackingType.KIT},
        )
        assert product.unit_of_measure == unit

    # Invalid case
    with pytest.raises(ValueError, match='Kit tracking requires unit_of_measure in'):
        minimal_product(
            unit_of_measure=UnitOfMeasure.BOX,
            traceability={'tracking_type': ProductTrackingType.KIT},
        )


def test_units_liquid():
    # Valid
    product = minimal_product(
        physical_state=ProductPhysicalState.LIQUID,
        unit_of_measure=UnitOfMeasure.LITER,
        storage_requirements={'packaging_type': PackagingType.DRUM},
        traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
    )
    assert product.unit_of_measure == UnitOfMeasure.LITER

    # Invalid unit
    with pytest.raises(ValueError, match='For liquid products, unit_of_measure must be LITER or MILLILITER'):
        minimal_product(
            physical_state=ProductPhysicalState.LIQUID,
            unit_of_measure=UnitOfMeasure.KILOGRAM,
            traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
        )

    # Invalid packaging
    with pytest.raises(ValueError, match='Liquid products cannot be stored in boxes'):
        minimal_product(
            physical_state=ProductPhysicalState.LIQUID,
            unit_of_measure=UnitOfMeasure.LITER,
            storage_requirements={'packaging_type': PackagingType.BOX},
            traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
        )


def test_units_gas():
    # Valid
    product = minimal_product(
        physical_state=ProductPhysicalState.GAS,
        unit_of_measure=UnitOfMeasure.CUBIC_METER,
        storage_requirements={'packaging_type': PackagingType.CYLINDER},
        handling={'requires_ventilation': True},
        traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
    )
    assert product.unit_of_measure == UnitOfMeasure.CUBIC_METER

    # Invalid unit
    with pytest.raises(ValueError, match='For gas products, unit_of_measure must be LITER, MILLILITER, or CUBIC_METER'):
        minimal_product(
            physical_state=ProductPhysicalState.GAS,
            unit_of_measure=UnitOfMeasure.KILOGRAM,
            traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
        )

    # Invalid packaging
    with pytest.raises(ValueError, match='For gas products, packaging_type must be CYLINDER or DRUM'):
        minimal_product(
            physical_state=ProductPhysicalState.GAS,
            unit_of_measure=UnitOfMeasure.LITER,
            storage_requirements={'packaging_type': PackagingType.BOX},
            handling={'requires_ventilation': True},
            traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
        )

    # Missing ventilation
    with pytest.raises(ValueError, match='Gas products must have requires_ventilation = True'):
        minimal_product(
            physical_state=ProductPhysicalState.GAS,
            unit_of_measure=UnitOfMeasure.LITER,
            storage_requirements={'packaging_type': PackagingType.CYLINDER},
            handling={'requires_ventilation': False},
            traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
        )


def test_units_bulk():
    # Valid weight
    product = minimal_product(
        physical_state=ProductPhysicalState.BULK,
        unit_of_measure=UnitOfMeasure.KILOGRAM,
        traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
    )
    assert product.unit_of_measure == UnitOfMeasure.KILOGRAM

    # Valid volume
    product = minimal_product(
        physical_state=ProductPhysicalState.BULK,
        unit_of_measure=UnitOfMeasure.CUBIC_METER,
        traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
    )
    assert product.unit_of_measure == UnitOfMeasure.CUBIC_METER

    # Invalid
    with pytest.raises(ValueError, match='For bulk products, unit_of_measure must be weight.*or volume'):
        minimal_product(
            physical_state=ProductPhysicalState.BULK,
            unit_of_measure=UnitOfMeasure.LITER,
            traceability=Traceability(tracking_type=ProductTrackingType.WEIGHT_BASED),
        )


def test_size_type_heavy():
    # Valid
    product = minimal_product(
        classification={'size_type': ProductSizeType.HEAVY},
        dimensions={'weight_kg': HEAVY_MIN_KG},
        handling={'is_stackable': False},
    )
    assert product.classification.size_type == ProductSizeType.HEAVY

    # Missing weight
    with pytest.raises(ValueError, match='For HEAVY products, dimensions.weight_kg is required'):
        minimal_product(
            classification={'size_type': ProductSizeType.HEAVY},
            handling={'is_stackable': False},
            dimensions={},
        )

    # Weight too low
    with pytest.raises(ValueError, match=f'For HEAVY products, weight_kg must be ≥ {HEAVY_MIN_KG} kg'):
        minimal_product(
            classification={'size_type': ProductSizeType.HEAVY},
            handling={'is_stackable': False},
            dimensions={'weight_kg': HEAVY_MIN_KG - 1},
        )


def test_size_type_oversized():
    # Valid
    product = minimal_product(
        classification={'size_type': ProductSizeType.OVERSIZED},
        dimensions={'width_cm': OVERSIZED_MIN_CM + 10},
        handling={'is_stackable': False},
    )
    assert product.classification.size_type == ProductSizeType.OVERSIZED

    # No dimensions
    with pytest.raises(ValueError, match='For OVERSIZED products, at least one dimension .* must be provided'):
        minimal_product(
            classification={'size_type': ProductSizeType.OVERSIZED},
            handling={'is_stackable': False},
            dimensions={},
        )

    # All dimensions too small
    with pytest.raises(
        ValueError, match=f'For OVERSIZED products, at least one dimension must be > {OVERSIZED_MIN_CM} cm'
    ):
        minimal_product(
            classification={'size_type': ProductSizeType.OVERSIZED},
            handling={'is_stackable': False},
            dimensions={'width_cm': OVERSIZED_MIN_CM - 10},
        )


def test_size_type_light():
    # Valid
    product = minimal_product(
        classification={'size_type': ProductSizeType.LIGHT},
        dimensions={'weight_kg': LIGHT_MAX_KG},
    )
    assert product.classification.size_type == ProductSizeType.LIGHT

    # Missing weight
    with pytest.raises(ValueError, match='For LIGHT products, dimensions.weight_kg is required'):
        minimal_product(
            classification={'size_type': ProductSizeType.LIGHT},
            dimensions={},
        )

    # Weight too high
    with pytest.raises(ValueError, match=f'For LIGHT products, weight_kg must be ≤ {LIGHT_MAX_KG} kg'):
        minimal_product(
            classification={'size_type': ProductSizeType.LIGHT},
            dimensions={'weight_kg': LIGHT_MAX_KG + 1},
        )


def test_size_type_small_parts():
    # Valid
    product = minimal_product(
        classification={'size_type': ProductSizeType.SMALL_PARTS},
        dimensions={'width_cm': SMALL_PARTS_MAX_CM - 1},
    )
    assert product.classification.size_type == ProductSizeType.SMALL_PARTS

    # No dimensions
    with pytest.raises(ValueError, match='For SMALL_PARTS products, at least one dimension .* must be provided'):
        minimal_product(
            classification={'size_type': ProductSizeType.SMALL_PARTS},
            dimensions={},
        )

    # All dimensions too large
    with pytest.raises(
        ValueError, match=f'For SMALL_PARTS products, at least one dimension must be < {SMALL_PARTS_MAX_CM} cm'
    ):
        minimal_product(
            classification={'size_type': ProductSizeType.SMALL_PARTS},
            dimensions={'width_cm': SMALL_PARTS_MAX_CM + 10},
        )


def test_handling_heavy_or_oversized_not_stackable():
    for size in (ProductSizeType.HEAVY, ProductSizeType.OVERSIZED):
        with pytest.raises(ValueError, match='Heavy or oversized products cannot be stackable'):
            minimal_product(
                classification={'size_type': size},
                handling={'is_stackable': True},
                dimensions={'weight_kg': 100, 'width_cm': 300},
            )


def test_role_returns_requires_quarantine():
    with pytest.raises(ValueError, match='Returned products must require quarantine'):
        minimal_product(
            role_type=ProductRoleType.RETURNS,
            handling={'requires_quarantine': False},
        )


# Not provided test wrong session just ignore
# def test_tracking_type_physical_state_compatibility():
#     for state in (ProductPhysicalState.LIQUID, ProductPhysicalState.GAS, ProductPhysicalState.BULK):
#         for tracking in (ProductTrackingType.PIECE, ProductTrackingType.KIT):
#             with pytest.raises(
#                 ValueError, match=f'{state.value.capitalize()} products cannot be tracked by {tracking.value}'
#             ):
#                 minimal_product(
#                     unit_of_measure=UnitOfMeasure.,
#                     physical_state=state,
#                     traceability={'tracking_type': tracking},
#                 )


# ----------------------------------------------------------------------
# 8. Complex product creation (all valid fields)
# ----------------------------------------------------------------------
def test_complex_product_creation():
    product = BaseProduct(
        sku='COMPLEX01',
        name='Complex Product',
        unit_of_measure=UnitOfMeasure.KILOGRAM,
        physical_state=ProductPhysicalState.SOLID,
        role_type=ProductRoleType.FINISHED_GOOD,
        status=ProductStatus.ACTIVE,
        description='A complex product with all compositions filled',
        dimensions={
            'weight_kg': 100.0,
            'width_cm': 150,
            'height_cm': 200,
            'depth_cm': 300,
        },  # type: ignore
        handling={
            'is_fragile': True,
            'is_stackable': False,
            'requires_ventilation': True,
        },  # type: ignore
        traceability={
            'tracking_type': ProductTrackingType.EXPIRY_TRACKED,
            'production_date': date.today() - timedelta(days=30),
            'expiry_date': date.today() + timedelta(days=30),
        },  # type: ignore
        storage_requirements={
            'storage_condition': ProductStorageCondition.PERISHABLE,
            'temperature_regime': TemperatureRegime.CHILLED,
        },  # type: ignore
        classification={
            'size_type': ProductSizeType.HEAVY,
            'moving_type': ProductMovingType.NORMAL_MOVING,
            'abc_category': ABCCategory.B,
        },  # type: ignore
    )
    assert product.sku == 'COMPLEX01'
    assert product.dimensions.volume_m3 == (150 * 200 * 300) / 1_000_000
    assert product.traceability.expiry_date == date.today() + timedelta(days=30)
    assert product.storage_requirements.temperature_regime == TemperatureRegime.CHILLED
