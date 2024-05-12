from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError, RequestError

from app.core.config import settings


async def get_token():

    if not settings.CURRENT_TOKEN == "":
        return settings.CURRENT_TOKEN

    token_url = f"{settings.HIKVISION_URL}/api/hccgw/platform/v1/token/get"

    data = {
        "appKey": "zmgty84ni29u7vlhd2we5iieo2oafyiq",
        "secretKey": "khl15eqnah24syua3pbo2l8ixt4q4zhx",
    }

    async with AsyncClient() as client:
        try:
            response = await client.post(url=token_url, json=data)
            response.raise_for_status()
            data = response.json()

            settings.CURRENT_TOKEN = data["data"]["accessToken"]
            print("Taken new Token", settings.CURRENT_TOKEN)

            return settings.CURRENT_TOKEN
        except HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Ошибка с API: {e}",
            )
        except RequestError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка с сервером API: {e}")

