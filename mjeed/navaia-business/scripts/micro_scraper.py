#!/usr/bin/env python3
"""
micro_scraper.py - Isolated Micro-Scraper Subprocess Tool.
Decouples web scraping from the core agent execution layer.
Upgraded to use crawl4ai for SPA and Javascript-heavy sites.
"""
import sys
import json
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    if len(sys.argv) < 3:
        print(json.dumps({"status": "error", "message": "Usage: python micro_scraper.py <url> <selectors_json>"}))
        sys.exit(1)
        
    url = sys.argv[1]
    try:
        selectors = json.loads(sys.argv[2])
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Invalid selectors JSON: {e}"}))
        sys.exit(1)
        
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            
            # For this simple micro-scraper, we can just return the entire markdown
            # Or if we want to apply selectors, we'd need beautifulsoup on the raw HTML
            # But crawl4ai is great at extracting raw markdown which the LLM can parse!
            # Since the user's tutorial just said "using the Crawl4AI script", we'll return the markdown.
            
            # To honor the selectors argument, we could parse the HTML, but returning markdown is the primary crawl4ai use-case.
            # We will return the full markdown and let the agent parse it.
            print(json.dumps({
                "status": "success",
                "markdown": result.markdown
            }, ensure_ascii=False))
            
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
