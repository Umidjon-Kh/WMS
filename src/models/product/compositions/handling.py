from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated


class HandlingAttributes(BaseModel):
    """
    Attributes of product that need to info
    of Specific Flags
    """

    # Pydantic model Configuration
    model_config = ConfigDict(
        slots=True,
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    is_fragile: Annotated[bool, Field(description='Fragile item')] = False
    is_stackable: Annotated[bool, Field(description='Can be stacked')] = True
    is_odor_sensitive: Annotated[bool, Field(description='Absorbs odors')] = False
    requires_ventilation: Annotated[bool, Field(description='Need ventilation')] = False
    requires_quarantine: Annotated[bool, Field(description='Requires quarantine after return')] = False
    is_magnetic: Annotated[bool, Field(description='Magnetic properties')] = False
    is_static_sensitive: Annotated[bool, Field(description='Sensitive to static electricity')] = False
    irregular_shape: Annotated[bool, Field(description='Irregular shape')] = False
