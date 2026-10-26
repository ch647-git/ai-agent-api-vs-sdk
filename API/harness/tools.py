import json
import sys
import os

# הוספת תיקיית השורש לנתיב כדי שנוכל לייבא מ-shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from shared.tools_def import (
    get_study_topics,
    update_task_status,
    check_external_schedule
)
from API.harness.memory import AgentMemory

memory_manager = AgentMemory()

def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    מקבל את שם הכלי והארגומנטים שהמודל ביקש להפעיל,
    מפעיל את הפונקציה המתאימה ומחזיר את התוצאה כמחרוזת.
    """
    print(f"[API/harness/tools.py] מפעיל כלי: {tool_name} עם ארגומנטים: {arguments}")
    
    try:
        if tool_name == "get_study_topics":
            result = get_study_topics()
            return json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result
            
        elif tool_name == "update_task_status":
            task_id = arguments.get("task_id")
            status = arguments.get("status")
            result = update_task_status(task_id, status)
            return json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result
            
        elif tool_name == "check_external_schedule":
            date = arguments.get("date", "")
            result = check_external_schedule(date)
            return json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result

        elif tool_name == "save_memory":
            key = arguments.get("key")
            value = arguments.get("value")
            if not key:
                return json.dumps({"error": "Missing key for memory save", "is_error": True}, ensure_ascii=False)
            memory_manager.set(key, value)
            return json.dumps({"status": "success", "message": f"Saved preference '{key}' successfully."}, ensure_ascii=False)

        elif tool_name == "get_memory":
            key = arguments.get("key")
            val = memory_manager.get(key)
            return json.dumps({key: val}, ensure_ascii=False)
            
        else:
            return json.dumps({"error": f"הכלי {tool_name} אינו מוכר במערכת", "is_error": True}, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({"error": f"שגיאה בהפעלת הכלי: {str(e)}", "is_error": True}, ensure_ascii=False)


# הגדרת סכמות הכלים עבור ה-API (Tool Definitions)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_study_topics",
            "description": "שליפת נושאי הלימוד, הקורס הפעיל ורשימת המשימות הנוכחית של הסטודנטית.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_status",
            "description": "עדכון סטטוס של משימה קיימת לפי מזהה המשימה והסטטוס החדש.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "מזהה המשימה (לדוגמה: 1 או 2)"
                    },
                    "status": {
                        "type": "string",
                        "description": "הסטטוס החדש (לדוגמה: 'completed', 'in_progress', 'pending')"
                    }
                },
                "required": ["task_id", "status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_external_schedule",
            "description": "בדיקת זמינות ולוח זמנים לתאריך מסוים.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "התאריך לבדיקה בפורמט YYYY-MM-DD"
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "שמירה או עדכון של העדפה או נתון בזיכרון ארוך הטווח (לשימוש בין סשנים).",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "שם המפתח או ההעדפה"
                    },
                    "value": {
                        "type": "string",
                        "description": "הערך לשמירה"
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory",
            "description": "שליפת נתון או העדפה מתוך הזיכרון ארוך הטווח לפי מפתח.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "מפתח הזיכרון לשליפה"
                    }
                },
                "required": ["key"]
            }
        }
    }
]