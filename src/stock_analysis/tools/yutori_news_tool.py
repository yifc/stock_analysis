from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests
import os
import json

class YutoriNewsToolSchema(BaseModel):
    """Input for YutoriNewsTool."""
    stock_ticker: str = Field(..., description="The stock ticker to scout for news (e.g., AAPL).")

class YutoriNewsTool(BaseTool):
    name: str = "Yutori News Scout"
    description: str = (
        "This tool uses the Yutori Scouting API to find real-time news and updates about a company. "
        "It will create a continuous scouting task if one doesn't exist and return the latest findings for the given stock."
    )
    args_schema: Type[BaseModel] = YutoriNewsToolSchema
    
    def _run(self, stock_ticker: str) -> str:
        api_key = os.environ.get('YUTORI_API_KEY')
        if not api_key:
            return "Error: YUTORI_API_KEY not found in environment variables."

        base_url = "https://api.yutori.com/v1/scouting/tasks"
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # 1. Check for existing scout
        try:
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()
            scouts = response.json().get("scouts", [])
        except Exception as e:
            return f"Error listing scouts: {str(e)}"

        target_query = f"News, product updates, and market sentiment for {stock_ticker}"
        scout_id = None

        for scout in scouts:
            if scout.get("query") == target_query:
                scout_id = scout.get("id")
                break
        
        # 2. Create scout if not exists
        if not scout_id:
            try:
                payload = {
                    "query": target_query,
                    "display_name": f"{stock_ticker} News Scout"
                }
                response = requests.post(base_url, headers=headers, json=payload)
                response.raise_for_status()
                scout_id = response.json().get("id")
            except Exception as e:
                return f"Error creating scout: {str(e)}"

        # 3. Get updates
        try:
            updates_url = f"{base_url}/{scout_id}/updates?page_size=5"
            response = requests.get(updates_url, headers=headers)
            if response.status_code == 404:
                return "Scout created. No updates available yet. Please check back later."
            response.raise_for_status()
            data = response.json()
            updates = data.get("updates", [])
            
            if not updates:
                return f"No news updates found yet for {stock_ticker}. The scout is active and looking."
            
            results = []
            for update in updates:
                content = update.get("content", "")
                timestamp = update.get("timestamp", "")
                citations = update.get("citations", [])
                links = [c.get("url") for c in citations if c.get("url")]
                
                results.append(f"Time: {timestamp}\nUpdate: {content}\nLinks: {', '.join(links)}\n---")
            
            return "\n".join(results)

        except Exception as e:
            return f"Error fetching updates: {str(e)}"
