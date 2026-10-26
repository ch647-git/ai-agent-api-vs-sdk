class AgentContext:
    """
    מחלקה לניהול ההקשר (Context) והנחיות המערכת (System Prompts) של הסוכן.
    """
    def __init__(self, base_system_prompt: str = ""):
        self.base_system_prompt = base_system_prompt
        self.dynamic_context = {}

    def set_system_prompt(self, prompt: str):
        """עדכון הנחיית המערכת הראשית"""
        self.base_system_prompt = prompt

    def get_system_prompt(self) -> str:
        """קבלת הנחיית המערכת המלאה כולל נתונים דינמיים אם קיימים"""
        prompt = self.base_system_prompt
        if self.dynamic_context:
            prompt += f"\n\nהקשר נוסף למערכת:\n{self.dynamic_context}"
        return prompt

    def update_dynamic_context(self, key: str, value):
        """הוספה או עדכון של נתון הקשר דינמי"""
        self.dynamic_context[key] = value

    def clear_dynamic_context(self):
        """איפוס ההקשר הדינמי"""
        self.dynamic_context.clear()