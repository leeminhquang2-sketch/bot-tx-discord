# bot/config_manager.py
import json
import os

CONFIG_FILE = "data/config.json"

DEFAULT_CONFIG = {
    "api_port": 5000,
    "api_host": "0.0.0.0",
    "daily_reward": 5000,
    "bet_multiplier": 194,
    "currency_name": "MQ",
    "min_bet": 1000,
    "max_bet": 10000000,
    "enable_web": True,
    "debug_mode": False,
    "web_title": "Game MQ Admin",
    "web_footer": "© 2026 Game MQ System"
}

class ConfigManager:
    def __init__(self):
        self.ensure_data_dir()
        self.config = self.load_config()
    
    def ensure_data_dir(self):
        if not os.path.exists("data"):
            os.makedirs("data")
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    
    def save_config(self, config=None):
        if config is None:
            config = self.config
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def update(self, data):
        self.config.update(data)
        self.save_config()
    
    def reload(self):
        self.config = self.load_config()
        return self.config

# Singleton
config_manager = ConfigManager()
