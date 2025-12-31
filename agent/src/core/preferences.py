import yaml
from pathlib import Path
from typing import Dict, Any

class PreferenceManager:
    def __init__(self, filepath: str = "config/preferences.yaml"):
        self.filepath = Path(filepath)
        self._cache: Dict[str, Any] = {}
        self.load()

    def load(self):
        if not self.filepath.exists():
            self._cache = {"workflows": {}, "rules": [], "general": {}}
            return

        with open(self.filepath, "r") as f:
            try:
                self._cache = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                print(f"Error parsing preferences: {e}")
                self._cache = {}

    def get_system_prompt_addition(self) -> str:
        self.load()
        
        workflows = self._cache.get("workflows", {})
        rules = self._cache.get("rules", [])
        general = self._cache.get("general", {})

        workflow_str = "\n".join(
            [f"- {name}: {data.get('description', '')} (Actions: {', '.join(data.get('actions', []))})" 
             for name, data in workflows.items()]
        )
        
        rules_str = "\n".join([f"- {rule}" for rule in rules])
        
        return (
            f"<user_preferences>\n"
            f"PREFERRED APPS: {general}\n\n"
            f"DEFINED WORKFLOWS :\n{workflow_str}\n\n"
            f"STRICT RULES:\n{rules_str}\n"
            f"</user_preferences>"
        )
