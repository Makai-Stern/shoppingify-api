from typing import Optional

from pydantic import BaseModel


class CartSchema(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = "Started"
    foods: Optional[list] = []
