# Tournaments Organizer
Simple Flask Website to Help Organize Single Elimination Competitions

List of Available Pages And Functionalities
* `'/'`: placeholder for the index page
* `'/add_competitors'`: registrate new competitors
* `'/round'`: see the competition matchup for each round
* `'/round_summary'`: see the summary of all the rounds

Since this will be a prototype that will be continually built upon, the following is also included:
* `Dockerfile`: for future deployment
* `.travis.yml`: continuous integration
* `integration_test`: integration tests for the application

Future Improvements:
* `/round` page still needs significant improvement. Currently, after users submitted the form, they need to manually click go back to keep entering infos
* `add_competitor` form hasn't handle situations when entering competitors with the same name
* Better displays

## Run Virtual Environment

Virtual environment is a key component in ensuring that the application is configured in the right environment

##### Requirements
* Python 3
* Pip 3

##### Installation
To install virtualenv via pip run:
```bash
$ pip3 install virtualenv
```

##### Usage
Creation of virtualenv:

    $ virtualenv -p python3 venv

If the above code does not work, you could also do

    $ python3 -m venv venv

To activate the virtualenv:

    $ source venv/bin/activate

Install dependencies in virtual environment:

    $ pip3 install -r requirements.txt

## Environment Variables

The environment variables are stored within the `.env` file and loaded with dotenv package.

IMPORTANT: I didn't put my `.env` file here as it contains sensitive information. You need to create a `.env` file in the root directory and I will send the content with the email

## Run Application

Start the server by running:

    $ export FLASK_ENV=development
    $ python3 -m flask run
    
