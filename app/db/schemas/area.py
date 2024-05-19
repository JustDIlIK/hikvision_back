from pydantic import BaseModel


class SAreaFilter(BaseModel):
    includeSubArea: int = 1


class SArea(BaseModel):
    pageIndex: int = 1
    pageSize: int = 500
    filter: SAreaFilter
