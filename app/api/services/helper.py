from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError
from starlette.responses import JSONResponse

from app.api.dependencies.token import get_token
from app.api.responses.persons import Person_errors
from app.core.config import settings
from app.db.cache import attendance_cache
from app.logs.logger import get_logger

logger = get_logger(__name__)


async def hik_requests_helper(url, **kwargs):

    logger.info(f"Вызов метода\nurl={url}\nkwargs={kwargs}")

    async with AsyncClient() as client:
        try:
            response = await client.post(
                url=url, headers={"Token": kwargs["token"]}, json=kwargs["data"]
            )

            response.raise_for_status()
            logger.info(f"Данные получены с метода")
            data = response.json()
            if data["errorCode"] in ["OPEN000006", "OPEN000007"]:
                logger.warning(f"Токент устарел")
                await get_token()
                return await hik_requests_helper(
                    url, token=settings.CURRENT_TOKEN, data=kwargs["data"]
                )
            elif data["errorCode"] != "0":
                logger.exception(f"Ошибка -{data['errorCode']}- {data['message']}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Ошибка -{data['errorCode']}- {data['message']}.",
                )
            return data
        except HTTPStatusError as e:

            logger.exception(
                f"Ошибка при данных с Hikvision\n{e}\nСтатус кода: {e.response.status_code}"
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "detail": f"Ошибка -{e.response.status_code}- {e}. Совет: {Person_errors[e.response.status_code]}"
                },
            )
        except RequestError as e:

            attendance_cache.cache = {}
            attendance_cache.date_status = {}

            logger.exception(f"Ошибка при данных с Hikvision\n{e}\nСтатус кода: {500}")

            raise HTTPException(status_code=500, detail=f"Ошибка с сервером API: {e}")
