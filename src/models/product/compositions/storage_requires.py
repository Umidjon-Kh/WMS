from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated
from ..enums import ProductStorageCondition, HazardClass, TemperatureRegime, PackagingType


class StorageRequirements(BaseModel):
    """
    Composition for product storage conditions.
    Includes storage type, hazard class, temperature regime, and packaging.
    """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    storage_condition: Annotated[
        Optional[ProductStorageCondition],
        Field(description='General storage requirements (perishable, hazardous, etc.)'),
    ] = None
    hazard_class: Annotated[Optional[HazardClass], Field(description='Dangerous goods class (if Hazardous)')] = None
    temperature_regime: Annotated[Optional[TemperatureRegime], Field(description='Required temperature regime')] = None
    packaging_type: Annotated[Optional[PackagingType], Field(description='Type of packaging used')] = None

    @model_validator(mode='after')
    def check_hazard_consistency(self) -> 'StorageRequirements':
        """If storage_condition is HAZARDOUS, hazard_class must be provided, and vice versa."""
        if self.storage_condition == ProductStorageCondition.HAZARDOUS and self.hazard_class is None:
            raise ValueError('hazard_class required for hazardous products')
        if self.hazard_class is not None and self.storage_condition != ProductStorageCondition.HAZARDOUS:
            raise ValueError('hazard_class only allowed for hazardous products')
        return self

    @model_validator(mode='after')
    def check_temperature_required(self) -> 'StorageRequirements':
        """If storage_condition requires temperature control, temperature_regime must be provided."""
        if self.storage_condition in (
            ProductStorageCondition.PERISHABLE,
            ProductStorageCondition.TEMPERATURE_CONTROLLED
        ) and self.temperature_regime is None:
            raise ValueError('temperature_regime required for perishable or temperature-controlled products')
        return self
