from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated
from ..constants import POSITIVE_F



class Dimensions(BaseModel):
    """
    Composition for physical sizes and weight of product.
    If all three dimensions are not None, volume calculates auto
    """
    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,   # Gives enum.value instaed of enum.key
        validate_assignment=True    # validates in setting value
    ) # type: ignore

    # -------- Volume and Weights (optional) --------
    weight_kg: Optional[POSITIVE_F] = Field(None, description='Weight in kg')
    width_cm: Optional[POSITIVE_F] = Field(None, description='Width in cm')
    height_cm: Optional[POSITIVE_F] = Field(None, description='Height in cm')
    depth_cm: Optional[POSITIVE_F] = Field(None, description='Depth in cm')
    volume_m3: Optional[POSITIVE_F] = Field(None, description='Volume in cubic meters')

    @model_validator(mode='after')
    def calculato_vol(self) -> 'Dimensions':
        """Returns claculated volume size"""
        if self.volume_m3 is None and self.width_cm and self.height_cm and self.depth_cm:
            # Volume in m^3: = (cm * cm * cm) / 1_000_000
            self.volume_m3 = (self.width_cm * self.height_cm * self.depth_cm) / 1_000_000
        return self


