from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Annotated
from warnings import warn
from ..enums import CycleCountFrequency, OrderFrequency
from ..constants import POSITIVE_F, POSITIVE_INT


class CtgPlanning(BaseModel):
    """
    Inventory planning parameters for the product category.

    These settings help automate stock level recommendations and cycle counting.
    """

    model_config = ConfigDict(
        slots=True,
        validate_assignment=True,
    )  # type: ignore

    # Stock level thresholds
    min_stock_level: Annotated[
        Optional[POSITIVE_F],
        Field(description='Minimum recommended stock level (total across all products in category)'),
    ] = None

    max_stock_level: Annotated[
        Optional[POSITIVE_F],
        Field(description='Maximum recommended stock level (total across all products in category)'),
    ] = None

    # Reorder and safety
    reorder_point: Annotated[
        Optional[POSITIVE_F],
        Field(description='Stock level at which a new order should be placed'),
    ] = None

    safety_stock: Annotated[
        Optional[POSITIVE_F],
        Field(description='Minimum safety stock to cover uncertainties'),
    ] = None

    # Order frequency
    order_frequency: Annotated[
        Optional[OrderFrequency],
        Field(description='How often orders should be placed for this category'),
    ] = None

    custom_order_interval_days: Annotated[
        Optional[POSITIVE_INT],
        Field(description='Number of days between orders when order_frequency is CUSTOM'),
    ] = None

    # Cycle counting frequency
    cycle_count_frequency: Annotated[
        Optional[CycleCountFrequency],
        Field(description='How often cycle counting should be performed for this category'),
    ] = None

    # Optional: custom interval in days if frequency is CUSTOM
    custom_count_interval_days: Annotated[
        Optional[POSITIVE_INT], Field(description='Number of days between cycle counts when frequency is CUSTOM')
    ] = None

    # ----------- Validators --------
    @model_validator(mode='after')
    def check_stock_levels(self) -> 'CtgPlanning':
        """If both min and max are provided, ensure min <= max."""
        if self.min_stock_level is not None and self.max_stock_level is not None:
            if self.min_stock_level > self.max_stock_level:
                raise ValueError('min_stock_level cannot be greater than max_stock_level')
        return self

    @model_validator(mode='after')
    def check_custom_interval(self) -> 'CtgPlanning':
        """If frequency is CUSTOM, then custom_count_interval_days must be provided."""
        if self.cycle_count_frequency == CycleCountFrequency.CUSTOM and self.custom_count_interval_days is None:
            raise ValueError('custom_count_interval_days is required when cycle_count_frequency is CUSTOM')
        return self

    @model_validator(mode='after')
    def check_reorder_and_safety(self) -> 'CtgPlanning':
        """If both reorder_point and safety_stock are provided, ensure reorder_point >= safety_stock."""
        if self.reorder_point is not None and self.safety_stock is not None:
            if self.reorder_point < self.safety_stock:
                warn('reorder_point is less than safety_stock. This may lead to frequent stockouts.', UserWarning)
        return self

    @model_validator(mode='after')
    def check_custom_order_interval(self) -> 'CtgPlanning':
        """If order_frequency is CUSTOM, then custom_order_interval_days must be provided."""
        if self.order_frequency == OrderFrequency.CUSTOM and self.custom_order_interval_days is None:
            raise ValueError('custom_order_interval_days is required when order_frequency is CUSTOM')
        return self
