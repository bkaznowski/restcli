import json
from errors import UserError

class Environments():
    _environments = {}

    def __init__(self, filename: str):
        self._load_environments(filename)

    def find(self, name: str):
        if name not in self._environments:
            if name == 'default':
                raise UserError(
                    f'No default env set in environments. Set a default environment or provide one.'
                )
            raise UserError(f'Could not find {name} in available environments.')
        return self._environments[name]

    def _load_environments(self, filename):
        try:
            with open(filename) as json_file:
                data = json.load(json_file)
                for d in data:
                    self._validate_environment_object(d)
                    for name in d['names']:
                        self._environments[name] = d
        except Exception as e:
            raise UserError(str(e))

    @staticmethod
    def _validate_environment_object(d):
        if 'names' not in d:
            raise UserError(f"Environment json object missing 'names' field: {d}")
        if 'base_url' not in d:
            raise UserError(f"Environment json object missing 'base_url' field: {d}")

    def is_default_env_set(self):
        return 'default' in self._environments
