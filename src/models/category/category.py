from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID, uuid4
from datetime import datetime
from typing import Annotated, Optional
from .constants import NAME_VALID, DES_VALID, POSITIVE_INT, PATH_URL, CODE_VALID


class Category(BaseModel):
    """
    Model Category of Products, Supports Hierarchy from parent_id
    """

    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # Gives enum.value instaed of enum.key
        validate_assignment=True,  # validates in setting value
    )  # type: ignore

    # ------- main fields -------
    id: UUID = Field(default_factory=uuid4, frozen=True)
    sku: CODE_VALID
    name: NAME_VALID
    parent_id: Annotated[Optional[UUID], Field(description='Perant Category ID')] = None
    description: DES_VALID
    created_at: datetime = Field(default_factory=datetime.now, description='Category creatin date')
    updated_at: datetime = Field(default_factory=datetime.now, description='Category las update date')

    # -------- status fields ------
    is_active: Annotated[bool, Field(description='Category is active')] = True
    is_deleted: Annotated[bool, Field(description='Category is deleted')] = False

    # -------- Hierarchy and sort -------
    level: Optional[POSITIVE_INT] = 0
    path: Optional[PATH_URL] = ''
    sort_order: Optional[POSITIVE_INT] = 0

    # -------- Compositions ----------

    # --------- Validators and Cross Validators ---------
    # -------- Time-Stamps ---------
    @model_validator(mode='after')
    def check_timestamps(self) -> 'Category':
        """Validating time-stamps of category"""
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cant be earlier than creation_at')
        return self
