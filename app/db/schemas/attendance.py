from pydantic import BaseModel
from typing_extensions import List


class SAttendance(BaseModel):
    beginTime: str = "2024-05-01T00:00:00+05:00"
    endTime: str = "2024-05-31T23:59:59+05:00"
    personName: str = ""
    personCode: str = ""
    personGroupIds: List[str] = []


class SAttendanceRecordCriteria(BaseModel):
    beginTime: str = "2024-05-01T00:00:00+05:00"
    endTime: str = "2024-05-31T00:00:00+05:00"
    eventTypes: str = "110013"
    elementIDs: str = "1d9196f3aa524e9896c951ed21b83b5b"


class SAttendanceRecord(BaseModel):
    pageIndex: int = 1
    pageSize: int = 200
    searchCriteria: SAttendanceRecordCriteria


class SRecordCertificate(BaseModel):
    recordGuid: str
    elementId: str
    areaId: str
    areaName: str
    deviceId: str
    deviceName: str
    snapPicUrl: str
    snapPicUrl2: str = None
    occurTime: str
    id: str
    fullPath: str
    firstName: str
    lastName: str
    personCode: str
    phoneNum: str
    photoUrl: str
    time: str
    date: str
    time_end: str = None
