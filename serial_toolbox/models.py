from pydantic import BaseModel
from typing import Literal

class Config(BaseModel):
    baudrate: int
    timeout: float
    format: Literal['STR', 'HEX']
    plotting: bool
    print_numbers: bool
    window_size: int