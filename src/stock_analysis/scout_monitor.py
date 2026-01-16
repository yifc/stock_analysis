import os
import time
import requests
import threading
from datetime import datetime

class ScoutMonitor:
    def __init__(self, stock_ticker, callback, poll_interval=60):
        self.stock_ticker = stock_ticker
        self.callback = callback
        self.poll_interval = poll_interval
        self.api_key = os.environ.get('YUTORI_API_KEY')
        self.base_url = "https://api.yutori.com/v1/scouting/tasks"
        self.scout_id = None
        self.seen_update_ids = set()
        self.running = False
        self._thread = None

    def _get_headers(self):
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _ensure_scout_exists(self):
        """Finds existing scout or creates a new one for the ticker."""
        if not self.api_key:
            print("Error: YUTORI_API_KEY not set.")
            return False

        headers = self._get_headers()
        target_query = f"News, product updates, and market sentiment for {self.stock_ticker}"

        # 1. Check existing
        try:
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            scouts = response.json().get("scouts", [])
            for scout in scouts:
                if scout.get("query") == target_query:
                    self.scout_id = scout.get("id")
                    print(f"Found existing scout: {self.scout_id}")
                    return True
        except Exception as e:
            print(f"Error checking scouts: {e}")
            return False

        # 2. Create if not exists
        try:
            payload = {
                "query": target_query,
                "display_name": f"{self.stock_ticker} News Scout"
            }
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            self.scout_id = response.json().get("id")
            print(f"Created new scout: {self.scout_id}")
            return True
        except Exception as e:
            print(f"Error creating scout: {e}")
            return False

    def _poll_loop(self):
        """Main polling loop running in a thread."""
        print(f"Starting monitor for {self.stock_ticker} with scout {self.scout_id}...")
        
        # Initial fetch to mark current updates as seen so we don't trigger immediately on old news
        self._fetch_updates(initial=True)
        
        while self.running:
            try:
                has_new = self._fetch_updates(initial=False)
                if has_new:
                    print(f"New updates detected for {self.stock_ticker}! Triggering analysis...")
                    self.callback(self.stock_ticker)
            except Exception as e:
                print(f"Error in poll loop: {e}")
            
            time.sleep(self.poll_interval)

    def _fetch_updates(self, initial=False):
        """Fetches updates and returns True if new ones are found."""
        try:
            url = f"{self.base_url}/{self.scout_id}/updates?page_size=10"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 404:
                return False
                
            response.raise_for_status()
            data = response.json()
            updates = data.get("updates", [])
            
            new_updates_found = False
            
            for update in updates:
                u_id = update.get("id") # Assuming updates have an ID, or we hash content
                # If no ID, we can try to use content hash or timestamp + content as ID. 
                # Inspecting Yutori tool response structure doesn't show ID, let's verify.
                # The tool just reads content. Let's assume we can use the content itself or timestamp as unique key if ID is missing.
                if not u_id:
                     # Fallback key
                    u_id = f"{update.get('timestamp')}_{update.get('content')[:20]}"
                
                if u_id not in self.seen_update_ids:
                    self.seen_update_ids.add(u_id)
                    if not initial:
                        new_updates_found = True
            
            return new_updates_found

        except Exception as e:
            print(f"Error fetching updates: {e}")
            return False

    def start(self):
        if not self._ensure_scout_exists():
            print("Failed to initialize scout. Monitor not started.")
            return

        self.running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
