from typing import Optional

from pydantic import BaseModel


class CategorySchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
