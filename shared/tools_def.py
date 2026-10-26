import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def load_data():
    """טעינת הנתונים מקובץ ה-JSON המקומי"""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """שמירת הנתונים חזרה לקובץ"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_study_topics() -> str:
    """שליפת נושאי לימוד ומשימות מתוך הקבצים המקומיים"""
    data = load_data()
    return json.dumps({
        "active_course": data.get("active_course"),
        "tasks": data.get("tasks"),
        "study_topics": data.get("study_topics")
    }, ensure_ascii=False)

def update_task_status(task_id: int, status: str) -> str:
    """עדכון סטטוס משימה במערכת המקומית"""
    data = load_data()
    tasks = data.get("tasks", [])
    updated = False
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            updated = True
            break
    if updated:
        save_data(data)
        return json.dumps({"success": True, "message": f"משימה {task_id} עודכנה בהצלחה ל־{status}"}, ensure_ascii=False)
    return json.dumps({"success": False, "error": "משימה לא נמצאה"}, ensure_ascii=False)

def check_external_schedule(date: str) -> str:
    """
    בדיקת זמינות לוח זמנים לתאריך בפורמט YYYY-MM-DD.
    """
    print(f"[shared/tools_def.py] בדיקת לוח זמנים לתאריך: {date}")
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        is_weekend = parsed_date.weekday() >= 4
        
        status_text = "פנוי לפגישות ולימוד" if not is_weekend else "סוף שבוע - סגור לפעילות"
        
        result = {
            "requested_date": date,
            "available": not is_weekend,
            "status": status_text,
            "message": "התאריך נבדק בהצלחה."
        }
        return json.dumps(result, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({
            "error": f"פורמט תאריך שגוי, נדרש YYYY-MM-DD. פרטים: {str(e)}",
            "is_error": True
        }, ensure_ascii=False)