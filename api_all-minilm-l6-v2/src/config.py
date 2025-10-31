import json
import os

class Config:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        with open(self.config_path, 'r') as f:
            config_data = json.load(f)

        # Assign properties dynamically from config_data
        for key, value in config_data.items():
            setattr(self, key, value)

        # Validate essential fields
        required_fields = [
            "input_db_path", "output_db_path", "input_table",
            "id_column", "text_column", "output_table", "batch_size"
        ]
        for field in required_fields:
            if not hasattr(self, field):
                raise ValueError(f"Missing required config field: {field}")

        # Ensure batch_size is a positive integer
        if not isinstance(self.batch_size, int) or self.batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")
