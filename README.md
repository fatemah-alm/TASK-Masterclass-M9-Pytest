# Pytest

Is my code working as intended?

## Setup

1. Fork and clone [this repository](https://github.com/JoinCODED/TASK-Masterclass-M9-Pytest).
2. Make sure to have `python 3.9.10` installed (use `pyenv install 3.9.10` to ensure it is installed).
3. Install the project dependencies using `poetry install`.
4. Run the migrations using `poetry run manage migrate`.

## Configuration

1. Install `python-decouple` and `dj_database_url` using poetry add `poetry add python-decouple dj_database_url`.
2. Update your django settings.
   1. Change `DEBUG` to read from the environment variables and default to `False`.
   2. Update your secret key to read from your environment variables (do not default to anything).
   3. Set up your database to connect to your postgres database.
      - Create a local database by entering `psql` (run `psql` in your terminal).
        - If this command does not work, it is usually because you have a hyphen in your computer name so you must do `psql your_computer_name`, where each underscore is where a hyphen would've been. If you are stuck, do `psql -l` to see the list of available databases on your machine.
      - Run `CREATE DATABASE recipes;` to create a database called `recipes`.
      - Connect to your newly created database in django, using `dj_database_url` (do not add a default, we want to fail if no database is set up).
3. Add a `.env` file:
   - Add `DEBUG` to be `True`.
   - Add a `SECRET_KEY` (use `openssl rand -hex 32` to generate a key).
   - Add your database url.
