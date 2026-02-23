from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated, Optional
from uuid import UUID, uuid4
from ..enums import PutawayStrategy, ReplenishmentMethod


class CtgStorageSettings(BaseModel):
    """
    Placement and replenishment settings for the product category.
    They determine how products in this category should be stored in the warehouse
    and which replenishment method should be used.
    """
