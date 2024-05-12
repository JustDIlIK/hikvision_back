import json
from typing import List

from pydantic import BaseModel


class SPersonAccessAdding(BaseModel):
    personId: str
    accessLevelIdList: list


class SPersonAdding(BaseModel):
    groupId: str
    personCode: str
    firstName: str
    lastName: str
    gender: int = 2
    phone: str = ""
    description: str
    startDate: str = "2024-01-01T11:08:23+08:00"
    endDate: str = "2035-10-21T11:08:23+08:00"


class SPersonPhotoAdding(BaseModel):
    personId: str
    photoData: str


class SPersonPatching(BaseModel):
    groupId: str
    personId: str
    personCode: str
    firstName: str
    lastName: str
    gender: int = 2
    phone: str = ""
    description: str
    startDate: str = "2024-01-01T11:08:23+08:00"
    endDate: str = "2035-10-21T11:08:23+08:00"


class SPersonDetail(BaseModel):
    personId: str
