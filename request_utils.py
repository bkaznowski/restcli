import json
from errors import UserError

class Requests():
    _requests = {}

    def __init__(self, filename: str):
        self._load_requests(filename)

    def _load_requests(self, filename):
        try:
            with open(filename) as json_file:
                data = json.load(json_file)
                for d in data:
                    self._validate_request_object(d)
                    self._requests[d['name']] = d
        except Exception as e:
            raise UserError(str(e))

    def find(self, name: str):
        if name not in self._requests:
            raise UserError(f'Could not find {name} in available requests.')
        return self._requests[name]

    @staticmethod
    def _validate_request_object(d):
        if 'name' not in d:
            raise UserError(f"Request json object missing 'name' field: {d}")
        if 'endpoint' not in d:
            raise UserError(f"Request json object missing 'endpoint' field: {d}")
        if 'type' not in d:
            raise UserError(f"Request json object missing 'type' field: {d}")
        if 'body' not in d:
            raise UserError(f"Request json object missing 'body' field: {d}")

    def print_request_list(self):
        for r in self._requests.values():
            print(f'Name: {r["name"]}')
            if 'description' in r:
                print(f'Description: {r["description"]}')
            print('-' * 20)
