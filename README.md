# Bravo API

The server side application of the BRowse All Variants Online (BRAVO) project.

## Installation
For running an instance of Bravo API, install as a package.
```
python -m pip install git+https://github.com/statgen/bravo_api.git@main
```
See [Development](#Development) section for developer installation.

## Dependencies

### Data

### Document Store (Mongo)

## Development
Checkout and install as editable package with development and testing extras.
```
git clone https://github.com/statgen/bravo_api.git
cd bravo_api
python -m pip install -e .[dev,test]
```

### Testing
When installed as editable package, run `pytest` from root dir or anywhere in tests dir.

```
# Run the tests
pytest
```

Top level testconf.py in the tests directory prevents marked tests from running.
In order to run marked tests in addition to the unmarked, provide a match expression.

```
# Run integration tests
pytest -m 'integration'
```

#### Autorunning tests
A low overhead (not constantly polling) method of running `pytest` anytime a .py file is changed
can be achieved using `fd` and `entr` in a separate terminal.
Only thing this won't pick up is new files.

```sh
fd '.*\.py$' | entr -c pytest
```

See [notes.md](notes.md)
