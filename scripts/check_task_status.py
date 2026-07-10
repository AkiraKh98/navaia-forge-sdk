import asyncio
from sqlalchemy import text
from app.deps import async_session_factory

async def check():
    async with async_session_factory() as db:
        r = await db.execute(text(
            "SELECT id, title, status, result, metadata_json "
            "FROM tasks WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868'"
        ))
        t = r.fetchone()
        print(f"Status: {t[2]}")
        print(f"Result:\n{t[3]}")
        print(f"\nMetadata: {t[4]}")

asyncio.run(check())
