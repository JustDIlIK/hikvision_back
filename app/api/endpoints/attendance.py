import asyncio
from calendar import monthrange
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends
from starlette.responses import Response, JSONResponse

from app.api.endpoints.areas import get_areas
from app.api.services.persons import find_max_min
from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.cache import attendance_cache, attendance_file_cache
from app.db.schemas.area import SArea
from app.db.schemas.attendance import SAttendanceRecord, SRecordCertificate, SReportCard

import pandas as pd

router = APIRouter(prefix="/attendance", tags=["Расписание"])


@router.post("/", summary="Получение данных по посещаемости")
async def get_attendance_list(
    attendance_records: SAttendanceRecord, token=Depends(get_token)
):
    attendance_records = attendance_records.dict()
    result_data = {}
    page_index = 1
    print(attendance_records)
    while True:
        print(f"{page_index=}")

        data = await hik_requests_helper(
            url=f"{settings.HIKVISION_URL}/api/hccgw/acs/v1/event/certificaterecords/search",
            token=token,
            data={
                "pageIndex": page_index,
                "pageSize": 200,
                **attendance_records,
            },
        )

        print(f'{data["data"]["totalNum"]=}')
        print(f'{data["data"]["pageIndex"]=}')
        print(f'{data["data"]["pageSize"]=}')

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
        else:
            await asyncio.sleep(1.5)

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
    print("Collecting Records Finished")
    return persons_list


async def get_attendance_list_file(
    attendance_records: SAttendanceRecord, token: str, all_time: str
):

    data = await get_attendance_list(attendance_records, token)

    attendance_file_cache.cache[all_time] = data
    attendance_file_cache.date_status[all_time] = "Finished"


