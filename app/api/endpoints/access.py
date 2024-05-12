from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.schemas.person import SPersonAccessAdding

router = APIRouter(
    prefix="/access",
    tags=["Группы доступа"],
)


@router.get("/", summary="Получение всех групп доступа")
async def get_access(token=Depends(get_token)):

    data = await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/acspm/v1/accesslevel/list",
        token=token,
        data={
            "accessLevelSearchRequest": {
                "pageIndex": 1,
                "pageSize": 100,
                "searchCriteria": {"accessLevelName": "", "associateResInfoList": []},
            }
        },
    )

    return data


@router.post("/", summary="Добавления пользователя к группам доступа")
async def add_person_to_access(
    person_data: SPersonAccessAdding, token=Depends(get_token)
):
    person_data = person_data.dict()
    await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/acspm/v1/accesslevel/person/add",
        token=token,
        data={
            "personList": [
                {
                    "personId": person_data["personId"],
                    "accessLevelIdList": person_data["accessLevelIdList"],
                }
            ]
        },
    )

    return JSONResponse(
        content={"detail": "Успешное добавление в группы доступа"}, status_code=201
    )


@router.delete("/", summary="Удаление пользователя с групп доступа")
async def delete_person_from_access(
    person_data: SPersonAccessAdding, delete: bool = False, token=Depends(get_token)
):
    person_data = person_data.dict()
    await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/acspm/v1/accesslevel/person/delete",
        token=token,
        data={
            "personList": [
                {
                    "personId": person_data["personId"],
                    "accessLevelIdList": person_data["accessLevelIdList"],
                    "deleteAll": delete,
                }
            ]
        },
    )
    return JSONResponse(
        content={"detail": "Успешное удаление с группы доступа"}, status_code=200
    )


@router.patch("/", summary="Изменение у пользователя групп доступа")
async def patch_person_access(
    person_data: SPersonAccessAdding, delete: bool = False, token=Depends(get_token)
):
    person_data = person_data.dict()
    data = await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/acspm/v1/accesslevel/person/modify",
        token=token,
        data={
            "personList": [
                {
                    "personId": person_data["personId"],
                    "accessLevelIdList": person_data["accessLevelIdList"],
                    "deleteAll": delete,
                }
            ]
        },
    )
    return JSONResponse(
        content={"detail": "Успешное изменение группы доступа"}, status_code=200
    )


@router.get(
    "/detail/{person_id}",
    summary="Получение информации по группам доступ у конкретного пользователя",
)
async def get_person_access_detail(person_id: str, token=Depends(get_token)):

    data = await hik_requests_helper(
        f"{settings.HIKVISION_URL}/api/hccgw/acspm/v1/maintain/overview/person/{person_id}/elementdetail",
        token=token,
        data={"returnSuccess": True},
    )

    return data
