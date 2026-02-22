from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from typing import Optional
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

    # -------- Cross Validators ---------
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

    @model_validator(mode='after')
    def check_timesmaps(self) -> 'BaseProduct':
        """Validating timestamps of product"""
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cant be earlier than creation_at')
        return self

    @model_validator(mode='after')
    def validate_units(self) -> 'BaseProduct':
        """Validating unit matchings"""
        # ------- Dict for all units type ---------
        weight_units = {UnitOfMeasure.KILOGRAM, UnitOfMeasure.GRAM}
        piece_units = {UnitOfMeasure.PIECE, UnitOfMeasure.BOX, UnitOfMeasure.PALLET, UnitOfMeasure.SET}
        # volume_units = {UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER, UnitOfMeasure.CUBIC_METER}
        liquid_units = {UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER}
        gas_units = {UnitOfMeasure.LITER, UnitOfMeasure.MILLILITER, UnitOfMeasure.CUBIC_METER}
        bulk_units = weight_units | {UnitOfMeasure.CUBIC_METER}

        # ------- Tracking type unit validation -------
        # Weight based
        if self.traceability.tracking_type == ProductTrackingType.WEIGHT_BASED:
            # Checking unit
            if self.unit_of_measure not in weight_units:
                raise ValueError('For tracking type Weight-Based products units must be in kg or gram')
        # Piece
        elif self.traceability.tracking_type == ProductTrackingType.PIECE:
            # Checking unit
            if self.unit_of_measure not in piece_units:
                raise ValueError('For tracking type Piece products units must be in pc, box, pallet or set')
        # Kit
        elif self.traceability.tracking_type == ProductTrackingType.KIT:
            # Checking unit
            if self.unit_of_measure not in (UnitOfMeasure.SET, UnitOfMeasure.PIECE):
                raise ValueError('For tracking type Kit products units must be in set or pc')

        # ---------- Physical state unit validation
        # Liquids
        if self.physical_state == ProductPhysicalState.LIQUID:
            # Checking unit
            if self.unit_of_measure not in liquid_units:
                raise ValueError('For products with physical state Liquid units must be in liter or mililiter')
            # Checking packaging type
            if self.storage_requirements.packaging_type == PackagingType.BOX:
                raise ValueError('Liquid products cannot be stored in boxes')
        # Gas
        elif self.physical_state == ProductPhysicalState.GAS:
            # Checking unit
            if self.unit_of_measure not in gas_units:
                raise ValueError(
                    'For products with physical state Gas units must be in liter, mililiter or cubic meter'
                )
            # Checking packaging type for gas
            if self.storage_requirements.packaging_type not in (PackagingType.CYLINDER, PackagingType.DRUM, None):
                raise ValueError('For products with physical state Gas packaging type must be in cylinder or drum')
            # Checking handling flags for gas
            if not self.handling.requires_ventilation:
                raise ValueError('Gas products should have requires_ventilation')
        # Bulk
        elif self.physical_state == ProductPhysicalState.BULK:
            # Checking unit
            if self.unit_of_measure not in bulk_units:
                raise ValueError('For products physical type Bulk units must be in weight or volume')
        return self

    @model_validator(mode='after')
    def validate_size_type(self) -> 'BaseProduct':
        """Validating size type requirements"""
        dims = self.dimensions
        # Heavy
        if self.classification.size_type == ProductSizeType.HEAVY:
            # Checking weight noen or not
            if dims.weight_kg is None:
                raise ValueError('For size_type Heavy products required weight_kg field')
            # Checking limit
            if dims.weight_kg < HEAVY_MIN_KG:
                raise ValueError(f'For size_type Heavy products min required weitgh is {HEAVY_MIN_KG} kg')

        # Over-sized
        elif self.classification.size_type == ProductSizeType.OVERSIZED:
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
        elif self.classification.size_type == ProductSizeType.LIGHT:
            # Checking weight is none or not
            if dims.weight_kg is None:
                raise ValueError('For sized_type Light products required weight_kg field')
            # Checking max weight for light products
            if dims.weight_kg > LIGHT_MAX_KG:
                raise ValueError(f'For size_type Light products max required weight is {LIGHT_MAX_KG} kg')

        # Small-parts
        elif self.classification.size_type == ProductSizeType.SMALL_PARTS:
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

    @model_validator(mode='after')
    def validate_handlings(self) -> 'BaseProduct':
        """Validating handling matchings"""
        if not self.handling.is_stackable and self.classification.size_type in (
            ProductSizeType.HEAVY,
            ProductSizeType.OVERSIZED,
        ):
            raise ValueError('Heavy or oversized products cannot be stackable')
        return self

    @model_validator(mode='after')
    def validate_role(self) -> 'BaseProduct':
        """Validating role type matchings"""
        # For returned products must require quarantine
        if self.role_type == ProductRoleType.RETURNS and not self.handling.requires_quarantine:
            raise ValueError('Returned products must require quarantine')
        return self