@router.post("/file/", summary="Получение данных по посещаемости (файл)")
async def get_attendance_file(
    attendance_records: SAttendanceRecord, token=Depends(get_token)
):
    print(attendance_records.searchCriteria.beginTime)
    all_time = str(
        attendance_records.searchCriteria.beginTime
        + attendance_records.searchCriteria.endTime
    )

    if (
        all_time in attendance_file_cache.cache
        and (datetime.now() - attendance_file_cache.lt).total_seconds() < 600
    ):
        data = attendance_file_cache.cache[all_time]
    elif all_time in attendance_file_cache.date_status:
        if attendance_file_cache.date_status[all_time] == "Progress":
            return JSONResponse(
                content=f"Данные еще не готовы!",
                status_code=206,
            )
    else:
        attendance_file_cache.date_status[all_time] = "Progress"
        asyncio.create_task(
            get_attendance_list_file(attendance_records, token, all_time)
        )
        attendance_file_cache.lt = datetime.now()
        return JSONResponse(content="Запрос принят на исполнение", status_code=201)

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
            "deviceName",
            "photoUrl",
            "snapPicUrl",
            "snapPicUrl2",
        ],
        axis=1,
        inplace=True,
    )

    new_order = [
        "firstName",
        "lastName",
        "fullPath",
        "areaName",
        "date",
        "time",
        "time_end",
        "phoneNum",
    ]

    df = df[new_order]
    df["areaName"] = df["areaName"].apply(lambda x: x.split(" - ")[1])

    translations = {
        "firstName": "ФИО",
        "lastName": "Должность",
        "fullPath": "Компания",
        "areaName": "Локация",
        "date": "Дата",
        "time": "Время входа",
        "time_end": "Время выхода",
        "phoneNum": "Номер телефона",
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


async def get_attendance_list_reports(month_data: SReportCard, token):
    area_data = SArea.parse_obj(
        {"pageIndex": 1, "pageSize": 500, "filter": {"includeSubArea": 1}}
    )

    areas = await get_areas(area_data, token)
    persons_dict = {}

    for area in areas:
        data = await get_attendance_list(
            SAttendanceRecord.parse_obj(
                {
                    "pageSize": 200,
                    "searchCriteria": {
                        "beginTime": f"{month_data.date}-01T00:00:00+05:00",
                        "endTime": f"{month_data.date}-31T23:59:59+05:00",
                        "eventTypes": "110013",
                        "elementIDs": area["id"],
                    },
                }
            ),
            token,
        )

        for persons in data.values():
            for person in persons:

                person = person.model_dump()
                if person["personCode"] in persons_dict:
                    persons_dict[person["personCode"]].append(person)
                else:
                    persons_dict[person["personCode"]] = [person]
    attendance_cache.cache[month_data.date] = persons_dict
    attendance_cache.date_status[month_data.date] = "Finish"


@router.post("/report-card", summary="Получение данных в виде табеля")
async def get_attendance_report_card(month_data: SReportCard, token=Depends(get_token)):
    persons_dict = {}
    if (
        month_data.date in attendance_cache.cache
        and (datetime.now() - attendance_cache.lt).total_seconds() < 600
    ):
        persons_dict = attendance_cache.cache[month_data.date]
    elif month_data.date in attendance_cache.date_status:
        if attendance_cache.date_status[month_data.date] == "Progress":
            return JSONResponse(
                content=f"Данные еще не готовы!",
                status_code=206,
            )
    else:
        attendance_cache.date_status[month_data.date] = "Progress"
        asyncio.create_task(get_attendance_list_reports(month_data, token))
        attendance_cache.lt = datetime.now()
        return JSONResponse(content="Запрос принят на исполнение", status_code=201)

    today = datetime.strptime(month_data.date, "%Y-%m")

    days = list(range(1, monthrange(today.year, today.month)[1] + 1))
    df = pd.DataFrame(
        columns=[
            "firstName",
            "lastName",
            "fullPath",
            "areaName",
            "time",
            "time_end",
            *days,
            "worked",
            "days",
        ]
    )

    for i, (key, value) in enumerate(persons_dict.items()):
        person_series = pd.Series()
        days_series = pd.Series(data=[0] * len(days), index=days)

        person_series["firstName"] = value[0]["firstName"]
        person_series["lastName"] = value[0]["lastName"]
        person_series["fullPath"] = value[0]["fullPath"]

        person_series["areaName"] = value[0]["areaName"].split(" - ")[1]

        person_series = pd.concat([person_series, days_series])
        person_series["worked"] = 0
        person_series["days"] = 0
        sum_hours = 0
        sum_days = 0

        for index, person in enumerate(value):
            current_day = int(person["date"].split("-")[2])

            if person["time_end"] != "None":

                time = datetime.strptime(person["time"], "%H:%M:%S")

                if time.hour < 9 and person_series["areaName"] == "Офис":
                    time = time.replace(hour=9)

                time_end = datetime.strptime(person["time_end"], "%H:%M:%S")

                duration = round(((time_end - time).total_seconds() / 3600), 1)

                if duration > 8:
                    duration = 8
                elif duration == 0:
                    sum_days -= 1
                elif duration < 0:
                    duration = 1.5

                sum_hours += duration

                person_series[current_day] += duration

            else:
                person_series[current_day] += 1.5
                sum_hours += 1.5

            sum_days += 1

        person_series["worked"] = sum_hours
        person_series["days"] = sum_days

        df = df._append(person_series, ignore_index=True)

    df.index = df.index + 1
    df.drop(
        ["time", "time_end"],
        axis=1,
        inplace=True,
    )
    df = df.sort_values(by=["areaName", "fullPath", "lastName", "firstName"])
    translations = {
        "firstName": "ФИО",
        "lastName": "Должность",
        "fullPath": "Компания",
        "areaName": "Локация",
        "worked": "Кол-во часов",
        "days": "Кол-во дней",
    }
    df = df.rename(columns=translations)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Расписание", index=False)

    output.seek(0)

    headers = {f"Content-Disposition": f"attachment; filename={month_data.date}.xlsx; "}

    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
