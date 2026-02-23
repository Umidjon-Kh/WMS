from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID, uuid4
from datetime import datetime
from typing import Annotated, Optional
from .constants import NAME_VALID, DES_VALID


class Category(BaseModel):
    """
    Model Vategory of Products, Supports Hierarchy from parent_id
    """

    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # ------- main fields -------
    id: UUID = Field(default_factory=uuid4, frozen=True)
    name: NAME_VALID
    parent_id: Annotated[Optional[UUID], Field(description='Perant Category ID')] = None
    description: DES_VALID
    created_at: datetime = Field(default_factory=datetime.now, description='Category creatin date')
    updated_at: datetime = Field(default_factory=datetime.now, description='Category las update date')

    # --------- Validators ---------
    # -------- Time-Stamps ---------
    @model_validator(mode='after')
    def check_timestamps(self) -> 'Category':
        """Validating timestamps of category"""
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cant be earlier than creation_at')
        return self
