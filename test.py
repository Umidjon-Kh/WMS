# test_product.py
from src.models.product import BaseProduct, Dimensions
from src.models.product.enums import (
    UnitOfMeasure,
    ProductPhysicalState,
    ProductRoleType,
    ProductTrackingType,
    ProductStorageCondition,
    ProductSizeType,
    ProductStatus,
    TemperatureRegime
)


def test_create_regular_product():
    """Обычный товар без дополнительных атрибутов"""
    product = BaseProduct(
        sku="REG123",
        name="Regular Item",
        unit_of_measure=UnitOfMeasure.PIECE,
        physical_state=ProductPhysicalState.SOLID,
        role_type=ProductRoleType.FINISHED_GOOD,
        tracking_type=ProductTrackingType.PIECE,
        status=ProductStatus.ACTIVE,
    )
    assert product.sku == "REG123"
    assert product.name == "Regular Item"
    assert product.dimensions == Dimensions()  # пустые размеры
    print("✅ Regular product created")


def test_product_with_dimensions():
    """Товар с заданными габаритами (объём должен вычислиться автоматически)"""
    product = BaseProduct(
        sku="TABLE01",
        name="Стол",
        unit_of_measure=UnitOfMeasure.PIECE,
        physical_state=ProductPhysicalState.SOLID,
        role_type=ProductRoleType.FINISHED_GOOD,
        tracking_type=ProductTrackingType.PIECE,
        status=ProductStatus.ACTIVE,
        dimensions={
            "weight_kg": 15.5,
            "width_cm": 120,
            "height_cm": 75,
            "depth_cm": 60,
        },
    )
    # объём должен вычислиться: 120*75*60 / 1_000_000 = 0.54
    assert product.dimensions.volume_m3 == 0.54
    print("✅ Product with dimensions created, volume =", product.dimensions.volume_m3)


def test_perishable_product():
    """Скоропортящийся товар (требует дат и special tracking)"""
    from datetime import date, timedelta

    today = date.today()
    prod_date = today - timedelta(days=5)
    exp_date = today + timedelta(days=10)

    product = BaseProduct(
        sku="MILK01",
        name="Молоко",
        unit_of_measure=UnitOfMeasure.LITER,
        physical_state=ProductPhysicalState.LIQUID,
        role_type=ProductRoleType.FINISHED_GOOD,
        tracking_type=ProductTrackingType.EXPIRY_TRACKED,
        status=ProductStatus.ACTIVE,
        storage_condition=ProductStorageCondition.PERISHABLE,
        production_date=prod_date,
        expiry_date=exp_date,
        temperature_regime=TemperatureRegime.FROZEN
    )
    assert product.storage_condition == ProductStorageCondition.PERISHABLE
    assert product.expiry_date == exp_date
    print("✅ Perishable product created")


def test_invalid_heavy_product():
    """Товар с типом HEAVY, но без веса — должна быть ошибка"""
    import pytest

    with pytest.raises(ValueError, match="required weight_kg"):
        BaseProduct(
            sku="HEAVY01",
            name="Тяжёлый",
            unit_of_measure=UnitOfMeasure.PIECE,
            physical_state=ProductPhysicalState.SOLID,
            role_type=ProductRoleType.FINISHED_GOOD,
            tracking_type=ProductTrackingType.PIECE,
            status=ProductStatus.ACTIVE,
            size_type=ProductSizeType.HEAVY,
            # weight_kg не указан
        )


if __name__ == "__main__":
    test_create_regular_product()
    test_product_with_dimensions()
    test_perishable_product()
    test_invalid_heavy_product()
    print("\n🎉 Все тесты прошли успешно!")
