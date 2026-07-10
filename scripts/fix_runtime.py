import asyncio
from sqlalchemy import text
from app.deps import async_session_factory

async def fix_and_check():
    async with async_session_factory() as db:
        # 1. Check task table columns
        r = await db.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'tasks' ORDER BY ordinal_position"
        ))
        cols = [row[0] for row in r.fetchall()]
        print("Task columns:", cols)

        # 2. Check recent tasks
        r3 = await db.execute(text(
            "SELECT id, title, status FROM tasks ORDER BY created_at DESC LIMIT 5"
        ))
        tasks = r3.fetchall()
        print(f"\nRecent tasks ({len(tasks)}):")
        for t in tasks:
            print(f"  {t[0]} | {t[1][:60]} | status={t[2]}")

        # 3. Switch runtime_mode from claw_code to claude_max
        print("\n--- Switching runtime_mode to claude_max ---")
        await db.execute(text(
            "UPDATE workforces SET runtime_mode = 'claude_max' WHERE name = 'NAVAIA Business'"
        ))
        await db.commit()
        print("Done.")

        # 4. Verify
        r4 = await db.execute(text(
            "SELECT id, name, runtime_mode FROM workforces WHERE name = 'NAVAIA Business'"
        ))
        verify = r4.fetchone()
        print(f"Verified: {verify[1]} | runtime_mode={verify[2]}")

        # 5. Check agent model names
        r5 = await db.execute(text(
            "SELECT name, role, model_name FROM agents WHERE workforce_id = :wfid"
        ), {"wfid": str(verify[0])})
        print("\nAgent models:")
        for a in r5.fetchall():
            print(f"  {a[0]} | {a[1]} | model={a[2]}")

asyncio.run(fix_and_check())
