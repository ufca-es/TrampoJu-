# data_manager.py
import json

class DataManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    def load_json(self, filename: str, default_key: str) -> dict:
        try:
            with open(f"{self.base_path}/{filename}", "r", encoding="utf-8") as f:
                data = json.load(f)
                if default_key not in data:
                    data[default_key] = []
                return data
        except FileNotFoundError:
            return {default_key: []}

    def save_json(self, filename: str, data: dict):
        with open(f"{self.base_path}/{filename}", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)