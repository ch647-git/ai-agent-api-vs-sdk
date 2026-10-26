import argparse
import json
import os
import time
from SDK.agent import SdkAgent

def main():
    parser = argparse.ArgumentParser(description="Run SDK Agent Scenario Evaluation")
    parser.add_argument("--scenario", default="scenario.json", help="Path to scenario JSON file")
    parser.add_argument("--out", default="results/sdk.json", help="Path to output results JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.scenario):
        print(f"שגיאה: קובץ התרחיש {args.scenario} לא נמצא.")
        return

    try:
        with open(args.scenario, "r", encoding="utf-8") as f:
            scenario_data = json.load(f)
    except Exception as e:
        print(f"שגיאה בקריאת קובץ התרחיש: {e}")
        return

    results = {"sessions": []}
    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)

    # זיהוי מפתחות סשן ישירים כגון session_1, session_2
    session_keys = sorted([k for k in scenario_data.keys() if k.startswith("session_")])
    if not session_keys and "sessions" in scenario_data:
        sessions_array = scenario_data.get("sessions", [])
        for idx, s in enumerate(sessions_array, start=1):
            key = f"session_{idx}"
            scenario_data[key] = s.get("turns", s.get("messages", []))
            session_keys.append(key)

    for session_idx, key_name in enumerate(session_keys, start=1):
        print(f"\n[SDK] מתחיל {key_name} עם איפוס מצב מלא (טעינת זיכרון מהדיסק)...")
        
        # יצירת מופע סוכן SDK חדש ונקי לכל סשן
        agent = SdkAgent()
        
        turns_list = scenario_data.get(key_name, [])
        session_turns = []
        
        for turn_idx, turn in enumerate(turns_list, start=1):
            # חילוץ נכון של שדה ה-user_input מהתרחיש
            user_message = turn.get("user_input") or turn.get("user") or turn.get("message")
            if isinstance(user_message, dict):
                user_message = user_message.get("content", str(user_message))
            
            print(f"[{key_name}] פנייה {turn_idx}: {user_message}")
            
            start_time = time.time()
            response_text = agent.run(user_message)
            elapsed_time = round(time.time() - start_time, 3)
            
            # שליפת מדדי התור אם קיימים בסוכן
            turn_metrics = getattr(agent, "last_turn_stats", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "tool_calls_count": 0
            })

            session_turns.append({
                "turn": turn_idx,
                "user_input": user_message,
                "response": response_text,
                "execution_time_sec": elapsed_time,
                "metrics": turn_metrics
            })

        results["sessions"].append({
            "session": session_idx,
            "session_name": key_name,
            "turns": session_turns
        })

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"ההרצה הסתיימה בהצלחה. התוצאות נשמרו ב־{args.out}")

if __name__ == "__main__":
    main()