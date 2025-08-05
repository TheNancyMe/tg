import httpx
from config import API_URL

async def add_note(user_id: int, title: str, description: str | None, passcode: str | None = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/notes/", json={
            "user_id": user_id,
            "title": title,
            "description": description,
            "passcode": passcode
        })
        response.raise_for_status()
        return response.json()

async def list_notes(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/notes/{user_id}")
        response.raise_for_status()
        return response.json()

async def get_note(note_id: int, passcode: str | None = None):
    async with httpx.AsyncClient() as client:
        params = {"passcode": passcode} if passcode else {}
        response = await client.get(f"{API_URL}/note/{note_id}", params=params)
        if response.status_code == 403:
            raise PermissionError()
        response.raise_for_status()
        return response.json()

async def delete_note(note_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_URL}/notes/{note_id}")
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True
