import os
import sys
import json
import subprocess

def agent_scraping_skill(url: str, selectors: dict = {}) -> dict:
    """
    Safe, isolated scraping tool executed cleanly within your existing venv.
    Executes the micro_scraper.py using the exact same venv Python executable.
    """
    # Force the script to execute using your CURRENT venv's python binary
    venv_python = sys.executable 
    
    # Path to your micro-scraper script
    script_path = os.path.join(os.path.dirname(__file__), "micro_scraper.py")
    
    selectors_str = json.dumps(selectors)
    
    try:
        # Run as a separate operating system process capped by a hard timeout
        process = subprocess.run(
            [venv_python, script_path, url, selectors_str],
            capture_output=True,
            text=True,
            timeout=45  # Safety boundary: prevents any infinite hangs or freezes
        )
        
        # Parse the clean JSON stdout returned by crawl4ai
        if process.stdout:
            try:
                return json.loads(process.stdout)
            except json.JSONDecodeError:
                return {"status": "error", "message": f"Failed to parse JSON. Stdout: {process.stdout}"}
        else:
            return {"status": "error", "message": f"Scraper crashed: {process.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Scraping task timed out. Process killed safely."}
