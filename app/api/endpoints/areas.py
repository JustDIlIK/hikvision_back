from fastapi import APIRouter, Depends

from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.schemas.area import SArea

router = APIRouter(prefix="/areas", tags=["Объекты и устройства"])


@router.post("/")
async def get_areas(area_data: SArea, token=Depends(get_token)):

    area_data = area_data.dict()

    data = await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/resource/v1/areas/doors/get",
        token=token,
        data={**area_data},
    )
    data = data["data"]["door"]
    devices = []

    for device in data:
        dev_info = device.pop("device")["devInfo"]
        dev_info.pop("category")
        dev_info.pop("streamSecretKey")

        device["device"] = dev_info
        devices.append(device)

    return devices
