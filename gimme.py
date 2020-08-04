#!/usr/bin/env python3
import argparse
import json
import uuid
import requests
import sys
from string import Formatter
from errors import UserError, RequestError
from request_utils import Requests
from environment_utils import Environments


class Cli(object):
    def __init__(
        self,
        requests_filename='requests.json',
        environments_filename='envs.json',
        print_all_responses=False
    ):
        self.requests = Requests(filename=requests_filename)
        self.environments = Environments(filename=environments_filename)
        self.print_all_responses = print_all_responses

    def make_call(self, request_name, env_name):
        request = self.requests.find(request_name)
        environment = self.environments.find(env_name)

        parsed_req = self._parse_request(request, env_name)

        url = f"{environment['base_url']}{parsed_req['endpoint']}"

        headers = {'content-type': 'application/json'}
        if 'headers' in environment:
            headers = {**headers, **environment['headers']}

        if parsed_req['type'] == 'POST':
            response = requests.post(url, data=json.dumps(parsed_req['body']), headers=headers)
        elif parsed_req['type'] == 'PUT':
            response = requests.put(url, data=json.dumps(parsed_req['body']), headers=headers)
        elif parsed_req['type'] == 'GET':
            response = requests.get(url, params=parsed_req['body'], headers=headers)
        else:
            raise UserError(f'Unknown HTTP method {parsed_req["type"]}')

        response_json = response.json()
        if response.status_code != 200:
            raise RequestError(
                f'{response.status_code} returned when calling {request_name} with response '
                f'{response_json}. Expected status code 200.'
            )

        if self.print_all_responses:
            print(f'Response for call to {request_name}:')
            print(response_json)
        
        return response_json

    def _parse_request(self, request, base_url):
        if isinstance(request, str):
            parameters = [
                parameter for _, parameter, _, _ in Formatter().parse(request) if parameter
            ]
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


def setup_argparse():
    parser = argparse.ArgumentParser(description='Create and retrieve objects in a rest API.')
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

    parser.add_argument(
        '-rf',
        '--requests_file',
        help='the requests file location',
    )

    parser.add_argument(
        '-ef',
        '--environments_file',
        help='the environments file location',
    )

    parser.add_argument(
        '-o',
        '--output_all_requests',
        help='prints all the requests being made',
        action='store_true'
    )

    parser.add_argument(
        '-e',
        '--env',
        '--environment',
        metavar='env_name',
        help='the name of environment to use',
    )
    return parser


if __name__ == '__main__':
    parser = setup_argparse()

    args = parser.parse_args()

    cli = None
    try:
        cli = Cli(
            requests_filename=args.requests_file or 'requests.json',
            environments_filename=args.environments_file or 'envs.json',
            print_all_responses=args.output_all_requests
        )
    except UserError as e:
        print(str(e))
        sys.exit(1)

    if args.list:
        cli.requests.print_request_list()
    elif args.request:
        try:
            print(cli.make_call(args.request, args.env or 'default'))
        except (UserError, RequestError) as e:
            print(str(e))
            sys.exit(1)
    else:
        print('Type -h for help')
