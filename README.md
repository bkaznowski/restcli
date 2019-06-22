# Gimme - a generic REST CLI tool
This script allows creating a simple REST CLI. It is designed to be lightweight, flexible and easy to use. The main usecase for this is to quickly setup an environment for a manual test. Once the environment is setup, you can use the objects in requests from curl or postman.

## How to use it
1) Populate the [environment file](#environment-file).
2) Populate the [requests file](#requests-file).
3) Run the script with the request name and the environment var (this can be omitted if a default is set).

positional arguments:
* `request_name` - the name of a request to make

optional arguments:
* `-h`, `--help` - show this help message and exit
* `-l`, `--list` - list all objects and exit
* `-e env_name`, `--env env_name`, `--environment env_name` - the name environment to use

## Environment file
There are two fields that are required:
| name of field | required | description                                                                                             |
|---------------|----------|---------------------------------------------------------------------------------------------------------|
| `names`       | yes      | Used to specify which base URL to use. `default` can be provided to make an environment the default one |
| `base_url`    | yes      | The base URL of your API                                                                                |
| `headers`     | no       | Used to provide headers in requests                                                                     |

Example:
```json
[
  {
    "names": ["default", "local", "l"],
    "base_url": "http://localhost"
  },
  {
    "names": ["dev", "d"],
    "base_url": "http://dev.somedomain.com",
    "headers": {
      "Api_Key": "some api key",
      "Authorization": "Basic abc123="
    }

  },
  {
    "names": ["staging", "s"],
    "base_url": "http://staging.somedomain.com",
    "headers": {
      "Api_Key": "some api key",
      "Authorization": "Basic abc123="
    }
  },
  {
    "names": ["prod"],
    "base_url": "http://prod.somedomain.com",
    "headers": {
      "Api_Key": "some api key",
      "Authorization": "Basic abc123="
    }
  }
]
```

## Requests file
The requests file requires that objects have fields called:

| name of field | required | description                                               |
|---------------|----------|-----------------------------------------------------------|
| `name`        | yes      | What you will use when calling and referring to objects   |
| `descrption`  | no       | Will be displayed when listing the requests               |
| `type`        | yes      | The HTTP request type. Supported types are: `POST`, `GET` |
| `endpoint`    | yes      | The endpoint                                              |
| `body`        | yes      | the body of the request                                   |
You can provide dynamic fields by using `{name[some_field]}`. `{uuid}` will generate a random uuid. Anything else will try and make a call and use the `id` field in the response. These dynamic fields can be used in any of the objects parameters (body/endpoint).

Example:
```json
[
  {
    "name": "user",
    "description":  "Creates a user",
    "type": "POST",
    "endpoint": "/users",
    "body": {
      "request_id": "{uuid}",
      "user": {
        "id": "{uuid}",
        "name": "A user"
      }
    }
  },
  {
    "name": "user_group",
    "description":  "Creates a user group",
    "type": "POST",
    "endpoint": "/user_group",
    "body": {
      "request_id": "{uuid}",
      "account": {
        "id": "{uuid}",
        "name": "some name",
        "users": [
          "{user[id]}",
          "{user[id]}",
          "{user[id]}"
        ]
      }
    }
  }
]
```