from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.models.records import Record
from app.db.repositories.record import RecordDAO
from app.db.schemas.attendance import SRecordCertificate
from app.db.schemas.record import SRecord

router = APIRouter(
    prefix="/heartbeat",
    tags=["Обновление данных"],
)


@router.post("/")
async def heartbeat(record_data: SRecord, token=Depends(get_token)):

    record_data = record_data.dict()
    last_record = await RecordDAO.get_last()

    if not last_record:
        last_record = Record(record_id="")

    result_data = []

    page_index = 1

    while True:
        data = await hik_requests_helper(
            url=f"{settings.HIKVISION_URL}/api/hccgw/acs/v1/event/certificaterecords/search",
            token=token,
            data={
                "pageIndex": page_index,
                "pageSize": 200,
                "searchCriteria": record_data,
            },
        )

        persons_record = data["data"]["recordList"]
        first_record = None

        if not persons_record:
            break

        if len(persons_record) > 0:
            first_record = persons_record[0]

        count = 0

        for person_record in persons_record:

            if (
                person_record["recordGuid"] == last_record.record_id
                or datetime.strptime(
                    person_record["deviceTime"].split("T")[0], "%Y-%m-%d"
                ).date()
                != datetime.now().date()
            ):
                if count != 0:
                    await RecordDAO.add_record(record_id=first_record["recordGuid"])
                break

            date, time = person_record["deviceTime"].split("T")
            person_info = person_record.pop("personInfo")
            snap_pic = person_record.pop("acsSnapPicList")[0]["snapPicUrl"]

            person_id = person_info["id"]
            person_info = person_info["baseInfo"]
            person_info.update({"id": person_id, "snapPicUrl": snap_pic})

            result_data.append(
                SRecordCertificate(
                    **{
                        **person_info,
                        **person_record,
                        "time": time.split("+")[0],
                        "date": date,
                    }
                )
            )

            count += 1

        if page_index * 200 > data["data"]["totalNum"]:
            break

    return result_data
