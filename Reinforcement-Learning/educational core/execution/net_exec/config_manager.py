import json
import logging

def load_config(filepath="config.json"):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"فایل پیکربندی {filepath} پیدا نشد.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"JSON نامعتبر در فایل پیکربندی {filepath}.")
        return {}
