# tap-zohosprints

`tap-zohosprints` is a Singer tap for ZohoSprints.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

- [ ] `Developer TODO:` Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

```bash
pipx install tap-zohosprints
```

## Configuration

### Accepted Config Options
```
api_url: (Required) #Example (no trailing slash) https://sprintsapi.zoho.com/zsapi
oauth_url: (Required) #Example (no tailing slash) https://accounts.zoho.com/oauth/v2/token
client_id: (Required) 
client_password: (Required)
refresh_token: (Required)
```

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-zohosprints --about
```
### Setup Authentication
We need to get a client ID and Secret to setup our tap
1. Goto https://api-console.zoho.com/ to create an API Client
1. Click Add Client
1. Create a "Self Client"
1. Keep the client id and client secret handy for setting up the tap/target
1. Generate a scoped code
    1. Click the Self client (in the api console)
    1. Generate Code tab
    1. Scope: ZohoSprints.teams.READ, ZohoSprints.projects.READ, ZohoSprints.epic.READ, ZohoSprints.sprints.READ, ZohoSprints.items.READ
    (Will get added to later)
    1. Time Duration: 10 minutes or so
    1. Create, save this code for the refresh token step below

### How to generate a refresh token
1. Use your favorite tool to do adhoc HTTP Requests (I'm going to use PostMan for these steps)
1. Create a post request to the URL: https://accounts.zoho.com/oauth/v2/token
1. In the Body of the request you will need these x-www-form-urlencoded values
    1. code: (Generated from the Self Client)
    1. client_id: (Generated from the Self Client steps)
    1. client_secret: (Genereated from the Self Client steps)
    1. redirect_uri: https://localhost.com (This value doesn't matter for our use case but the api requires it)
    1. grant_type: authorization_code
1. Copy the refresh_token that is generated for the tap

### Source Authentication and Authorization

- [ ] `Developer TODO:` If your tap requires special access on the source system, or any special authentication requirements, provide those here.

## Usage

You can easily run `tap-zohosprints` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-zohosprints --version
tap-zohosprints --help
tap-zohosprints --config CONFIG --discover > ./catalog.json
```

## Developer Resources

- [ ] `Developer TODO:` As a first step, scan the entire project for the text "`TODO:`" and complete any recommended steps, deleting the "TODO" references once completed.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_zohosprints/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-zohosprints` CLI interface directly using `poetry run`:

```bash
poetry run tap-zohosprints --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-zohosprints
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-zohosprints --version
# OR run a test `elt` pipeline:
meltano elt tap-zohosprints target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
