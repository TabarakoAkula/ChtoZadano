import asyncio
import json
import os

import dotenv
import requests

dotenv.load_dotenv()

DOCKER_URL = os.getenv("DOCKER_URL")


async def check_for_admin(telegram_id):
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/is_user_admin/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
        },
    )
    response_data = json.loads(response.json())
    admin = response_data["is_admin"]
    superuser = response_data["is_superuser"]
    if not admin and not superuser:
        return "user"
    if admin and not superuser:
        return "admin"
    if superuser:
        return "superuser"
    return "Undefined"


async def delete_become_admin(telegram_id):
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/become_admin_delete_user/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
        },
    )
    return
