# EBcL SDK Tests

This folder contains the EBcL SDK tests, written using the Robot Framework.

## Prepare the test enviroment

To prepare the test environment, change to the root folder of this repository and:

- prepare a Python environment: `python3 -m venv .venv`
- activate the environment: `source .venv/bin/activate`
- install the dependencies: `pip install -r requirements.txt`

## Run the tests

When the test environment is available, you can run the tests with `robot test`.

Please be aware that the image build tests run multiple hours.
