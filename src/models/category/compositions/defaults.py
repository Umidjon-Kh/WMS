from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated
from ...product.enums import (
    ProductStorageCondition,
    TemperatureRegime,
    HazardClass,
    PackagingType,
    UnitOfMeasure,
    ProductTrackingType,
)
from ..constants import POSITIVE_INT


class CtgDefaults(BaseModel):
    """
    Defaults if Product doesnt have one of the
    Important fields this compositor auto fill fields
    to group all tham
    """

    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # Default values for important fields to group Products
    default_storage_condition: Annotated[
        Optional[ProductStorageCondition], Field(description='Storage Condition by default')
    ] = None
    default_temperature_regime: Annotated[
        Optional[TemperatureRegime], Field(description='Temperature regime by default if it required')
    ] = None
    default_hazard_class: Annotated[
        Optional[HazardClass], Field(description='Hazard class by default if Hazardous')
    ] = None
    default_tracking_type: Annotated[Optional[ProductTrackingType], Field(description='Tracking type by default')] = (
        None
    )
    default_packaging_type: Annotated[Optional[PackagingType], Field(description='Packaging type by default')] = None
    default_shelf_life_days: Annotated[Optional[POSITIVE_INT], Field(description='Default expiry date')] = None
    default_unit_of_measure: Annotated[Optional[UnitOfMeasure], Field(description='Deafault unit of measure')] = None

    # ----------- Validators --------
    # ------- Hazard class Consistensy ------
    @model_validator(mode='after')
    def check_hazard_consistency(self) -> 'CtgDefaults':
        """If storage_condition is HAZARDOUS, hazard_class must be provided, and vice versa."""
        if self.default_storage_condition == ProductStorageCondition.HAZARDOUS and self.default_hazard_class is None:
            raise ValueError('hazard_class required for hazardous products')
        if (
            self.default_hazard_class is not None
            and self.default_storage_condition != ProductStorageCondition.HAZARDOUS
        ):
            raise ValueError('hazard_class only allowed for hazardous products')
        return self

    # --------- Tempertaure Regime required Conditions -------
    @model_validator(mode='after')
    def check_temperature_required(self) -> 'CtgDefaults':
        """If storage_condition requires temperature control, temperature_regime must be provided."""
        if self.default_storage_condition and self.default_temperature_regime:
            if (
                self.default_storage_condition
                in (
                    ProductStorageCondition.PERISHABLE,
                    ProductStorageCondition.TEMPERATURE_CONTROLLED,
                    ProductStorageCondition.MEDICINE,
                )
                and self.default_temperature_regime is None
            ):
                raise ValueError('temperature_regime required for perishable or temperature-controlled products')
        return self

    # --------- Recommendations ----------
    @model_validator(mode='after')
    def recommendations_validator(self) -> 'CtgDefaults':
        """Recommendation for StorageRequirements"""
        # For Electronics products recommend tempertaure_regime
        if (
            self.default_storage_condition == ProductStorageCondition.ELECTRONICS
            and not self.default_temperature_regime
        ):
            print('Recommendation: For product type Electronics recommendts temperature_regime')
        return self

    # ------- Storag Requirements Condition -------
    @model_validator(mode='after')
    def validate_stgc_requirements(self) -> 'CtgDefaults':
        """Validating Product Storage Condition types requirements"""
        # Validating for Perishable and Traceability products requirements
        if self.default_storage_condition and self.default_tracking_type:
            if (
                self.default_storage_condition in (ProductStorageCondition.PERISHABLE, ProductStorageCondition.MEDICINE)
                and self.default_tracking_type != ProductTrackingType.EXPIRY_TRACKED
            ):
                raise ValueError('Perishable and Medicine products must have tracking_type = EXPIRY_TRACKED')
        return self

    # -------- Tracking Type -------
    @model_validator(mode='after')
    def validate_tracking_type_units(self) -> 'CtgDefaults':
        """Validating units of measure for Product Tracking type units"""
        if self.default_tracking_type and self.default_unit_of_measure:
            # Weight Based
            if self.default_tracking_type == ProductTrackingType.WEIGHT_BASED:
                allowed = {
                    UnitOfMeasure.KILOGRAM,
                    UnitOfMeasure.GRAM,
                    UnitOfMeasure.LITER,
                    UnitOfMeasure.MILLILITER,
                    UnitOfMeasure.CUBIC_METER,
                }
                if self.default_unit_of_measure not in allowed:
                    raise ValueError(
                        'Weight-based tracking requires unit_of_measure'
                        f' in {allowed}, got {self.default_unit_of_measure}'
                    )
            # Piece
            elif self.default_tracking_type == ProductTrackingType.PIECE:
                allowed = {UnitOfMeasure.PIECE, UnitOfMeasure.BOX, UnitOfMeasure.PALLET, UnitOfMeasure.SET}
                if self.default_unit_of_measure not in allowed:
                    raise ValueError(
                        f'Piece tracking requires unit_of_measure in {allowed}, got {self.default_unit_of_measure}'
                    )
            # Kit
            elif self.default_tracking_type == ProductTrackingType.KIT:
                allowed = {UnitOfMeasure.SET, UnitOfMeasure.PIECE}
                if self.default_unit_of_measure not in allowed:
                    raise ValueError(
                        f'Kit tracking requires unit_of_measure in {allowed}, got {self.default_unit_of_measure}'
                    )
        return self
