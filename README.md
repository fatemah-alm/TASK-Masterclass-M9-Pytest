# Pytest

Is my code working as intended?

## Setup

1. Fork and clone [this repository](https://github.com/JoinCODED/TASK-Masterclass-M9-Pytest).
2. Make sure to have `python 3.9.10` installed (use `pyenv install 3.9.10` to ensure it is installed).
3. Install the project dependencies using `poetry install`.
4. Run the migrations using `poetry run manage migrate`.

## Configuration

1. Install `python-decouple`, `psycopg2`, and `dj-database-url` using `poetry add python-decouple dj-database-url`.
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

## Query Tests

1. Add a `conftest.py` in the root of your project.
2. Add a `client_query` fixture (have a look [here](https://docs.graphene-python.org/projects/django/en/latest/testing/#using-pytest)).
3. Add a fixture for a cuisine inside `food/tests.py`.
   - Do not forget to mark its DB usage (i.e., `@pytest.mark.django_db`).
4. Test that querying for a single cuisine with your `cuisine id` (use the fixture to retrieve the id) matches your response.
5. Test that querying for all cuisines has your `cuisine` fixture in the response.

## Mutation Tests

1. Install `hypothesis` using `poetry add 'hypothesis[django]'`.
2. Add a string strategy for `name` and `origin`.
3. Test the `CreateIngredient` mutation works with the `name` and `origin` supplied.

## Mutation Tests Bonus

1. Add an `Ingredient` fixture in `food/tests.py`.
2. Use `hypothesis` to generate random `name` and `steps`.
3. Test that the `UpdateIngredient` mutation has the new `name` and `steps` generated, but all the other attributes match what was in the fixture.

## File Upload Tests

1. Update your `client_query` fixture so that it uses `file_graphql_query` if `files` was passed in `kwargs`, otherwise use `graphql_query` like before.
2. Add a mutation test for `CreateCuisine` that:
   - Checks if passing in a `banner` returns a `banner` in the response.
   - Checks that omitting `banner` returns `None` in the response for `banner`.

**HINT:** Remember to use `SimpleUploadedFile` imported from `django.core.files.uploadedfile` to generate your files.
