from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError

from app.core.config import settings
from app.logs.logger import get_logger

logger = get_logger(__name__)


async def get_token():
    logger.info(f"Вызов метода get_token()")

    if not settings.CURRENT_TOKEN == "":
        logger.info(f"Использован токен '{settings.CURRENT_TOKEN}' с экша")
        return settings.CURRENT_TOKEN

    token_url = f"{settings.HIKVISION_URL}/api/hccgw/platform/v1/token/get"

    data = {
        "appKey": settings.APP_KEY,
        "secretKey": settings.SECRET_KEY,
    }

    async with AsyncClient() as client:
        try:

            response = await client.post(url=token_url, json=data)
            response.raise_for_status()
            data = response.json()

            settings.CURRENT_TOKEN = data["data"]["accessToken"]

            logger.info(f"Получен новый токен '{settings.CURRENT_TOKEN}'")

            return settings.CURRENT_TOKEN
        except HTTPStatusError as e:
            logger.exception(f"Ошибка при получение токена\n{e}\nСтатус кода: {e.response.status_code}")

            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Ошибка с API: {e}",
            )
        except RequestError as e:
            logger.exception(f"Ошибка при получение токена\n{e}\nСтатус кода: {500}")
            raise HTTPException(status_code=500, detail=f"Ошибка с сервером API: {e}")

