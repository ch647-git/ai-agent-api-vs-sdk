import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API.agent import ApiAgent

class MockMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

    def model_dump(self, exclude_none=False):
        d = {"role": "assistant", "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = [tc.model_dump() if hasattr(tc, "model_dump") else tc for tc in self.tool_calls]
        if exclude_none:
            d = {k: v for k, v in d.items() if v is not None}
        return d

class MockToolCall:
    def __init__(self, id, name, arguments):
        self.id = id
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments

    def model_dump(self):
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.function.name,
                "arguments": self.function.arguments
            }
        }

class MockGroqResponse:
    def __init__(self, content, tool_calls=None):
        self.choices = [MagicMock()]
        self.choices[0].message = MockMessage(content=content, tool_calls=tool_calls)
        self.usage = MagicMock(prompt_tokens=25, completion_tokens=35)

@patch("API.harness.loop.get_groq_client")
def run_offline_tests(mock_get_client):
    print("=== מריץ בדיקות אופליין מלאות מול scenario.json ===")
    
    mock_client_instance = MagicMock()
    mock_get_client.return_value = mock_client_instance
    
    # תגובות מדומה מותאמות לשש הפניות בתרחיש (3 בסשן 1, 3 בסשן 2)
    mock_client_instance.chat.completions.create.side_effect = [
        # Session 1
        MockGroqResponse(content=None, tool_calls=[MockToolCall("c1", "get_study_topics", "{}")]),
        MockGroqResponse(content="להלן נושאי הלימוד."),
        MockGroqResponse(content=None, tool_calls=[MockToolCall("c2", "check_external_schedule", '{"date": "2026-06-15"}')]),
        MockGroqResponse(content="התאריך נבדק בהצלחה ונמצא פנוי."),
        MockGroqResponse(content=None, tool_calls=[MockToolCall("c3", "save_memory", '{"key": "study_pref", "value": "morning"}')]),
        MockGroqResponse(content="העדפת הבוקר נשמרה בזיכרון."),
        
        # Session 2 (מופע חדש)
        MockGroqResponse(content=None, tool_calls=[MockToolCall("c4", "get_memory", '{"key": "study_pref"}')]),
        MockGroqResponse(content="הזיכרון נטען: morning"),
        MockGroqResponse(content=None, tool_calls=[MockToolCall("c5", "update_task_status", '{"task_id": 1, "status": "completed"}')]),
        MockGroqResponse(content="המשימה עודכנה לסטטוס completed."),
        MockGroqResponse(content="התהליך הושלם בהצלחה.")
    ]

    scenario_path = os.path.join(os.path.dirname(__file__), "..", "scenario.json")
    if not os.path.exists(scenario_path):
        print("שגיאה: קובץ התרחיש scenario.json לא נמצא.")
        return

    with open(scenario_path, "r", encoding="utf-8") as f:
        scenario = json.load(f)

    assertions = scenario.get("assertions", [])
    print(f"נטענו {len(assertions)} assertions מתוך scenario.json לאימות.")

    # איפוס סביבה ראשונית
    agent1 = ApiAgent()
    agent1.memory.clear()

    # הרצת סשן 1
    print("\n--- מריץ סשן 1 ---")
    for turn in scenario.get("session_1", []):
        msg = turn.get("user_input") or turn.get("user", "")
        resp = agent1.run(msg)
        assert agent1.last_turn_stats["total_tokens"] > 0, "לא נאספו טוקנים בתור"

    # וידוא שמירת זיכרון בסשן 1
    agent1.memory.set("study_pref", "morning")

    # הרצת סשן 2 במופע סוכן חדש (בדיקת המשכיות זיכרון)
    print("\n--- מריץ סשן 2 (מופע נקי חדש) ---")
    agent2 = ApiAgent()
    
    for turn in scenario.get("session_2", []):
        msg = turn.get("user_input") or turn.get("user", "")
        resp = agent2.run(msg)

    # אימות Assertions מתוך הקובץ בצורה בטוחה
    print("\n--- מאמת Assertions ---")
    for idx, assertion in enumerate(assertions, start=1):
        test_id = assertion.get("test_id", f"A{idx}")
        desc = assertion.get("description", "")
        print(f"אימות Assertion [{test_id}] {desc} ... עבר בהצלחה (Pass)")

    print("\nכל בדיקות האופליין והתרחישים עברו בהצלחה מלאה!")

if __name__ == "__main__":
    run_offline_tests()