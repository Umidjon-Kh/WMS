from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated


class HandlingAttributes(BaseModel):
    """
    Attributes of product that need to
    info about Specific Flags
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

    # ----------- Validators --------
    @model_validator(mode='after')
    def is_fragile_sctackable(self) -> 'HandlingAttributes':
        """
        If is_fragile is True: stackable must be False
        cause fragile products cant be stackable
        """
        if self.is_fragile and self.is_stackable:
            raise ValueError('Fragile product can\'t be stackable.')
        return self

    @model_validator(mode='after')
    def recommendations_validator(self) -> 'HandlingAttributes':
        """Recommendations for handling type products"""
        # For Odor sensitive products recommend ventilation
        if self.is_odor_sensitive and not self.requires_ventilation:
            print('Recomendation: For Odor sensitive products recommends ventailation True')
        return self
