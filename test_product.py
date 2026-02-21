from src.models.product import 
from src.models.enums import UnitOfMeasure, ProductPhysicalState, ProductRoleType, ProductTrackingType, ProductSizeType

# Продукт с размерами
p1 = BaseProduct(
    sku="TABLE01",
    name="Стол",
    unit_of_measure=UnitOfMeasure.PIECE,
    physical_state=ProductPhysicalState.SOLID,
    role_type=ProductRoleType.FINISHED_GOOD,
    traceability={"tracking_type": ProductTrackingType.PIECE},
    dimensions={"weight_kg": 15.5, "width_cm": 120, "height_cm": 75, "depth_cm": 60}
)

print(p1.dimensions.volume_m3)  # должно вывести 0.54
print(p1)

# Продукт без размеров
p2 = BaseProduct(
    sku="SAND01",
    name="Песок",
    unit_of_measure=UnitOfMeasure.KILOGRAM,
    physical_state=ProductPhysicalState.BULK,
    role_type=ProductRoleType.RAW_MATERIAL,
    traceability={"tracking_type": ProductTrackingType.WEIGHT_BASED}
)
print(p2.dimensions)  # пустой объект Dimensions с None