# FI-API
FI-API is a RESTful interface to the command line [FI library written in Python](https://github.com/bbusenius/FI). It dynamically generates JSON endpoints for all functions in the [FI module](https://github.com/bbusenius/FI). When a new function is added to the FI module it is automatically reflected in this repository and should be reachable as a new JSON endpoint.

## Installation

```
git clone https://github.com/bbusenius/FI-API.git
```

## Development

### Install the requirements
Create a virtual env and install the requirements with:

```
pip install -r requirements.txt
```

### Run the Flask app

```
env FLASK_APP=app.py flask run
```
Visit the site at http://127.0.0.1:5000

## Run with Docker
### Build

```
docker build --no-cache -t ubuntu-fi-api .
```
### Run

```
docker run -d -p 1337:80 ubuntu-fi-api
```

You should now see the site at http://localhost:1337

## Example API Calls (running in Docker)

Get a list of possible endpoints:

http://localhost:1337/json/

Example API call:

http://localhost:1337/json/savings_rate?take_home_pay=6500&spending=1900

Returns:

```
70.76923076923077
```
