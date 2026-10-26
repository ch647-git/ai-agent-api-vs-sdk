import os

directories = [
    "shared",
    "API/harness",
    "SDK",
    "tests",
    "results"
]


files = [
    "shared/__init__.py",
    "shared/data.json",
    "shared/tools_def.py",
    "API/main.py",
    "API/agent.py",
    "API/harness/__init__.py",
    "API/harness/loop.py",
    "API/harness/tools.py",
    "API/harness/history.py",
    "API/harness/memory.py",
    "API/harness/context.py",
    "API/harness/compaction.py",
    "API/harness/caching.py",
    "API/harness/tokens.py",
    "SDK/main.py",
    "SDK/agent.py",
    "SDK/tools.py",
    "scenario.json"
]

def create_project_structure():
    print("מתחיל ביצירת מבנה הפרויקט...")
 
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"נוצרה תיקייה: {directory}")
        
   
    for file_path in files:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    f.write("{}")
                else:
                    f.write("")
            print(f"נוצר קובץ: {file_path}")
            
    print("הפרויקט מוכן לעבודה!")

if __name__ == "__main__":
    create_project_structure()