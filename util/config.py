default_config = {
    'debug': False,
    'max_repos': 3,
    'max_files_per_repo': 5,
    'max_depth_per_repo': 3,
}

class Config:
    def __init__(self):
        self._config = default_config

    def set(self, key, value):
        # If value is None, use default value
        if value is None:
          return

        self._config[key] = value

    def get(self, key, default=None):
        return self._config.get(key, default)