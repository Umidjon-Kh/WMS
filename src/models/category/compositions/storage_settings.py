from pydantic import BaseModel, ConfigDict, Field, model_validator
from warnings import warn
from typing import Optional, Annotated
from uuid import UUID
from ..enums import PutawayStrategy, ReplenishmentMethod


class CtgStorageSettings(BaseModel):
    """
    Storage placement and replenishment settings for the product category.

    These settings determine how products in this category should be stored
    in the warehouse (which zones, putaway strategy) and how they should be
    replenished (by pallet, case, etc.).
    """

    model_config = ConfigDict(
        slots=True,
        use_enum_values=True,  # use enum values instead of keys in serialization
        validate_assignment=True,
    )  # type: ignore

    # References to zones (future models)
    default_storage_zone_id: Annotated[
        Optional[UUID], Field(description='Default storage zone ID (where products are kept)')
    ] = None

    default_picking_zone_id: Annotated[
        Optional[UUID], Field(description='Default picking zone ID (where products are picked from)')
    ] = None

    # Storage strategy
    putaway_strategy: Annotated[
        Optional[PutawayStrategy], Field(description='Strategy for putting away products (FIFO, FEFO, LIFO, etc.)')
    ] = None

    # Replenishment method
    replenishment_method: Annotated[
        Optional[ReplenishmentMethod], Field(description='How to replenish the picking zone (pallet, case, each, bulk)')
    ] = None

    # --------- Validators -----------
    @model_validator(mode='after')
    def validate_zones_consistency(self) -> 'CtgStorageSettings':
        """Validating zones consistensy"""
        if self.default_picking_zone_id and not self.default_storage_zone_id:
            warn('Picking zone is set but storage zone is not. This might cause issues during putaway.', UserWarning)
        if self.putaway_strategy and not self.default_storage_zone_id:
            warn(
                f'Putaway strategy "{self.putaway_strategy.value}" is set'
                ' but no storage zone defined. Storage zone is recommended.',
                UserWarning,
            )
        return self
