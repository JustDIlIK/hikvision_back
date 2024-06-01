from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Body
from starlette.responses import JSONResponse

from app.api.dependencies.token import get_token
from app.api.responses.persons import Person_errors
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.cache import person_cache
from app.db.schemas.person import (
    SPersonPhotoAdding,
    SPersonAdding,
    SPersonPatching,
    SPersonDetail,
)

router = APIRouter(
    prefix="/persons",
    tags=["Пользователи"],
)


@router.get("/", summary="Получение всех пользователей")
async def get_all_persons(token=Depends(get_token)):
    if (
        not person_cache.need_update
        and (datetime.now() - person_cache.lt).total_seconds() <= 3600
    ):
        temp_data = [data for data in person_cache.cache.values()]
        return temp_data
    else:
        person_cache.cache.clear()
    persons = []
    page_index = 1

    while True:

        print(f"{page_index=}")

        data = await hik_requests_helper(
            f"{settings.HIKVISION_URL}/api/hccgw/person/v1/persons/list",
            token=token,
            data={"pageIndex": page_index, "pageSize": 100, "filter": {}},
        )

        page_index += 1
        person_list = data["data"]["personList"]

        for person in person_list:
            person_cache.cache[person["personInfo"]["personCode"]] = person

        persons.extend(person_list)

        if len(data["data"]["personList"]) == 0:
            break

    person_cache.need_update = False
    person_cache.lt = datetime.now()

    return persons


@router.post("/", summary="Добаление пользователя")
async def add_person(person: SPersonAdding, token=Depends(get_token)):

    person = person.dict()
    data = await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/person/v1/persons/add",
        token=token,
        data=person,
    )

    person_cache.need_update = True

    return data


@router.put("/", summary="Изменения данных пользователя")
async def updating_person(person: SPersonPatching, token=Depends(get_token)):

    person = person.dict()

    await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/person/v1/persons/update",
        token=token,
        data=person,
    )
    person_cache.need_update = True
    return JSONResponse(
        content={"detail": "Успешное изменение пользователя"}, status_code=201
    )


@router.delete("/", summary="Удаление пользователя")
async def delete_person(person: SPersonDetail, token=Depends(get_token)):
    person = person.dict()

    await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/person/v1/persons/delete",
        token=token,
        data=person,
    )
    person_cache.need_update = True
    return JSONResponse(
        content={"detail": "Успешное удаление пользователя"}, status_code=201
    )


@router.post("/detail/", summary="Получение конкретного пользователя")
async def get_person_detail(person: SPersonDetail, token=Depends(get_token)):
    person = person.dict()

    data = await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/person/v1/persons/get",
        token=token,
        data=person,
    )

    return data


@router.post("/photo/", summary="Вставка фото пользователя")
async def upload_photo(person_data: SPersonPhotoAdding, token=Depends(get_token)):
    person_data = person_data.dict()
    await hik_requests_helper(
        url=f"{settings.HIKVISION_URL}/api/hccgw/person/v1/persons/photo",
        token=token,
        data={
            "personId": person_data["personId"],
            "photoData": person_data["photoData"],
        },
    )
    person_cache.need_update = True
    return JSONResponse(content={"detail": "Фото добавлено"}, status_code=201)
