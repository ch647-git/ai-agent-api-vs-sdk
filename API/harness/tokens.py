class TokenTracker:
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.turns_log = []

    def reset(self):
        """איפוס מוחלט של נתוני הטוקנים"""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.turns_log = []

    def add_usage(self, usage_or_prompt=0, completion_tokens=0, session_idx=1, turn_idx=1, model="llama-3.3-70b-versatile"):
        """תמיכה הן באובייקט usage של ה־API והן בהעברת מספרים ישירים לבדיקות"""
        if hasattr(usage_or_prompt, "prompt_tokens"):
            p_tokens = getattr(usage_or_prompt, "prompt_tokens", 0)
            c_tokens = getattr(usage_or_prompt, "completion_tokens", 0)
        else:
            p_tokens = int(usage_or_prompt)
            c_tokens = int(completion_tokens)

        self.total_prompt_tokens += p_tokens
        self.total_completion_tokens += c_tokens
        
        self.turns_log.append({
            "session": session_idx,
            "turn": turn_idx,
            "model": model,
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": p_tokens + c_tokens
        })

    def get_stats(self):
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "turns": self.turns_log
        }

token_tracker = TokenTracker()