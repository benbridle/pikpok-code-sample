# Code sample for Ben Bridle

The code is for the login and account-management section of a work-in-progress MMO game called Doctrine. 

## Setup

To create the user and empty database for Doctrine, run `sudo mysql -N < scripts/create_user_and_database.sql` in the project root.

## Usage

Run `./start_app` in the project root to start serving the app with gunicorn. Navigate to `localhost:8004` in a browser to access the user-facing website, or access the JSON API via `localhost:8004/api/...`