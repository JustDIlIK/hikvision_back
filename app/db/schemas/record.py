from pydantic import BaseModel


class SRecord(BaseModel):
    elementIDs: str = "1d9196f3aa524e9896c951ed21b83b5b"
    eventTypes: str = "110013"
    object_id: str
