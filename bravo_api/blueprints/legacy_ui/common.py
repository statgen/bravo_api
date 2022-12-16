from webargs.flaskparser import FlaskParser
from marshmallow import EXCLUDE

# Error message for argument validation
ERR_EMPTY_MSG = {'invalid_string': 'String must not be empty.'}
ERR_GT_ZERO_MSG = {'invalid_value': 'Value must be greater than 0.'}
ERR_START_STOP_MSG = {'invalid_start_stop': 'Start value must be less than stop value.'}
ERR_CONTINUE_STOP_MSG = {'invalid_continue_stop':
                         'Continue from value must be less than stop value.'}


# Parser to exclude extra parameters passed in json bodies.
#   Accomodate extraneous pagination and other extra args from BraVue.
class Parser(FlaskParser):
    DEFAULT_UNKNOWN_BY_LOCATION = {"json": EXCLUDE}
