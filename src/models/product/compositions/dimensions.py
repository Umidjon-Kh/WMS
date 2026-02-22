from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated
from ..constants import POSITIVE_F


class Dimensions(BaseModel):
    """
    Composition for Product Dimensions its Optional
    Cause one of the size type objects dont need
    all fields to be initialized its need to check
    dimensions or weight required for size type product
    """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # Volume and Weights (optional)
    weight_kg: Annotated[Optional[POSITIVE_F], Field(description='Weight in kg')] = None
    width_cm: Annotated[Optional[POSITIVE_F], Field(description='Width in cm')] = None
    height_cm: Annotated[Optional[POSITIVE_F], Field(description='Height in cm')] = None
    depth_cm: Annotated[Optional[POSITIVE_F], Field(description='Depth in cm')] = None
    volume_m3: Annotated[Optional[POSITIVE_F], Field(description='Volume in cubic meters')] = None

    # ----------- Validators --------
    @model_validator(mode='after')
    def calculato_vol(self) -> 'Dimensions':
        """If all three dimensions are not None, volume calculates auto"""
        if self.volume_m3 is None and self.width_cm and self.height_cm and self.depth_cm:
            # Volume in m^3: = (cm * cm * cm) / 1_000_000
            self.volume_m3 = (self.width_cm * self.height_cm * self.depth_cm) / 1_000_000
        return self
