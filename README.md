# Generic REST CLI tool
This script allows creating a simple REST CLI. It is designed to be lightweight, flexible and easy to use.

## How to use it
1) Populate the [environment file](#envs-file).
2) Populate the [requests file](#requests-file).
3) Run the script with the request name and the environment var (this can be omitted if a default is set).

## Environment file
There are two fields that are required:
1) names - this is used to specify which base URL to use. `default` can be provided to make an environment the default one.
2) base_url - this is the base URL of your API.
```json
[
  {
    "names": ["default", "local", "l"],
    "base_url": "localhost"
  },
  {
    "names": ["dev", "d"],
    "base_url": "http://dev.somedomain.com"
  },
  {
    "names": ["staging", "s"],
    "base_url": "http://staging.somedomain.com"
  },
  {
    "names": ["prod"],
    "base_url": "http://prod.somedomain.com"
  }
]
```

## Requests file
The requests file requires that objects have fields called:
1) name - this is what you will use when calling and referring to objects.
2) type - the HTTP request type. This is currently ignored.
3) endpoint - the endpoint.
4) body - the body of the request.
You can provide dynamic fields by using `{name}`. `{uuid}` will generate a random uuid. Anything else will try and make a call and use the `id` field in the response. These dynamic fields can be used in any of the objects parameters.
```json
[
  {
    "name": "user",
    "type": "POST",
    "endpoint": "/users",
    "body": {
      "request_id": "{uuid}",
      "user": {
        "id": "{uuid}"
      }
    }
  },
  {
    "name": "user_group",
    "type": "POST",
    "endpoint": "/user_group",
    "body": {
      "request_id": "{uuid}",
      "account": {
        "id": "{uuid}",
        "name": "some name",
        "users": [
          "{user}",
          "{user}",
          "{user}"
        ]
      }
    }
  }
]
```