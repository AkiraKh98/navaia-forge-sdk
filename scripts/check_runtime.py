import asyncio
from sqlalchemy import text
from app.deps import async_session_factory

async def check():
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id, name, runtime_mode FROM workforces"))
        rows = r.fetchall()
        print(f"Found {len(rows)} workforces")
        for row in rows:
            print(f"  {row[0]} | {row[1]} | {row[2]}")

asyncio.run(check())
