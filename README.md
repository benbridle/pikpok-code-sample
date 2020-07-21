# Code sample for Ben Bridle

Note: a live demo of this code sample can be accessed by visiting http://doctrine.benbridle.com

![Screenshot of the Doctrine account dashboard](https://github.com/benbridle/pikpok-code-sample/blob/master/images/dashboard.png?raw=true)

## Background

This code sample contains a work-in-progress Web API and account management website for an MMO game called Doctrine that is in early development.

The code sample includes a Web API written using Python with Flask and SQLAlchemy, an SQL database using MySQL, a web app using HTML, CSS, and Javascript, and tests written with Pytest.

## Setup

### Installing system dependencies 
For database access, Doctrine requires the `mysql-server` system package to be installed on the target system. The `build-essential`, `python3-dev`, `python3-venv`, and `libmysqlclient-dev` system packages will also need to be installed in order to compile the required python packages in the next step.

Install these system packages by running:
```
sudo apt update
sudo apt install mysql-server build-essential python3-dev python3-venv libmysqlclient-dev
```

### Installing python dependencies
Enter the project root directory, and then create a virtual environment named `venv` by running: 

```
python3 -m venv venv
```

To install all required python packages into the virtual environment, run:
```
. venv/bin/activate
pip3 install wheel
pip3 install -r requirements.txt
```

(Note: `wheel` must be installed _before_ the rest of the requirements in order to prevent installation errors with `mysqlclient`)

Before the server is first run, the MySQL database, tables, and user will need to be created by running:
```
./initialise_database
```

### (Optional) Serving the application using nginx

Install `nginx` and `supervisor` by running:

```
sudo apt update
sudo apt install nginx supervisor
```

Generate self-signed certificates by running:

```
./scripts/generate-certificates
```

Edit the .`flaskenv` file in the project root directory, removing the `FLASK_ENV=development` line. 

Edit the nginx and supervisor configuration files in `/config` to match your situation. For example, in the nginx configuration file you'll want to replace the `server_name` directive with the domain that points to your server, and in the supervisor configuration file you'll want to change the project directory and user to match the directory path and user name on your server.

Make symbolic links between the configuration files and the nginx/supervisor configuration directories by running:
```
sudo ln -s $PWD/config/nginx.conf /etc/nginx/sites-enabled/doctrine.conf
sudo ln -s $PWD/config/supervisor.conf /etc/supervisor/conf.d/doctrine.conf
```

To finish, restart nginx and supervisor in order to load the new configuration files by running:

```
sudo service nginx restart
sudo service supervisor restart
```

## Usage
(Optional) To run the test suite, run:

```
./run_tests
```

To begin serving the application locally, run:

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
- Improve the website user interface on mobile devices.