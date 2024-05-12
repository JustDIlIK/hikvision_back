from fastapi import APIRouter, Depends

from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings

router = APIRouter(
    prefix="/groups",
    tags=["Группы"],
)


@router.get("/", summary="Получение всех групп")
async def get_groups(token=Depends(get_token), parent_group_id: str = ""):
    print("get_groups called")

    data = await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/person/v1/groups/search",
        token=token,
        data={"depthTraversal": True, "parentGroupId": parent_group_id},
    )

    return data
