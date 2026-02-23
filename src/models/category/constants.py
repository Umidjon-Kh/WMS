from pydantic import Field
from typing import Annotated, Optional


# Validation Constants
SKU_VALID = Annotated[
    str, Field(pattern=r'^[A-Z0-9]{3,20}$', min_length=1, max_length=50, description='Unique SKU (Stock Keeping Unit)')
]
NAME_VALID = Annotated[str, Field(min_length=1, max_length=50, json_schema_extra={'strip_whitespace': True})]
DES_VALID = Annotated[Optional[str], Field(max_length=300)]
POSITIVE_INT = Annotated[int, Field(ge=0)]
POSITIVE_F = Annotated[float, Field(ge=0)]
URL_STR = Annotated[str, Field(max_length=500)]
PATH_URL = Annotated[str, Field(max_length=500)]
