import os
import json
from groq import Groq
from API.harness.tools import TOOLS_SCHEMA, execute_tool

# ניסיון ייבוא של מעקב הטוקנים אם קיים בפרויקט
try:
    from API.harness.tokens import token_tracker
except ImportError:
    token_tracker = None

_client = None

def get_groq_client():
    """אתחול עצל של לקוח ה־Groq המונע קריסה בזמן ייבוא מודולים ללא מפתח API"""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY", "mock_key_for_offline_tests")
        _client = Groq(api_key=api_key)
    return _client

def run_agent_loop(messages, model_name="llama-3.3-70b-versatile", max_rounds: int = 8):
    """
    מריץ את לולאת הסוכן המרכזית בצורה איטרטיבית:
    1. שולח את השיחה למודל יחד עם רשימת הכלים (TOOLS_SCHEMA).
    2. בודק האם המודל ביקש להפעיל כלים.
    3. מעדכן את מעקב הטוקנים מתשובת המודל.
    4. מריץ את הכלים, מטפל בשגיאות ומחזיר את התוצאות להיסטוריה.
    """
    print(f"[API/harness/loop.py] שולח בקשה למודל {model_name}...")
    
    client = get_groq_client()
    
    for round_number in range(max_rounds):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
        except Exception as exc:
            print(f"[API/harness/loop.py] שגיאת תקשורת מול ה-API: {exc}")
            return "אירעה שגיאה בתקשורת עם המודל."
        
        # עדכון מדדי טוקנים מתשובת המודל אם קיים מעקב
        if hasattr(response, 'usage') and response.usage:
            if token_tracker:
                if hasattr(token_tracker, 'add_usage'):
                    token_tracker.add_usage(response.usage)
                elif hasattr(token_tracker, 'update'):
                    token_tracker.update(response.usage)
        
        response_message = response.choices[0].message
        
        # שמירת הודעת המודל (כולל דרישות הכלים או הטקסט) בהיסטוריה
        messages.append(response_message.model_dump(exclude_none=True))
        
        # אם המודל לא ביקש להפעיל כלים, הגענו לתשובה הסופית
        if not response_message.tool_calls:
            print(f"[API/harness/loop.py] התור הסתיים בהצלחה.")
            return response_message.content or ""
            
        print(f"[API/harness/loop.py] סבב כלים {round_number + 1}/{max_rounds}: המודל ביקש להפעיל כלים.")
        
        # מעבר על כל הכלים שהמודל ביקש להפעיל בסבב הנוכחי
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            
            # פענוח והבטחת תקינות ארגומנטים ללא החלפה שקטה בשגיאה
            try:
                tool_args = json.loads(tool_call.function.arguments or "{}")
                if not isinstance(tool_args, dict):
                    raise ValueError("Tool arguments must resolve to a dictionary.")
            except (json.JSONDecodeError, ValueError) as err:
                print(f"[API/harness/loop.py] שגיאה בפענוח ארגומנטים לכלי {tool_name}: {err}")
                tool_result = json.dumps({
                    "error": f"Invalid arguments format: {str(err)}",
                    "is_error": True
                }, ensure_ascii=False)
            else:
                # הפעלת הכלי בפועל דרך הקובץ tools.py עם הגנת שגיאות
                try:
                    tool_result = execute_tool(tool_name, tool_args)
                except Exception as tool_exc:
                    print(f"[API/harness/loop.py] שגיאה בהרצת הכלי {tool_name}: {tool_exc}")
                    tool_result = json.dumps({
                        "error": str(tool_exc),
                        "is_error": True
                    }, ensure_ascii=False)
            
            print(f"[API/harness/loop.py] תוצאת הכלי {tool_name}: {tool_result}")
            
            # הוספת תוצאת הכלי בחזרה להיסטוריית השיחה עבור המודל
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })

    print(f"[API/harness/loop.py] הושגה מגבלת סבבי הכלים המקסימלית.")
    return "הסוכן הגיע למגבלת סבבי הכלים לפני השלמת הבקשה."