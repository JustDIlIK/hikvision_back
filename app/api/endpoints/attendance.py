from io import BytesIO

from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.api.services.persons import find_max_min
from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.schemas.attendance import SAttendanceRecord, SRecordCertificate

import pandas as pd

router = APIRouter(prefix="/attendance", tags=["Расписание"])


@router.post("/", summary="Получение данных по посещаемости")
async def get_attendance_list(
    attendance_records: SAttendanceRecord, token=Depends(get_token)
):

    attendance_records = attendance_records.dict()
    result_data = {}
    page_index = attendance_records["pageIndex"]

    while True:
        data = await hik_requests_helper(
            url=f"{settings.HIKVISION_URL}/api/hccgw/acs/v1/event/certificaterecords/search",
            token=token,
            data={
                "pageIndex": page_index,
                "pageSize": attendance_records["pageSize"],
                **attendance_records,
            },
        )

        for result in data["data"]["recordList"]:
            snap_pic = result.pop("acsSnapPicList")

            if len(snap_pic) == 0:
                continue

            snap_pic = snap_pic[0]["snapPicUrl"]

            person_info = result.pop("personInfo")

            person_id = person_info["id"]
            person_info = person_info["baseInfo"]
            person_info.update({"id": person_id, "snapPicUrl": snap_pic})
            date, time = result["deviceTime"].split("T")
            person = SRecordCertificate(
                **{**person_info, **result, "time": time.split("+")[0], "date": date}
            )

            if person_id == "":
                continue

            if person.photoUrl == "":
                person.photoUrl = "Убран с базы"

            if date in result_data:

                if person_id in result_data[date]:
                    result_data[date][person_id].append(person)
                else:
                    result_data[date][person_id] = [person]
            else:
                result_data[date] = {person_id: [person]}

        if data["data"]["totalNum"] < page_index * attendance_records["pageSize"]:
            break
        page_index += 1

    # Ищем уникальные (First and Last)

    persons_list = {}

    for date, persons in result_data.items():
        for person_id, person in persons.items():
            person_data = await find_max_min(person)

            if date in persons_list:
                persons_list[date].append(person_data)
            else:
                persons_list[date] = [person_data]

    return persons_list


@router.post("/file/", summary="Получение данных по посещаемости (файл)")
async def get_attendance_file(
    attendance_records: SAttendanceRecord, token=Depends(get_token)
):
    data = await get_attendance_list(attendance_records, token)
    persons_list = []

    for date, persons in data.items():
        for person in persons:
            persons_list.append(person.model_dump())

    df = pd.DataFrame(persons_list)

    first_date = persons_list[-1]["date"]
    second_date = persons_list[0]["date"]

    df.drop(
        [
            "recordGuid",
            "elementId",
            "areaId",
            "deviceId",
            "occurTime",
            "id",
            "personCode",
            "areaName",
            "deviceName",
        ],
        axis=1,
        inplace=True,
    )

    new_order = [
        "firstName",
        "lastName",
        "fullPath",
        "date",
        "time",
        "time_end",
        "phoneNum",
        "photoUrl",
        "snapPicUrl",
        "snapPicUrl2",
    ]

    df = df[new_order]

    translations = {
        "firstName": "ФИО",
        "lastName": "Должность",
        "fullPath": "Объект",
        "date": "Дата",
        "time": "Время входа",
        "time_end": "Время выхода",
        "phoneNum": "Номер телефона",
        "photoUrl": "Изображение",
        "snapPicUrl": "Отметился (Вход)",
        "snapPicUrl2": "Отметился (Выход)",
    }

    df = df.rename(columns=translations)

    df["Номер"] = range(1, len(df) + 1)

    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Расписание", index=False)

    output.seek(0)

    headers = {
        f"Content-Disposition": f"attachment; filename={first_date}-{second_date}.xlsx; "
    }
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
