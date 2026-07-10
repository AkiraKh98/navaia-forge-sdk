import sys, io, re, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from navaia_forge import NavaiaForgeClient

local_key = open('C:/Users/aabbo/navaia-forge-sdk/_local_api_key.txt').read().strip()
client = NavaiaForgeClient(api_key=local_key, base_url='http://localhost:8001')

task_id = '69795c7f-9c17-456b-a0df-2093c4a15868'

# Poll task status
for i in range(60):
    try:
        task = client.tasks.get(task_id=task_id)
        status = task.status
        print(f"[{i}] Status: {status}")
        
        if status in ('done', 'failed', 'cancelled'):
            print(f"\n=== TASK FINISHED: {status} ===")
            print(f"Result: {getattr(task, 'result', 'N/A')}")
            print(f"Error: {getattr(task, 'error', 'N/A')}")
            # Print full task
            print(f"\nFull task dump:")
            print(json.dumps(task.model_dump(), indent=2, default=str)[:3000])
            break
        
        if status == 'in_progress':
            # Check logs
            try:
                logs = client.tasks.logs(task_id=task_id)
                if logs:
                    for log in logs[-3:]:
                        print(f"  LOG: {str(getattr(log, 'message', log))[:200]}")
            except:
                pass
        
    except Exception as e:
        print(f"[{i}] Error: {e}")
    
    time.sleep(10)
