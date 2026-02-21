from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Optional, Annotated
from datetime import date
from ..enums import ProductTrackingType


class Traceability(BaseModel):
    """
    Composition for product traceability attributes
    Includes tracking type, production date, expiry date and related validations
    """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # Tracking type
    tracking_type: ProductTrackingType = Field(..., description='How the product is tracked (piece, weitgh, etc...)')
    # For products that need production and expiry date
    production_date: Annotated[Optional[date], Field(description='Date of product production')] = None
    expiry_date: Annotated[Optional[date], Field(description='Date of product expiry')] = None

    @field_validator('expiry_date')
    @classmethod
    def check_expiry_not_past(cls, value: Optional[date]) -> Optional[date]:
        """Expiry date cannot be in the past (if provided)."""
        if value is not None and value < date.today():
            raise ValueError('expiry_date cannot be in the past')
        return value

    @model_validator(mode='after')
    def check_dates_consistency(self) -> 'Traceability':
        """If both dates provided, expiry must be after production."""
        if self.production_date and self.expiry_date:
            if self.expiry_date <= self.production_date:
                raise ValueError('expiry_date must be later than production_date')
        return self

    @model_validator(mode='after')
    def check_expiry_tracking(self) -> 'Traceability':
        """If tracking type is EXPIRY_TRACKED, both dates must be provided."""
        if self.tracking_type == ProductTrackingType.EXPIRY_TRACKED:
            if self.production_date is None:
                raise ValueError('production_date required for expiry tracked products')
            if self.expiry_date is None:
                raise ValueError('expiry_date required for expiry tracked products')
        return self
