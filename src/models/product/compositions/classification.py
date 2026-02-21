from pydantic import BaseModel, ConfigDict, Field
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
