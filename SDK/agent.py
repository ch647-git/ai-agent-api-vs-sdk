
import os
import json
from groq import Groq
from SDK.tools import SDK_TOOLS_SCHEMA, execute_sdk_tool


class SdkAgent:
    """סוכן המשתמש ב-Groq SDK להפעלת כלים ולניהול שיחה."""

    def __init__(self, system_prompt: str = "", max_tool_rounds: int = 8):
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY אינו מוגדר במשתני הסביבה."
            )

        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds

        # היסטוריית השיחה נשמרת בזיכרון התהליך.
        self.messages = []

        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })

        # הכנת הכלים בפורמט המצופה על ידי Groq.
        self.tools = [
            {
                "type": "function",
                "function": tool["function"]
            }
            for tool in SDK_TOOLS_SCHEMA
        ]

    def run(self, user_input: str) -> str:
        """מריץ תור שיחה, כולל מספר סבבי הפעלת כלים."""

        print("[SDK/agent.py] קלט משתמש:", user_input)

        self.messages.append({
            "role": "user",
            "content": user_input
        })

        for round_number in range(self.max_tool_rounds):
            # שליחת בקשה למודל.
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.messages,
                    tools=self.tools if self.tools else None,
                    tool_choice="auto" if self.tools else None,
                    temperature=0.2
                )

            except Exception as exc:
                print(f"[SDK/agent.py] שגיאת API: {exc}")
                return "אירעה שגיאה בתקשורת עם המודל."

            message = response.choices[0].message

            # שמירת הודעת העוזר בהיסטוריה.
            assistant_message = message.model_dump(
                exclude_none=True
            )

            self.messages.append(assistant_message)

            # אם המודל לא ביקש כלים, התור הסתיים.
            if not message.tool_calls:
                answer = message.content or ""
                print("[SDK/agent.py] התור הסתיים.")
                return answer

            print(
                f"[SDK/agent.py] סבב כלים "
                f"{round_number + 1}/{self.max_tool_rounds}"
            )

            # הפעלת הכלים שהתבקשו.
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name

                try:
                    tool_args = json.loads(
                        tool_call.function.arguments or "{}"
                    )

                    if not isinstance(tool_args, dict):
                        raise ValueError(
                            "ארגומנטים חייבים להיות אובייקט JSON."
                        )

                    result = execute_sdk_tool(
                        tool_name,
                        tool_args
                    )

                    # שמירה על פורמט מחרוזת בתוצאת הכלי.
                    if not isinstance(result, str):
                        result = json.dumps(
                            result,
                            ensure_ascii=False,
                            default=str
                        )

                except (json.JSONDecodeError, ValueError) as exc:
                    result = json.dumps(
                        {
                            "error": (
                                f"ארגומנטים לא תקינים: {exc}"
                            )
                        },
                        ensure_ascii=False
                    )

                except Exception as exc:
                    result = json.dumps(
                        {
                            "error": (
                                f"שגיאה בהפעלת הכלי: {exc}"
                            )
                        },
                        ensure_ascii=False
                    )

                print(
                    f"[SDK/agent.py] כלי {tool_name} הסתיים."
                )

                # החזרת תוצאת הכלי להיסטוריית השיחה.
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        # עצירה מבוקרת במקרה שהמודל ממשיך לבקש כלים.
        print(
            "[SDK/agent.py] הושגה מגבלת סבבי הכלים."
        )

        return (
            "הסוכן הגיע למגבלת סבבי הכלים "
            "לפני השלמת הבקשה."
        )
