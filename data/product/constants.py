from pydantic import Field
from typing import Annotated, Optional

# Min Value Constants for sized type
HEAVY_MIN_KG = 50.0    # min weight for heavy size type
LIGH_MAX_KG = 10.0     # max weight for light size type
OVERSIZED_MIN_CM = 200.0   # min size for oversized size type
SMALL_PARTS_MAX_CM = 30.0   # max size for small parts size type


# Validation Constants
SKU_VALID = Annotated[str, Field(pattern=r'^[A-Z0-9]{3,20}$', min_length=1, max_length=50, description='Unique SKU (Stock Keeping Unit)')]
POSITIVE_F = Annotated[float, Field(ge=0)]
NAME_VALID = Annotated[str, Field(min_length=1, max_length=50, json_schema_extra={'strip_whitespace': True})]
DES_VALID = Annotated[Optional[str], Field(default=None, max_length=300)]