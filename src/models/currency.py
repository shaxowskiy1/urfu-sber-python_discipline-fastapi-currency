from dataclasses import dataclass
from typing import Optional


@dataclass
class Currency:
    id: Optional[int] = None
    code: Optional[str] = None
    fullname: Optional[str] = None
    sign: Optional[str] = None

    def __str__(self):
        return f"Currency{{id={self.id}, code='{self.code}', fullname='{self.fullname}', sign='{self.sign}'}}"

