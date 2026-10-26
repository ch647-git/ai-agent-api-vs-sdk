class HistoryCompactor:
    """
    מחלקה לכיווץ וניהול היסטוריית השיחה של הסוכן,
    במטרה לצמצם את כמות ה-tokens כאשר ההיסטוריה גדלה מדי.
    """
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages

    def compact(self, messages: list) -> list:
        """
        כיווץ ההיסטוריה: שומר את הודעת המערכת (אם קיימת)
        ואת ההודעות האחרונות ביותר עד לסף המקסימלי המוגדר.
        """
        if len(messages) <= self.max_messages:
            return messages

        system_message = None
        other_messages = messages

        # זיהוי ושמירת הודעת המערכת הראשונית במידה וקיימת
        if messages and messages[0].get("role") == "system":
            system_message = messages[0]
            other_messages = messages[1:]

        # חיתוך ההודעות השמורות כך שתישארנה רק האחרונות ביותר
        retained_messages = other_messages[-(self.max_messages - 1):]

        if system_message:
            return [system_message] + retained_messages
        
        return retained_messages