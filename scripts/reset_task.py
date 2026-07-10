import asyncio
from sqlalchemy import text
from app.deps import async_session_factory

async def reset_task():
    async with async_session_factory() as db:
        # Check valid enum values
        r = await db.execute(text(
            "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'taskstatus')"
        ))
        print("Valid TaskStatus enum values:", [row[0] for row in r.fetchall()])

        # Reset the failed lead-finding task to PENDING
        await db.execute(text(
            "UPDATE tasks SET status = 'PENDING', error = NULL, started_at = NULL, completed_at = NULL "
            "WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868'"
        ))
        await db.commit()
        print("Task reset to PENDING")

        # Verify
        r = await db.execute(text(
            "SELECT id, title, status FROM tasks WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868'"
        ))
        t = r.fetchone()
        print(f"Verified: {t[0]} | {t[1][:60]} | status={t[2]}")

asyncio.run(reset_task())
