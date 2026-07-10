import asyncio
from sqlalchemy import text
from app.deps import async_session_factory

async def approve_task():
    async with async_session_factory() as db:
        # Check column type
        r = await db.execute(text(
            "SELECT data_type FROM information_schema.columns WHERE table_name='tasks' AND column_name='metadata_json'"
        ))
        print(f"metadata_json type: {r.fetchone()[0]}")

        # Approve: set status to PENDING and add approval response to metadata
        await db.execute(text(
            "UPDATE tasks SET status = 'PENDING', "
            "metadata_json = metadata_json::jsonb || '{\"approval_response\": \"Approved. Proceed with the plan. Use the Google Places API key and Twenty CRM token from environment variables. Execute all phases.\"}'::jsonb "
            "WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868' AND status = 'WAITING_PLAN'"
        ))
        await db.commit()
        print("Task approved and set to PENDING")

        # Verify
        r = await db.execute(text(
            "SELECT id, title, status, metadata_json FROM tasks WHERE id = '69795c7f-9c17-456b-a0df-2093c4a15868'"
        ))
        t = r.fetchone()
        print(f"Status: {t[2]}")
        print(f"Metadata: {t[3]}")

asyncio.run(approve_task())
