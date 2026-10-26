import json
import os

class AgentMemory:
    """
    מחלקה לניהול זיכרון ארוך-טווח או זיכרון מותאם אישית של הסוכן,
    המאפשרת שמירה ושליפה של נתונים מתוך קובץ מקומי.
    """
    def __init__(self, memory_file: str = None):
        print("[API/harness/memory.py] מאתחל את מודול הזיכרון ארוך-הטווח...")
        if memory_file:
            self.memory_file = memory_file
        else:
            self.memory_file = os.path.join(os.path.dirname(__file__), "..", "memory_store.json")
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """יצירת קובץ הזיכרון אם אינו קיים"""
        if not os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"[API/harness/memory.py] שגיאה ביצירת קובץ הזיכרון: {e}")

    def load_memory(self) -> dict:
        """טעינת כל הנתונים מתוך קובץ הזיכרון"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[API/harness/memory.py] שגיאה בטעינת הזיכרון: {e}")
        return {}

    def save_memory(self, data: dict):
        """שמירת נתונים מעודכנים לקובץ הזיכרון"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[API/harness/memory.py] שגיאה בשמירת הזיכרון: {e}")

    def get(self, key: str, default=None):
        """שליפת ערך ספציפי מתוך הזיכרון לפי מפתח"""
        data = self.load_memory()
        value = data.get(key, default)
        print(f"[API/harness/memory.py] שולף מפתח '{key}' מהזיכרון.")
        return value

    def set(self, key: str, value):
        """שמירה או עדכון של ערך ספציפי בזיכרון"""
        data = self.load_memory()
        data[key] = value
        self.save_memory(data)
        print(f"[API/harness/memory.py] שומר מפתח '{key}' בזיכרון.")

    def clear(self):
        """איפוס מוחלט של הזיכרון ארוך הטווח"""
        if os.path.exists(self.memory_file):
            try:
                os.remove(self.memory_file)
            except Exception:
                pass
        # יצירת קובץ ריק מחדש לאחר המחיקה
        self._ensure_file_exists()
        print("[API/harness/memory.py] הזיכרון אופס בהצלחה.")