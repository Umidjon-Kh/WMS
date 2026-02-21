from pydantic import BaseModel, ConfigDict, Field, model_validator

# from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Optional, Annotated
from .constants import (
    NAME_VALID,
    SKU_VALID,
    # POSITIVE_F,
    DES_VALID,
    HEAVY_MIN_KG,
    OVERSIZED_MIN_CM,
    LIGHT_MAX_KG,
    SMALL_PARTS_MAX_CM,
)
from .compositions import Dimensions
from .enums import (
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
    # HandlingAttribute,
    PackagingType,
    ProductStatus,
)


# -------- Base Class Of Product --------
class BaseProduct(BaseModel):
    """Main class that contains all"""

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # ----- main fields -----
    sku: SKU_VALID
    name: NAME_VALID
    unit_of_measure: UnitOfMeasure = Field(..., description='Base unit of measure (how product is counted)')
    physical_state: ProductPhysicalState = Field(..., description='Physical state of product')
    tracking_type: ProductTrackingType = Field(..., description='How the product is tracked (piece, weitgh, etc...)')
    role_type: ProductRoleType = Field(..., description='Product role in production/logistic chain')
    status: ProductStatus = Field(..., description='Current lifecycle status')

    # -------- Optional fields default None ------
    description: Optional[DES_VALID] = None
    storage_condition: Annotated[
        Optional[ProductStorageCondition], Field(description='General storage requirements')
    ] = None
    size_type: Annotated[Optional[ProductSizeType], Field(description='Size/weight category')] = None
    moving_type: Annotated[Optional[ProductMovingType], Field(description='Turnover characteristic')] = None
    hazard_class: Annotated[Optional[HazardClass], Field(description='Dangerous goods class (if Hazardous)')] = None
    temperature_regime: Annotated[Optional[TemperatureRegime], Field(description='Required temperature regime')] = None
    abc_category: Annotated[
        Optional[ABCCategory], Field(description='ABC classification for inventory optimization')
    ] = None
    packaging_type: Annotated[Optional[PackagingType], Field(description='Type of packaging used')] = None

    # All compostions with default value
    # --------  Dimensions --------
    dimensions: Dimensions = Field(default_factory=lambda: Dimensions())

    # -------- Special Flags for Handling (bool) --------
    # I used bool instead of HandlingAttribute cause it more better
    # In my opinian but if you want to use Handling Attributes just
    # Replace bool wth Optional[]
    is_fragile: Annotated[bool, Field(description='Fragile item')] = False
    is_stackable: Annotated[bool, Field(description='Can be stacked')] = True
    is_odor_sensitive: Annotated[bool, Field(description='Absorbs odors')] = False
    requires_ventilation: Annotated[bool, Field(description='Need ventilation')] = False
    requires_quarantine: Annotated[bool, Field(description='Requires quarantine after return')] = False
    is_magnetic: Annotated[bool, Field(description='Magnetic properties')] = False
    is_static_sensitive: Annotated[bool, Field(description='Sensitive to static electricity')] = False
    irregular_shape: Annotated[bool, Field(description='Irregular shape')] = False

    # ------ Technical fields (auto sets) -------
    created_at: datetime = Field(default_factory=datetime.now, description='Creation timestamp')
    updated_at: datetime = Field(default_factory=datetime.now, description='Las update timestamp')

    # ------ For products that need their production and expiry date --------
    production_date: Annotated[Optional[date], Field(description='Date of product production')] = None
    expiry_date: Annotated[Optional[date], Field(description='Date of product expiry')] = None

    # -------- Validators ---------
    @model_validator(mode='after')
    def check_hazard_cls(self) -> 'BaseProduct':
        """Validation Hazard class and Hazardous product"""
        if (
            self.storage_condition == ProductStorageCondition.HAZARDOUS
            and self.hazard_class is None
            or self.hazard_class
            and self.storage_condition != ProductStorageCondition.HAZARDOUS
        ):
            raise ValueError('Field hazard_class only need for Hazardous products')
        return self

    @model_validator(mode='after')
    def check_temp_regime(self) -> 'BaseProduct':
        """If product_storage_condition type is Temperature_regime we need to check temperature_regime"""
        if (
            self.storage_condition
            in (ProductStorageCondition.PERISHABLE, ProductStorageCondition.TEMPERATURE_CONTROLLED)
            and self.temperature_regime is None
        ):
            raise ValueError('temperature_regime is required for Temperature-controlled or Perishable products')
        return self

    @model_validator(mode='after')
    def validate_perishable(self) -> 'BaseProduct':
        """Validation for Product type Perishable"""
        if self.storage_condition == ProductStorageCondition.PERISHABLE:
            if self.production_date is None:
                raise ValueError('production_date is required for Perishable products')
            if self.expiry_date is None:
                raise ValueError('expiry_date is required for Perishable products')
            if self.expiry_date <= self.production_date:
                raise ValueError('expiry_date must be later the production_date')
            if self.expiry_date < date.today():
                raise ValueError('Product expiry_date is out of date')
            if self.tracking_type != ProductTrackingType.EXPIRY_TRACKED:
                raise ValueError('For Perishable product  tracking_type must be expiry_tracked')
        return self

    @model_validator(mode='after')
    def validate_date_consistensy(self) -> 'BaseProduct':
        """Validation for dates"""
        if self.expiry_date and self.production_date:
            if self.expiry_date <= self.production_date:
                raise ValueError('expiry_date must be later than production_date')
            if self.expiry_date < date.today():
                raise ValueError('Product expiry_date is out of date')
        return self

    @model_validator(mode='after')
    def check_timesmaps(self) -> 'BaseProduct':
        """Check timestamps"""
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cant be earlier than creation_at')
        return self

    @model_validator(mode='after')
    def validate_units(self) -> 'BaseProduct':
        """Validation for units"""
        # ------- Dict for all units type ---------
        weight_units = {UnitOfMeasure.KILOGRAM, UnitOfMeasure.GRAM}
        piece_units = {UnitOfMeasure.PIECE, UnitOfMeasure.BOX, UnitOfMeasure.PALLET, UnitOfMeasure.SET}
        # volume_units = {UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER, UnitOfMeasure.CUBIC_METER}
        liquid_units = {UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER}
        gas_units = {UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER, UnitOfMeasure.CUBIC_METER}
        bulk_units = weight_units | {UnitOfMeasure.CUBIC_METER}

        # ------- Tracking type unit validation -------
        # Weight based
        if self.tracking_type == ProductTrackingType.WEIGHT_BASED:
            if self.unit_of_measure not in weight_units:
                raise ValueError('For tracking type Weight-Based products units must be in kg or gram')
        # Piece
        elif self.tracking_type == ProductTrackingType.PIECE:
            if self.unit_of_measure not in piece_units:
                raise ValueError('For tracking type Piece products units must be in pc, box, pallet or set')
        # Kit
        elif self.tracking_type == ProductTrackingType.KIT:
            if self.unit_of_measure not in (UnitOfMeasure.SET, UnitOfMeasure.PIECE):
                raise ValueError('For tracking type Kit products units must be in set or pc')

        # ---------- Physical state unit validation
        # Liquids
        if self.physical_state == ProductPhysicalState.LIQUID:
            if self.unit_of_measure not in liquid_units:
                raise ValueError('For products with physical state Liquid units must be in liter or mililiter')
        # Gas
        elif self.physical_state == ProductPhysicalState.GAS:
            # Checking unit
            if self.unit_of_measure not in gas_units:
                raise ValueError(
                    'For products with physical state Gas units must be in liter, mililiter or cubic meter'
                )
            # Addtional chacking packaging type
            if self.packaging_type not in (PackagingType.CYLINDER, PackagingType.DRUM, None):
                raise ValueError('For products with physical state Gas packaging type must be in cylinder or drum')
        # Bulk
        elif self.physical_state == ProductPhysicalState.BULK:
            if self.unit_of_measure not in bulk_units:
                raise ValueError('For products physical type Bulk units must be in weight or volume')
        return self

    @model_validator(mode='after')
    def validate_size_type(self) -> 'BaseProduct':
        """Validation for size type"""
        dims = self.dimensions
        # Heavy
        if self.size_type == ProductSizeType.HEAVY:
            # Checking weight noen or not
            if dims.weight_kg is None:
                raise ValueError('For size_type Heavy products required weight_kg field')
            # Checking limit
            if dims.weight_kg < HEAVY_MIN_KG:
                raise ValueError(f'For size_type Heavy products min required weitgh is {HEAVY_MIN_KG} kg')

        # Over-sized
        elif self.size_type == ProductSizeType.OVERSIZED:
            # Checkin contains dimension or not
            if dims.width_cm is None and dims.height_cm is None and dims.depth_cm is None:
                raise ValueError('For size_type Over-sized products min required 1 of 3 dimension(weight/height/depth)')
            # chekcing min cm of dimensions
            if not (
                dims.width_cm
                and dims.width_cm > OVERSIZED_MIN_CM
                or dims.height_cm
                and dims.height_cm > OVERSIZED_MIN_CM
                or dims.depth_cm
                and dims.depth_cm > OVERSIZED_MIN_CM
            ):
                raise ValueError(f'For size_type Over-sized products min required size is {OVERSIZED_MIN_CM} cm')

        # Light
        elif self.size_type == ProductSizeType.LIGHT:
            # Checking weight is none or not
            if dims.weight_kg is None:
                raise ValueError('For sized_type Light products required weight_kg field')
            # Checking max weight for light products
            if dims.weight_kg > LIGHT_MAX_KG:
                raise ValueError(f'For size_type Light products max required weight is {LIGHT_MAX_KG} kg')

        # Small-parts
        elif self.size_type == ProductSizeType.SMALL_PARTS:
            # Checkin contains dimension or not
            if dims.width_cm is None and dims.height_cm is None and dims.depth_cm is None:
                raise ValueError(
                    'For size_type Small-parts products min required 1 of 3 dimension(weight/height/depth)'
                )
            # chekcing min cm of dimensions
            if not (
                dims.width_cm
                and dims.width_cm < SMALL_PARTS_MAX_CM
                or dims.height_cm
                and dims.height_cm < SMALL_PARTS_MAX_CM
                or dims.depth_cm
                and dims.depth_cm < SMALL_PARTS_MAX_CM
            ):
                raise ValueError(f'For size_type Small-parts products max required size is {SMALL_PARTS_MAX_CM} cm')

        # For other size types if we need we add conditions for them
        # later not know caouse its not required
        return self
