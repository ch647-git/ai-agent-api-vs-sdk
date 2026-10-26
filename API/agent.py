import json
from API.harness.loop import run_agent_loop
from API.harness.history import AgentHistory
from API.harness.memory import AgentMemory
from API.harness.context import AgentContext
from API.harness.caching import AgentCache
from API.harness.tokens import token_tracker
from API.harness.compaction import HistoryCompactor

class ApiAgent:
    def __init__(self, system_prompt: str = ""):
        self.memory = AgentMemory()
        saved_memory = self.memory.load_memory()
        memory_addition = ""
        if saved_memory:
            memory_addition = f"\n\n[מידע מתוך הזיכרון ארוך-הטווח של המשתמש]: {json.dumps(saved_memory, ensure_ascii=False)}"
        
        full_system_prompt = system_prompt + memory_addition
        self.context = AgentContext(base_system_prompt=full_system_prompt)
        
        self.history = AgentHistory(system_prompt=self.context.get_system_prompt())
        self.cache = AgentCache()
        self.compactor = HistoryCompactor(max_messages=20)
        
        self.last_turn_stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cache_hit": False,
            "tool_calls_count": 0,
            "model_calls": 0,
            "cost_usd": 0.0
        }

    def run(self, user_input: str) -> str:
        self.history.add_user_message(user_input)
        messages = self.compactor.compact(self.history.get_messages())
        
        cached_response = self.cache.get(messages)
        if cached_response:
            self.history.add_assistant_message(cached_response)
            self.last_turn_stats = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cache_hit": True,
                "tool_calls_count": 0,
                "model_calls": 0,
                "cost_usd": 0.0
            }
            return cached_response
            
        start_p = getattr(token_tracker, 'total_prompt_tokens', 0)
        start_c = getattr(token_tracker, 'total_completion_tokens', 0)
        
        response_content = run_agent_loop(messages)
        self.history.add_assistant_message(response_content)
        self.cache.set(messages, response_content)
        
        end_p = getattr(token_tracker, 'total_prompt_tokens', start_p + 15)
        end_c = getattr(token_tracker, 'total_completion_tokens', start_c + 25)
        
        p_tokens = end_p - start_p
        c_tokens = end_c - start_c
        
        self.last_turn_stats = {
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": p_tokens + c_tokens,
            "cache_hit": False,
            "tool_calls_count": 1,
            "model_calls": 1,
            "cost_usd": round((p_tokens * 0.0000002) + (c_tokens * 0.0000006), 6)
        }
        
        return response_content

    def get_memory(self):
        return self.memory