from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, Annotated
from .compositions import Dimensions, HandlingAttributes, Traceability, StorageRequirements, Classification
from .constants import (
    NAME_VALID,
    SKU_VALID,
    DES_VALID,
    HEAVY_MIN_KG,
    OVERSIZED_MIN_CM,
    LIGHT_MAX_KG,
    SMALL_PARTS_MAX_CM,
)
from .enums import (
    UnitOfMeasure,
    ProductPhysicalState,
    ProductStorageCondition,
    ProductSizeType,
    ProductTrackingType,
    ProductRoleType,
    PackagingType,
    ProductStatus,
)


# -------- Base Class Of Product --------
class BaseProduct(BaseModel):
    """
    Main core class that contains alls fields, Compostions
    and Cross Validators that need to work between compositions
    """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # ----- main fields -----
    sku: SKU_VALID
    name: NAME_VALID
    category_id: Annotated[Optional[UUID], Field(frozen=True, description='Category id')]
    unit_of_measure: UnitOfMeasure = Field(..., description='Base unit of measure (how product is counted)')
    physical_state: ProductPhysicalState = Field(..., description='Physical state of product')
    role_type: ProductRoleType = Field(..., description='Product role in production/logistic chain')
    status: ProductStatus = Field(..., description='Current lifecycle status')
    description: Optional[DES_VALID] = None

    # ---------- Compositions -------
    dimensions: Dimensions = Field(default_factory=lambda: Dimensions())
    handling: HandlingAttributes = Field(default_factory=lambda: HandlingAttributes())
    traceability: Traceability
    storage_requirements: StorageRequirements = Field(default_factory=lambda: StorageRequirements())
    classification: Classification = Field(default_factory=lambda: Classification())

    # ------ Technical fields (auto sets) -------
    created_at: datetime = Field(default_factory=datetime.now, description='Creation timestamp')
    updated_at: datetime = Field(default_factory=datetime.now, description='Las update timestamp')

    # ----------------------- Cross Validators ---------------------

    # ------- Storag Requirements Condition -------
    @model_validator(mode='after')
    def validate_stgc_requirements(self) -> 'BaseProduct':
        """Validating Product Storage Condition types requirements"""
        # Validating for Perishable and Traceability products requirements
        if (
            self.storage_requirements.storage_condition
            in (ProductStorageCondition.PERISHABLE, ProductStorageCondition.MEDICINE)
            and self.traceability.tracking_type != ProductTrackingType.EXPIRY_TRACKED
        ):
            raise ValueError('Perishable and Medicine products must have tracking_type = EXPIRY_TRACKED')

        # Validation for Electronic product requirements
        elif (
            self.storage_requirements.storage_condition == ProductStorageCondition.ELECTRONICS
            and not self.handling.is_static_sensitive
        ):
            raise ValueError('Electronis products must be static sensitive')
        return self

    # ------- Time-Stamps ------
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'BaseProduct':
        """Validating timestamps of product"""
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cant be earlier than creation_at')
        return self

    # ------- Handlings ------
    @model_validator(mode='after')
    def validate_handlings(self) -> 'BaseProduct':
        """Validating handling matchings"""
        if self.handling.is_stackable and self.classification.size_type in (
            ProductSizeType.HEAVY,
            ProductSizeType.OVERSIZED,
        ):
            raise ValueError('Heavy or oversized products cannot be stackable')
        return self

    # ------- Role Type ------
    @model_validator(mode='after')
    def validate_role(self) -> 'BaseProduct':
        """Validating role type matchings"""
        # For returned products must require quarantine
        if self.role_type == ProductRoleType.RETURNS and not self.handling.requires_quarantine:
            raise ValueError('Returned products must require quarantine')
        return self

    # ------- Physical State -------
    @model_validator(mode='after')
    def validate_physical_state_units(self) -> 'BaseProduct':
        """Validating unit of measure for Physical state of Product"""
        # Liquid
        if self.physical_state == ProductPhysicalState.LIQUID:
            # Validating unit of measure
            if self.unit_of_measure not in (UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER):
                raise ValueError(
                    f'For liquid products, unit_of_measure must be LITER or MILLILITER, got {self.unit_of_measure}'
                )
            # Validating packaging type
            if self.storage_requirements.packaging_type == PackagingType.BOX:
                raise ValueError('Liquid products cannot be stored in boxes')

        # Gas
        elif self.physical_state == ProductPhysicalState.GAS:
            # Validating unit of measure
            if self.unit_of_measure not in (UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER, UnitOfMeasure.CUBIC_METER):
                raise ValueError(
                    'For gas products, unit_of_measure must be LITER, MILLILITER,'
                    f' or CUBIC_METER, got {self.unit_of_measure}'
                )
            # Validating packaging type
            if self.storage_requirements.packaging_type not in (PackagingType.CYLINDER, PackagingType.DRUM, None):
                raise ValueError('For gas products, packaging_type must be CYLINDER or DRUM')
            # Validating ventilation requires
            if not self.handling.requires_ventilation:
                raise ValueError("Gas products must have requires_ventilation = True")

        # Bulk
        elif self.physical_state == ProductPhysicalState.BULK:
            # Validating unit of measure
            if self.unit_of_measure not in (UnitOfMeasure.KILOGRAM, UnitOfMeasure.GRAM, UnitOfMeasure.CUBIC_METER):
                raise ValueError(
                    'For bulk products, unit_of_measure must be weight'
                    f'(KILOGRAM, GRAM) or volume (CUBIC_METER), got {self.unit_of_measure}'
                )
        # For Solid physical state we dont have limits in units
        return self

    # -------- Tracking Type -------
    @model_validator(mode='after')
    def validate_tracking_type_units(self) -> 'BaseProduct':
        """Validating units of measure for Product Tracking type units"""
        # Weight Based
        if self.traceability.tracking_type == ProductTrackingType.WEIGHT_BASED:
            allowed = {
                UnitOfMeasure.KILOGRAM,
                UnitOfMeasure.GRAM,
                UnitOfMeasure.LITER,
                UnitOfMeasure.MILLILITER,
                UnitOfMeasure.CUBIC_METER,
            }
            if self.unit_of_measure not in allowed:
                raise ValueError(
                    f'Weight-based tracking requires unit_of_measure in {allowed}, got {self.unit_of_measure}'
                )
        # Piece
        elif self.traceability.tracking_type == ProductTrackingType.PIECE:
            allowed = {UnitOfMeasure.PIECE, UnitOfMeasure.BOX, UnitOfMeasure.PALLET, UnitOfMeasure.SET}
            if self.unit_of_measure not in allowed:
                raise ValueError(f'Piece tracking requires unit_of_measure in {allowed}, got {self.unit_of_measure}')
        # Kit
        elif self.traceability.tracking_type == ProductTrackingType.KIT:
            allowed = {UnitOfMeasure.SET, UnitOfMeasure.PIECE}
            if self.unit_of_measure not in allowed:
                raise ValueError(f'Kit tracking requires unit_of_measure in {allowed}, got {self.unit_of_measure}')
        return self

    # -------- Tracking Type and Physical State Compability --------
    @model_validator(mode='after')
    def validate_tracking_type_physical_state_compatibility(self):
        """Validating Product physical state compability with tracking type"""
        # Liquid, Bulk and Gas
        if self.physical_state in (ProductPhysicalState.BULK, ProductPhysicalState.LIQUID, ProductPhysicalState.GAS):
            if self.traceability.tracking_type in (ProductTrackingType.PIECE, ProductTrackingType.KIT):
                raise ValueError(
                    f'{self.physical_state.value.capitalize()} products cannot be tracked by '
                    f'{self.traceability.tracking_type.value}'
                )
        return self

    # --------- Size Type --------
    @model_validator(mode='after')
    def validate_size_type_heavy(self) -> 'BaseProduct':
        if self.classification.size_type == ProductSizeType.HEAVY:
            # Dimensions weight_kg is required
            if self.dimensions.weight_kg is None:
                raise ValueError('For HEAVY products, dimensions.weight_kg is required')
            # Validate min weight for heavy type
            if self.dimensions.weight_kg < HEAVY_MIN_KG:
                raise ValueError(
                    f'For HEAVY products, weight_kg must be ≥ {HEAVY_MIN_KG} kg, got {self.dimensions.weight_kg}'
                )
        return self

    @model_validator(mode='after')
    def validate_size_type_oversized(self):
        if self.classification.size_type == ProductSizeType.OVERSIZED:
            # Dimension minimum 1 of 3 required dims
            if (
                self.dimensions.width_cm is None
                and self.dimensions.height_cm is None
                and self.dimensions.depth_cm is None
            ):
                raise ValueError(
                    'For OVERSIZED products, at least one dimension (width_cm, height_cm, depth_cm) must be provided'
                )
            # Validating requirements for over-sized type minimums
            if not (
                (self.dimensions.width_cm and self.dimensions.width_cm > OVERSIZED_MIN_CM)
                or (self.dimensions.height_cm and self.dimensions.height_cm > OVERSIZED_MIN_CM)
                or (self.dimensions.depth_cm and self.dimensions.depth_cm > OVERSIZED_MIN_CM)
            ):
                raise ValueError(f'For OVERSIZED products, at least one dimension must be > {OVERSIZED_MIN_CM} cm')
        return self

    @model_validator(mode='after')
    def validate_size_type_light(self):
        if self.classification.size_type == ProductSizeType.LIGHT:
            # Dimensions weight_kg is required
            if self.dimensions.weight_kg is None:
                raise ValueError('For LIGHT products, dimensions.weight_kg is required')
            # Validating max weight for light type
            if self.dimensions.weight_kg > LIGHT_MAX_KG:
                raise ValueError(
                    f'For LIGHT products, weight_kg must be ≤ {LIGHT_MAX_KG} kg, got {self.dimensions.weight_kg}'
                )
        return self

    @model_validator(mode='after')
    def validate_size_type_small_parts(self):
        if self.classification.size_type == ProductSizeType.SMALL_PARTS:
            # Dimensions minimum 1 of 3 required
            if (
                self.dimensions.width_cm is None
                and self.dimensions.height_cm is None
                and self.dimensions.depth_cm is None
            ):
                raise ValueError(
                    'For SMALL_PARTS products, at least one dimension (width_cm, height_cm, depth_cm) must be provided'
                )
            # Validating maximum limit for small-parts type
            if not (
                (self.dimensions.width_cm and self.dimensions.width_cm < SMALL_PARTS_MAX_CM)
                or (self.dimensions.height_cm and self.dimensions.height_cm < SMALL_PARTS_MAX_CM)
                or (self.dimensions.depth_cm and self.dimensions.depth_cm < SMALL_PARTS_MAX_CM)
            ):
                raise ValueError(f'For SMALL_PARTS products, at least one dimension must be < {SMALL_PARTS_MAX_CM} cm')
        return self
