<!-- DO NOT EDIT. GENERATED from doc/help.md Makefile -->

- [TL;DR](#tl-dr)
- [Overview](#overview)
- [OpenAPI](#openapi)
- [Setup](#setup)
- [Run](#run)
- [Call](#call)
- [Add a Route - Introduction](#add-a-route---introduction)
- [Add a Route - Details](#add-a-route---details)
- [Testing](#testing)
- [Add a dependency](#add-a-dependency)
- [Dev Workflow](#dev-workflow)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Links](#links)
- [Troubleshooting](#troubleshooting)
- [Extra](#extra)

## TL;DR

For a quick start you can run:

    make test

immediately after cloning this repo and the tests should all just work, assuming that you have Docker installed.

Under the hood, all the [Setup](#setup) steps below will be done so that the HUAPI pytests are run in the `huapi` Docker containter.

## Overview

Hosting UAPI exposes functionality for Hosting, Sites, Addons, and other resources provided by backend APIs to customer-facing front ends (such as MFEs inside an Account Manager). One of its primary functions is to authorize incoming requests by inspecting the uJWT and checking that the caller is authorized to operate on the target resource. If the caller is authorized, it will pass the call to the backend API. It can perform one-to-one API calls, or aggregate multiple backend API calls into a single response.

## OpenAPI

#### [ReDoc](https://beta-hosting-uapi.apps.provo1.endurancemb.com/redoc)
#### [SwaggerUI for beta](https://beta-hosting-uapi.apps.provo1.endurancemb.com/docs)

## Setup

0. Install Docker

    [Docker Install Intructions](https://confluence.newfold.com/display/HGPD/Docker+Setup)

1. Build

    Navigate to root of huapi repo.

        docker/build

## Run

### Start server

This mounts your host files and will auto-reload so any changes will be available immediately in the API.

    docker/server

You should be able to hit the API now in a seperate window (returns "ok")

    curl http://localhost:8000

### Run tests

    docker/test

### Run commands

For any of the commands listed in this README, you can run them in your docker container with `docker/run` or `docker/shell`.

    docker/run COMMAND

### Shell

Start a shell in the container, and run the commands normally (no prefix needed).

    docker/shell

To see the full list of commands, check out the `bin` directory.

### Make

Most commands can be run with make. Run `make help` to see the man page.

See [Makefile Usage](makefile-usage) below.


## Call

Calling the API requires passing a JWT in the HTTP header as `authorization: bearer JWT`.

A full example is in `examples/client-http.pl`

### Create HAL resources

Depending on what routes you are calling, you will need different resources to be created in HAL before making UAPI calls.

To create a basic hosting account, use `create-hosting`:

    create-hosting -h

### Creating a token

To create a token, use `create-token`. The token will be issued to a specific tenant/account and brand.

    create-token -h

### Other Resources

We will add more examples in the future, if you need other HAL resources (such as addons) please consult a HAL expert or try the HAL Integration room. You can also take a look at other scripts in the bin directory.


## Add a Route - Introduction

Click on a header link to jump to details on creating that kind of route.

### Introduction

#### [Method1 - Auto Generated Handler](#route1-autogen)

Some UAPI routes will map 1-to-1 with a HAL route. For this use-case, you can use the [route generator script](#route1-autogen) and do not have to write any code to create a new route. It will also generate the OpenAPI spec for that route. This allows new routes to be created quickly, consistently, and securely. Even if you will be building a custom route, the route generator script may be helpful for generating the base OpenAPI spec, which you can then modify by hand. It combines filtering the request args, calling HAL, and filtering the response.

#### [Method 2 - Direct Hal API Calls](#route2-direct)

If you need more flexibility, you can make direct API calls using the `clients.hal.user module`, created with `UapiHall.from_http(req)`. This module automatically authorizes the user based on the target in the URL and the account defined in token.

#### [Method 3 - Multiple Async Calls](#route3-multi)

If a route needs to make multiple HAL calls simultaneously there is a create_tasks() method to help fire off async tasks. See examples/ folder for some examples or look at some routes under app/routers/.

#### For all Methods

Whether you are using auto-generated or custom routes, make sure you understand the authorization scope, and what you are allowing the user to operate against.



### Authorization

These routes handle authorization for you by inspecting the JWT and ensuring it is authorized to act on the TARGET in the url, or to act on a resource owned by the target. The target has a TARGET_TYPE and a TARGET_ID. Urls are formatted as /`TARGET_TYPE/TARGET_ID/resource`. For example, `/hosting/123/ftp`, The target_type is hosting, the target_id is 123.

### Target IDs

Target ID is the primary key in HAL for hal-based methods, hosting_id maps to HAL's account_id. addon_id and site_id map to their respective ids. All routes also accept the calling platform's ID, called *Back reference* (platform's choose their own back reference when creating a HAL resource). To use a back reference instead of the HAL id, prefix it with ~ (`/hosting/~abc/ftp`). This is useful when the you do not have a HAL ID, but know your platform's back reference.

### Target Types

The target_types and example resource routes can be seen in the table below. You will notice that there is no target_id in the route path when the target_type is account. This is because the needed identifiers for the Account target type are in the JWT that is used to authorize requests to HUAPI.

| Target Type   | Example resource route making use of the Target Type id   |
| ------------- | --------------------------------------------------------- |
| Hosting       | /hosting/{hosting_id}/ftp                                 |
| Addons        | /addons/codeguard/{addon_id}/website_list                 |
| Sites         | /sites/{site_id}/sso                                      |
| Account       | /account/domains                                          |

Remember that target type is tied to authorization.


### Handler

The handler is the method that will process the request. Again, most handlers are just forwarding the request to HAL. Addon_action is an example of a handler that does some light pre-processing to make the mapping file simpler and to stream-line creating new addon actions.

Handler is not the same as target type, but the handler *often* implies the target_type. Addon_actions will always have a target_type of addon, and gap methods will often have a target_type of hosting.


## Add a Route - Details

### Method 1: Autogenerated Handler <a name="route1-autogen"></a>

Open a shell into your container `docker/shell`, or prefix the follow commands with `docker/run`.

#### 1. Generate Mapping File

    route new --name ftp --handler gap --action gap_ftp_list --http get

Creates:
* Mapping - app/routers/hosting/ftp/ftp.mapping.yaml

#### 2. Edit Request/Response

Edit the mapping file to define the request/response. These will filter the http request/response. You can also tweak any other settings such as the url.

Verify that target_type and all other settings are correct.

#### 3. Generate Route and OpenAPI

    route generate --name ftp

Creates:
* Route - app/routers/hosting/ftp/ftp.py
* OpenAPI - app/routers/hosting/ftp/ftp.openapi.json

The OpenAPI file is not only documentation, but is used to filter request/responses. The python method name must match the OperationID for this to work.


#### More New Route Examples

There are several other ways to generate new routes, here are some examples. Run `route -h` for more info.

Interactive menu to fill out arguments

    route new

Addon action

    route new --name codeguard --handler addon_action --action website_list --http get

Shortcut for gap method

    route new -s 'get gap_ftp_list'

Shortcut for addon_action

    route new -s 'get addon_action_codeguard_website_list'

#### Mapping file

##### Request

Request defines arguments which will be passed to HAL. If its an HTTP GET then args are pulled from the query string (and converted to HAL's RPC format). If its an HTTP POST they are pulled from JSON body.

The default routes reserve PATH parameters to refer to the TARGET_TYPE and TARGET_ID (/hosting/123), and extra parameters are sent in query string or body.

##### GET Example

UAPI Request

    GET /hosting/123/ftp?limit=1

Maps to HAL request

    { "limit": 1, "account_id": 123 }

##### Response

The response filters the response coming back from HAL. You only want to return fields that are needed by the UI. Remember that this is a customer-facing API, anything returned is visible by the customer whether its displayed in the UI or not.

### Method 2: Direct Calls to HAL  <a name="route2-direct"></a>

#### Example Code

    @router.get("/v1/sites/{site_id}/plugins")
    async def get_site_plugins(request: Request):
        hal = await uapi.UapiHal.from_http(request)

        if hal.subtype == "wordpress":
            request_args = hal.args()
            hal_result = hal.gt_site('WP_Plugin_List', request_args)
            response = build_response(hal_result)
            return response
        else:
            return { "error": "only wordpress type is supported" }

#### Explanation

* auth - the token in the http request auth header will be checked against the site_id in the url to see if the user owns the site.
* hal.args() - this will pull query string params or request_body depending on whether its a GET or POST, so args are handled the same for both. This method validates the incoming args against the OpenAPI spec.
* gt_site() - The site_id is converted into a hal account_id and docroot to be passed to GT in addition to other request_args passed. The regular gt() method can also be used for non-site calls (which will also add the account_id automatically)
* build_response() is not a real method.  It is a placeholder for whatever code you will use to filter, validate, and build a response for the user. Responses from HAL should be validated and filtered and not returned directly to the user.

### Method 3: Multiple Async Hal Calls <a name="route3-multi"></a>

#### Example Code

    @router.get('/v1/addons/{addon_id}/example_codeguard_backups_tasks')
    async def get_example_codeguard_backups_tasks(request: Request):
        hal = await UapiHal.from_http(request)

        db = HalTask('databases', 'addon_action', { 'action': 'database_list' })
        web = HalTask('websites', 'addon_action', { 'action': 'website_list' })

        results = await hal.call_tasks([db, web])

        response = {}

        if db.is_success:
            add_to_response(response, db.result)
        else:
            # handle error in db.result
            db.result

        if web.is_success:
            add_to_response(response, result.result)
        else:
            # handle error in web.result

## Error & Exception handling

To return an error from a route, throw an AppException (or deriviative) instead of returning a dict with an error message. AppExceptions are caught at a level above routes and are handled appropriately. Any exceptions that are thrown are logged and can be viewed from [datadog](https://app.datadoghq.com/logs?query=service%3Ahosting-uapi%20%20%40http.status_code%3A%3E%3D400&cols=%40http.method%2C%40http.status_code%2C%40http.url_details.path%2C%40duration_seconds%2C%40action%2C%40name%2C%40hal.duration%2C%40error.kind%2C%40error.message&index=&messageDisplay=inline&saved-view-id=1168927&stream_sort=time%2Cdesc&viz=stream&from_ts=1660667039223&to_ts=1663259039223&live=true).


DO:
```python
from app.exceptions.site import SiteTypeUnsupportedError

raise SiteTypeUnsupportedError('Only WordPress sites can be updated at this time')
```
DON'T:
```python
return {
    'error': "Only WordPress sites can be updated at this time"
}
```

AppException and AppException derived classes (found in app.exceptions.*) have specific error codes, events, and custom http status codes. The error codes are mapped to customer friendly error messages on the frontend. This is useful because the frontend devs & UX are given control over the messages that are displayed to the customer and their translations.

The difference between an error and an exception is that exceptions have the possibility of recovering from in some cases. Errors on the other hand, generally cannot be recovered from. It's not advised to catch exceptions unless your code is able to recover from it. If there is an edge case where you want to catch an exception / error and continue executing the code (this should be rare), you should log it at the very least with `log_warning(request: Request, message=None, event=None)` that's provided by app.logger.

When an exception/error is raised from a route, we catch it in the middleware layer. If it's a class derived from AppException, we pull the error code from the thrown object as well as the http status code. We will then return an error response containing the error code and set the status code of the response to what's defined in the class. For example, if a request is made with a bad Authorization header, we will throw `AuthHeaderError`. It will be caught in the middleware layer and our response status code will be 401 and the object we return will be:

```js
{
    "error": "unauthorized",
}
```


| Class                        | Error Code            | HTTP Status Code | Event                 |
|------------------------------|-----------------------|------------------|-----------------------|
| AppException                 | unknownError          | 512              | dynamic             |
| AuthHeaderError              | unauthorized          | 401              | Auth.Header.Invalid   |
| AuthTokenError               | unauthorized          | 401              | Auth.Token.Invalid    |
| AuthTokenUnknownKeyError     | unauthorized          | 401              | Auth.Token.UnknownKey |
| AuthTokenExpiredError        | authExpired           | 401              | Auth.Token.Expired    |
| HalNetworkError              | networkError          | 512              | Hal.NetworkError      |
| HalResourceNotFoundException | resourceNotFound      | 404              | Hal.NotFound          |
| SiteDBConnectionError        | siteDBConnectionError | 512              | Site.DB.ConnectError  |
| SiteConfigNotFoundException  | siteConfigNotFound    | 404              | Site.Config.NotFound  |
| SiteTypeUnsupportedError     | siteTypeUnsupported   | 400              | Site.Type.Unsupported |

If you want to throw an exception that isn't covered by an existing class, you can throw an AppException and specify the msg, event, and status code:

```python
raise AppException(f'site title is too long', event='Site.Title.Invalid', status_code=400, data={'title': site_title})
```

The first parameter is a message that describes or gives more details about the error. It is not returned to the frontend and displayed to customers. The event parameter should categorize the error in a resourceful way. The status code also helps categorize the error. When a customer passes bad data like an invalid site title, an appropriate status code would be a 4xx (client error). In this case, 400 (BAD_REQUEST). If the problem stems from a server (HAL, HUAPI, etc), then an appropriate code would be a 512 (server error). In the case of a server error, you can just not pass a status code as AppExceptions default is 512. The optional `data` parameter exists so any variables that might be helpful in determining why the error occurred can be logged.

## Testing

Testing uses the pytest framework.

    docker/test

Or run `pytest` in your container


## Add a dependency

Pipenv Install

    pipenv install <module_name>

Rebuild docker image: `docker/build`

This adds the dependency to `Pipfile` and regenerates the `Pipfile.lock` which will UPGRADE all modules if new versions exist. Both of these files are in git which allows for reproducible builds. Be mindful of what modules are upgrading and perform additional testing as needed.


If you want to install a module without updating others

    PIPENV_KEEP_OUTDATED=1 pipenv install <module_name>



## Dev Workflow

### Branch workflow

CURRENT WORKFLOW:

1. Create a feature branch from `beta`
2. QA on your feature-branch openshift instance (see below)
3. Create a pull request to `beta`
4. Merge to `beta`

FUTURE WORKFLOW:

1. Create a feature branch from `main`
2. QA on your feature-branch openshift instance (see below)
3. Create a pull request to `beta`
4. Merge to beta / QA on beta
5. Create a pull request to `main`
6. Merge to main

### Automated Tests

Code must have adequate test coverage, including both unit and integration tests.

Run `docker/test` after making changes to ensure tests pass.

### OpenAPI spec

OpenAPI spec mu

### Openshift Testing

Branches are auto-deployed to the Alpha Openshift so that testing can be performed in a prod-like environment. The hostname will be:

    {BRANCH}-hosting-uapi.apps.provo1.endurancemb.com

For example if my branch name is HG1-123-fix-bug, it would be deployed to

    hg1-123-fix-bug.hosting-uapi.apps.provo1.endurancemb.com

You can point a UI to your alpha/branch instance in order to do testing before merging to beta.

## Configuration

Configs are located in ./config/dev and have default values set.

You can create a config/dev/overrides.json. To override HAL url set it to


    {
        "hal": {
            "host": "your_url"
        }
    }

You can also set HAL_HOST=your_url in env variable.


## Deployment

### [CICD](https://jenkins-jenkins-hosting.apps.provo1.endurancemb.com/blue/organizations/jenkins/hosting-uapi/activity)

Jenkins Server

### [Alpha](https://console-openshift-console.apps.provo1.endurancemb.com/k8s/cluster/projects/hosting-uapi-alpha)

Branches are auto-deployed and tested here when pushed to stash. Uses HAL Beta.

### [Beta](https://console-openshift-console.apps.provo1.endurancemb.com/k8s/cluster/projects/hosting-uapi-beta)

The Beta deployment runs the beta branch and is connected to HAL Beta.

This namespace also contains **Staging** deployment. This deployment runs on the main branch, and is where tests are run before every deploy to production.

### [Prod](https://console-openshift-console.apps.provo1.endurancemb.com/k8s/cluster/projects/hosting-uapi-prod)

NOTE: Prod is not yet setup.


## Links

### [Confluence](https://confluence.newfold.com/display/EIGHAL/Hosting+UAPI)

## Troubleshooting

### ModuleNotFoundError: No module named ''

If the error is in Jenkins on your branch, make sure you added your new dependency with `pipenv install` (see instructions above).
Otherwise rebuild docker image with `docker/build`

## Extra

### Pipenv update check

To see which modules need updates

    pipenv update --outdated 2>/dev/null

Then to perform the update

    pipenv update

## Makefile Usage

Run `make test` to start the local HUAPI server (docker container),
and run all the tests.

Use this Makefile to do various actions with this repository.
It can start and stop the HUAPI server Docker container.
It (re)builds the Docker image if needed.
Actions that require the server will start it if needed.

## Set Configs
```
export HAL_URL="your hal url"
export HAL_SECRET="your hal secret"
```
## Makefile Targets

### Local Setup

* `make setup`

  Install `pipenv` for Python dependency management.
  This is only required if you need to add new deps or would like to run
  locally.
  Otherwise you can use the docker container.

* Installing New Dependencies

      pipenv install <pip_module>

  This command works the same as pip, except it will also add the new
  dependency to Pipfile and regenerate Pipfile.lock.
  Both Pipfile and Pipfile.lock should be committed to git.

### Testing Targets

* `make test`

  Runs `make test-pytest` in non-noisy mode.

* `make test-all`

  Runs `make test-pytest test-demo`.

* `make test-pytest` or `make pytest`

  Run pytest tests in container in `-s` noisy mode.

* `make test-demo`

  Run curl demo tests.

* `make test-ftp-create`

  Test creating new ftp account.

* `make test-ftp-list`

  Test listing ftp accounts.

### Docker HUAPI Server Targets

* `make build`

  (Re)Build the 'huapi' Docker image.
  This normally happens automatically when the image is needed.

* `make start`

  Run the 'huapi' Docker server container.
  The container is automatically started if needed by the `test-*` rules.

* `make stop`

  Stop/kill the Docker server container.

* `make status`

  Show if the Docker server is running or not.

* `make shell`

  Start a Bash shell inside the running server container.
  Command history is preserved between sessions.

### Other Targets

* `make hook`

  Sets up git hooks like pre-commit to make sure you don't commit simple
  mistakes.

  Runs: `./bin/huapi-git-enable-hooks`

* `make unhook`

  Sometimes you need to commit even when hooks fail.
  This command will remove the hooks until you run `make hook` again.

  Runs: `./bin/huapi-git-disable-hooks`

* `make pre-commit`

  Run the `pre-commit` hook without running `git commit`.

* `make help`

  Show this help.

* `make README.md`

  The README.md file is generated.
  If you want to update it, change either `doc/help.md` or `Makefile` (which
  cantains Markdown comments inline).
  You need to run `make help` (or `make README.md man/man1/huapi.1`) to
  update the generated files.

* `make clean`

  Remove all generated files.
  This will also stop the server container if it is running.

## TODO

* Add rules to deploy to openshift with Makefile
* Fix failures for `make test-pytest`
