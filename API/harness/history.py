import json
import os

class AgentHistory:
    """
    מחלקה לניהול היסטוריית השיחה של הסוכן.
    שומרת את רצף ההודעות (משתמש, עוזר, כלים, מערכת) בזיכרון ובדיסק בצורה אמינה.
    """
    def __init__(self, system_prompt: str = "", storage_file: str = "history_log.json"):
        self.storage_file = storage_file
        self.system_prompt = system_prompt
        self.messages = []
        
        # טעינת ההיסטוריה מהדיסק קודם לכן
        if os.path.exists(self.storage_file):
            self._load_from_disk()
            
        # וידוא קיומה של הודעת המערכת בהיסטוריה אם הוגדרה ואינה קיימת עדיין
        if system_prompt and not any(m.get("role") == "system" for m in self.messages):
            self.messages.insert(0, {
                "role": "system",
                "content": system_prompt
            })
            self._save_to_disk()

    def _load_from_disk(self):
        """טעינת ההיסטוריה מקובץ בדיסק אם הוא קיים"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.messages = data
            except Exception as e:
                print(f"[API/harness/history.py] שגיאה בטעינת היסטוריה: {e}")

    def _save_to_disk(self):
        """שמירת ההיסטוריה העדכנית לקובץ בדיסק"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[API/harness/history.py] שגיאה בשמירת היסטוריה: {e}")

    def add_message(self, message: dict):
        """הוספת הודעה כללית (כולל קריאות כלים ותשובות) להיסטוריה ושמירה בדיסק"""
        self.messages.append(message)
        self._save_to_disk()

    def add_user_message(self, content: str):
        """הוספת הודעת משתמש להיסטוריה ושמירה בדיסק"""
        print("[API/harness/history.py] מוסיף הודעת משתמש להיסטוריה.")
        self.add_message({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content: str):
        """הוספת תשובת הסוכן להיסטוריה ושמירה בדיסק"""
        print("[API/harness/history.py] מוסיף הודעת עוזר להיסטוריה.")
        self.add_message({
            "role": "assistant",
            "content": content
        })

    def add_tool_message(self, tool_call_id: str, tool_name: str, content: str):
        """הוספת תוצאת כלי להיסטוריה ושמירה בדיסק"""
        print(f"[API/harness/history.py] מוסיף תוצאת כלי ({tool_name}) להיסטוריה.")
        self.add_message({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": content
        })

    def get_messages(self):
        """קבלת כל היסטוריית השיחה הנוכחית"""
        return self.messages

    def clear(self):
        """איפוס ההיסטוריה והשארת הודעת המערכת בלבד"""
        print("[API/harness/history.py] מאפס את ההיסטוריה.")
        self.messages = []
        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        self._save_to_disk()