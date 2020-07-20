# Code sample for Ben Bridle

Note: a live demo of this code sample can be accessed by visiting http://doctrine.benbridle.com

## Background

This code sample contains the current Web API and account management website for an MMO game called Doctrine that is in early development. In Doctrine, players will construct and pilot remotely-controlled vehicles in order to explore a post-apocalyptic Earth, scavenge for resources, work together to construct sprawling bases, and fight back against the relentless expansion of a rampant artificial intelligence.

The code sample includes a Web API written using Python with Flask and SQLAlchemy, an SQL database using MySQL, a web app using HTML, CSS, and Javascript, and tests written with pytest.

## Setup
### Installing system dependencies
For database access, Doctrine requires both the `mysql-server` and `libmysqlclient-dev` system packages to be installed on the target system. 

Install these by running:
```
sudo apt install mysql-server libmysqlclient-dev
```

### Installing python dependencies
First, create a virtual environment named `venv` in the project root directory by running: 

```
python3 -m venv venv
```

To install all required python packages into the virtual environment, run:
```
. venv/bin/activate
pip3 install wheel
pip3 install -r requirements.txt
```

(Note: `wheel` must be manually installed before installing the rest of the requirements in order to prevent installation errors with `mysqlclient`)

Before the server is first run, the MySQL database, tables, and user need to be created by running:
```
./initialise_database
```



## Usage
To begin serving the application, run:

```
./start_server
```

Open a web browser and navigate to `localhost:8004/` to use the application. 

The Web API can be interacted with directly by visiting `localhost:8004/api/{endpoint}`. See `app/routes/api.py` for available endpoints.

## Known bugs

- On Google Chrome, using autofill in the 'Create account' and 'Login' forms changes the font.

## Future work

- Create tests for the web dashboard using Selenium.
- Add functionality to interact with profiles inside the account dashboard.
- Get the test suite to shut down the Flask server more elegantly