from pydantic import Field
from typing import Annotated, Optional


# Validation Constants
NAME_VALID = Annotated[str, Field(min_length=1, max_length=50, json_schema_extra={'strip_whitespace': True})]
DES_VALID = Annotated[Optional[str], Field(max_length=300)]
