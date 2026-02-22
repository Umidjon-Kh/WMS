from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated
from ..enums import ProductSizeType, ProductMovingType, ABCCategory


class Classification(BaseModel):
    """
    Composition for product classification attributes.
    Includes size/weight category, turnover characteristic, and ABC category.
    """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    size_type: Annotated[
        Optional[ProductSizeType],
        Field(description='Size/weight category (oversized, heavy, light, small parts, etc.)'),
    ] = None

    moving_type: Annotated[
        Optional[ProductMovingType], Field(description='Turnover characteristic (fast, normal, slow moving, etc.)')
    ] = None

    abc_category: Annotated[
        Optional[ABCCategory], Field(description='ABC classification for inventory optimization (A, B, C, D)')
    ] = None

    # ----------- Validators --------
    @model_validator(mode='after')
    def validate_size_moving(self) -> 'Classification':
        """Validating size_type type matching with moving"""
        # For Heavy and Over_Sized must be not Fast Moving
        if (
            self.size_type in (ProductSizeType.HEAVY, ProductSizeType.OVERSIZED)
            and self.moving_type == ProductMovingType.FAST_MOVING
        ):
            raise ValueError('For Products with size_type Heavy and Over_sized moving_type cant be fast')
        return self

    @model_validator(mode='after')
    def validate_category(self) -> 'Classification':
        """Validating category type matching with moving"""
        if self.abc_category == ABCCategory.A and self.moving_type not in (
            ProductMovingType.FAST_MOVING,
            ProductMovingType.NORMAL_MOVING,
        ):
            raise ValueError('Products with ABC category A must have moving_type FAST_MOVING or NORMAL_MOVING')
        return self
