#!/usr/bin/env python3
import argparse
import json
import uuid
import requests
from string import Formatter


class Cli(object):
    requests = {}
    environments = {}

    def __init__(self, requests_filename='requests.json', environments_filename='envs.json'):
        self._load_environments(filename=environments_filename)
        self._load_requests(filename=requests_filename)

    def make_call(self, request_name, env_name):
        if request_name not in self.requests:
            raise Exception(f'Could not find {request_name} in available requests.')
        if env_name not in self.environments:
            raise Exception(f'Could not find {env_name} in available environments.')

        req = self._parse_request(self.requests[request_name], env_name)
        url = f"{self.environments[env_name]['base_url']}{req['endpoint']}"
        headers = {'content-type': 'application/json'}
        if 'headers' in self.environments[env_name]:
            headers = {**headers, **self.environments[env_name]['headers']}

        if req['type'] == 'POST':
            response = requests.post(url, data=json.dumps(req['body']), headers=headers)
        elif req['type'] == 'GET':
            response = requests.get(url, params=req['body'], headers=headers)
        else:
            raise Exception(f'Unknown HTTP method {req["type"]}')
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def _parse_request(self, request, base_url):
        if isinstance(request, str):
            parameters = [parameter for _, parameter, _, _ in Formatter().parse(request) if parameter]
            values = {}
            for parameter in parameters:
                new_request = parameter.split('[')[0]
                values[new_request] = self._populate_parameter(new_request, base_url)
            return request.format(**values)
        if isinstance(request, list):
            parsed = []
            for value in request:
                parsed.append(self._parse_request(value, base_url))
            return parsed
        parsed = {}
        for attribute, value in request.items():
            parsed[attribute] = self._parse_request(value, base_url)
        return parsed

    def _populate_parameter(self, parameter_name, base_url):
        if parameter_name == 'uuid':
            return str(uuid.uuid4())
        else:
            return self.make_call(parameter_name, base_url)

    def _load_requests(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            for d in data:
                self._validate_request_object(d)
                self.requests[d['name']] = d

    def _load_environments(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            for d in data:
                self._validate_environment_object(d)
                for name in d['names']:
                    self.environments[name] = d

    @staticmethod
    def _validate_request_object(d):
        if 'name' not in d:
            raise Exception(f"Request json object missing 'name' field: {d}")
        if 'endpoint' not in d:
            raise Exception(f"Request json object missing 'endpoint' field: {d}")
        if 'type' not in d:
            raise Exception(f"Request json object missing 'type' field: {d}")
        if 'body' not in d:
            raise Exception(f"Request json object missing 'body' field: {d}")

    @staticmethod
    def _validate_environment_object(d):
        if 'names' not in d:
            raise Exception(f"Environment json object missing 'names' field: {d}")
        if 'base_url' not in d:
            raise Exception(f"Environment json object missing 'base_url' field: {d}")

    def is_default_env_set(self):
        return 'default' in self.environments

    def print_request_list(self):
        for r in self.requests.values():
            print(f'Name: {r["name"]}')
            if 'description' in r:
                print(f'Description: {r["description"]}')
            print('-' * 20)


if __name__ == '__main__':
    cli = Cli()

    parser = argparse.ArgumentParser(description='Create objects in a rest API.')
    parser.add_argument(
        'request',
        metavar='request_name',
        help='the name of a request to make',
        nargs='?'
    )

    parser.add_argument(
        '-l',
        '--list',
        help='list all objects and exit',
        action='store_true'
    )

    if cli.is_default_env_set():
        parser.add_argument(
            '-e',
            '--env',
            '--environment',
            metavar='env_name',
            help='the name environment to use',
        )
    else:
        required_named_args_parser = parser.add_argument_group('required named arguments')
        required_named_args_parser.add_argument(
            '-e',
            '--env',
            '--environment',
            metavar='env_name',
            help='the name environment to use. This can be made optional by naming an env as default',
            required=True
        )
    args = parser.parse_args()
    if args.list:
        cli.print_request_list()
    elif args.request:
        print(cli.make_call(args.request, args.env or 'default'))
    else:
        print('Type -h for help')
