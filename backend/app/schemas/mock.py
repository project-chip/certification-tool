from pydantic import BaseModel


class Mock(BaseModel):
    datetime: str
    device: str
    sPercent: str
    passCount: int
    failCount: int
