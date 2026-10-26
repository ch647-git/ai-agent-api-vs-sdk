import hashlib
import json

class AgentCache:
    """
    מחלקת מטמון (Cache) לשמירת תגובות קודמות של המודל,
    כדי להימנע מקריאות מיותרות ל-API עבור אותם נתונים או שאילתות.
    """
    def __init__(self):
        print("[API/harness/caching.py] מאתחל את מודול המטמון (Cache)...")
        self.cache = {}

    def _generate_key(self, data) -> str:
        """יצירת מפתח ייחודי (Hash) עבור נתוני הבקשה"""
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def get(self, query_data):
        """שליפת תשובה מהמטמון אם קיימת"""
        key = self._generate_key(query_data)
        if key in self.cache:
            print("[API/harness/caching.py] נמצאה התאמה במטמון (Cache hit).")
            return self.cache.get(key)
        return None

    def set(self, query_data, response):
        """שמירת תשובה חדשה במטמון"""
        print("[API/harness/caching.py] שומר תשובה חדשה במטמון.")
        key = self._generate_key(query_data)
        self.cache[key] = response

    def clear(self):
        """ניקוי המטמון"""
        print("[API/harness/caching.py] מאפס ומנקה את המטמון.")
        self.cache.clear()