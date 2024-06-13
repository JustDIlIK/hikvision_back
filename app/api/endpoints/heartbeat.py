from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.dependencies.token import get_token
from app.api.services.helper import hik_requests_helper
from app.core.config import settings
from app.db.models.records import Record
from app.db.repositories.record import RecordDAO
from app.db.schemas.attendance import SRecordCertificate
from app.db.schemas.record import SRecord
from app.logs.logger import get_logger

router = APIRouter(
    prefix="/heartbeat",
    tags=["Обновление данных"],
)

logger = get_logger(__name__)


@router.post("/")
async def heartbeat(record_data: SRecord, token=Depends(get_token)):

    record_data = record_data.dict()
    last_record = await RecordDAO.get_last(record_data["elementIDs"])

    logger.warning(f"{last_record.record_id=}")

    if not last_record:
        last_record = Record(record_id="")

    result_data = []

    persons_dict = {}

    page_index = 1
    is_stop = False
    first_record = None
    count = 0

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

        if not persons_record:
            break

        if len(persons_record) > 0 and first_record is None:
            first_record = persons_record[0]

        for person_record in persons_record:

            if (
                person_record["recordGuid"] == last_record.record_id
                or datetime.strptime(
                    person_record["deviceTime"].split("T")[0], "%Y-%m-%d"
                ).date()
                != datetime.now().date()
            ):
                logger.warning(f"Here")
                logger.warning(f"{count}")

                if count != 0:
                    await RecordDAO.add_record(
                        record_id=first_record["recordGuid"],
                        object_id=record_data["elementIDs"],
                    )

                is_stop = True

                break

            date, time = person_record["deviceTime"].split("T")
            person_info = person_record.pop("personInfo")
            snap_pic = person_record.pop("acsSnapPicList")

            if len(snap_pic) == 0:
                continue

            snap_pic = snap_pic[0]["snapPicUrl"]

            person_id = person_info["id"]
            person_info = person_info["baseInfo"]
            person_info.update({"id": person_id, "snapPicUrl": snap_pic})

            record_certificate = SRecordCertificate(
                **{
                    **person_info,
                    **person_record,
                    "time": time.split("+")[0],
                    "date": date,
                }
            )

            if person_info["personCode"] in persons_dict:
                persons_dict[person_info["personCode"]].append(record_certificate)
            elif person_info["personCode"] != "":
                persons_dict[person_info["personCode"]] = [record_certificate]
            count += 1

        page_index += 1

        if page_index * 200 > data["data"]["totalNum"] or is_stop:
            break

    for persons in persons_dict.values():

        first_record = persons[0]
        last_record = persons[-1]
        if first_record.time != last_record.time and (
            (
                datetime.strptime(first_record.time, "%H:%M:%S")
                - datetime.strptime(last_record.time, "%H:%M:%S")
            ).total_seconds()
            > 60
        ):
            result_data.extend([first_record, last_record])

    return persons_dict
