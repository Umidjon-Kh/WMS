from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, Annotated
from .product_enum import (
    UnitOfMeasure,
    ProductPhysicalState,
    ProductStorageCondition,
    ProductSizeType,
    ProductMovingType,
    ProductTrackingType,
    ProductRoleType,
    HazardClass,
    TemperatureRegime,
    ABCCategory,
    HandlingAttribute,
    PackagingType,
    ProductStatus,
)

SKU_VALID = Annotated[str, Field(pattern=r'^[A-Z0-9]{3,20}$', min_length=1, max_length=50, description='Unique SKU (Stock Keeping Unit)')]
POSITIVE_F = Annotated[float, Field(ge=0)]
NAME_VALID = Annotated[str, Field(min_length=1, max_length=50, json_schema_extra={'strip_whitespace': True})]
DES_VALID = Annotated[Optional[str], Field(default=None, max_length=300)]
# -------- Base Class Of Product --------
class BaseProduct(BaseModel):
    """Main class that contains all """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,   # Gives enum.value instaed of enum.key
        validate_assignment=True    # validates in setting value
    ) # type: ignore

    # ----- main fields -----
    sku: SKU_VALID
    name: NAME_VALID
    unit_of_measure: UnitOfMeasure = Field(
        ..., description='Base unit of measure (how product is counted)'
    )
    physical_state: ProductPhysicalState = Field(
        ..., description='Physical state of product'
    )
    tracking_type: ProductTrackingType = Field(
        ..., description='How the product is tracked (piece, weitgh, etc...)'
    )
    role_type: ProductRoleType = Field(
        ..., description='Product role in production/logistic chain'
    )
    status: ProductStatus = Field(
        ..., description='Current lifecycle status'
    )

    # -------- Optional fields default None ------
    description: DES_VALID
    storage_condition: Optional[ProductStorageCondition] = Field(
        None, description='General storage requirements'
    )
    size_type: Optional[ProductSizeType] = Field(
        None, description='Size/weight category'
    )
    moving_type: Optional[ProductMovingType] = Field(
        None, description='Turnover characteristic'
    )
    hazard_class: Optional[HazardClass] = Field(
        None, description='Dangerous goods class (if Hazardous)'
    )
    temperature_regime: Optional[TemperatureRegime] = Field(
        None, description='Required temperature regime'
    )
    abc_category: Optional[ABCCategory] = Field(
        None, description='ABC classification for inventory optimization'
    )
    packaging_type: Optional[PackagingType] = Field(
        None, description='Type of packaging used'
    )

    # -------- Volume and Weights (optional) --------
    weight_kg: Annotated[Optional[POSITIVE_F], Field(description='Weight in kg')]
    width_cm: Annotated[Optional[POSITIVE_F], Field(description='Width in cm')]
    height_cm: Annotated[Optional[POSITIVE_F], Field(description='Height in cm')]
    depth_cm: Annotated[Optional[POSITIVE_F], Field(description='Depth in cm')]
    volume_m3: Annotated[Optional[POSITIVE_F], Field(description='Volume in cubic meters')]

    # -------- Special Flags for Handling (bool) --------
    # I used bool instead of HandlingAttribute cause it more better
    # In my opinian but if you want to use Handling Attributes just
    # Replace bool wth Optional[]
    is_fragile: bool = Field(False, description='Fragile item')
    is_stackable: bool = Field(True, description='Can be stacked')
    is_odor_sensitive: bool = Field(False, description='Absorbs odors')
    requires_ventilation: bool = Field(False, description='Need ventilation')
    requires_quarantine: bool = Field(False, description='Requires quarantine after return')
    is_magnetic: bool = Field(False, description='Magnetic properties')
    is_static_sensitive: bool = Field(False, description='Sensitive to static electricity')
    irregular_shape: bool = Field(False, description='Irregular shape')


    # ------ Technical fields (auto sets) -------
    created_at: datetime = Field(default_factory=datetime.now, description='Creation timestamp')
    updated_at: datetime = Field(default_factory=datetime.now, description='Las update timestamp')

    # -------- Validators ---------
    @model_validator(mode='after')
    def check_hazard_cls(self) -> 'BaseProduct':
        if self.storage_condition == ProductStorageCondition.HAZARDOUS and self.hazard_class is None:
            raise ValueError('hazard_class is required for hazardous product')
        return self
    
    @model_validator(mode='after')
    def check_temp_regime(self) -> 'BaseProduct':
        if self.storage_condition == ProductStorageCondition.TEMPERATURE_CONTROLLED and self.temperature_regime is None:
            raise ValueError('temperature_regime is required for temperature-controlled product')
        return self
