import re
from decimal import ROUND_HALF_UP, Decimal
from inspect import signature

import fi
from diablo_utils import cast_by_type, functs_from_mod
from flask import Flask, escape, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
# This might need to change to app.json.sort_keys = False in Flask 2.3 or later
app.config['JSON_SORT_KEYS'] = False
CORS(app)

if __name__ == '__main__':
    app.run()

# All functions from the FI library
FUN_DICT = functs_from_mod(fi)


def error_msg(code: int, msg: str, required: list) -> str:
    """
    Generate an error message to display.

    Args:
        code: Numeric code

        msg:  Message

        required: list of allowed or required items

    Returns:
        Error message formatted as JSON.
    """
    retval = {'error': {'code': code, 'message': {msg: required}}}
    return jsonify(retval)


def get_mod_func_args(fun_params):
    """
    Retrieves function arguments from a GET request and casts them to their
    expected data types for a given module.

    Args:
        fun_params: parameters from an inspect.signature.

    Returns:
        A tuple where the first item is a boolean and the second item is a
        list of mixed data types to pass to a function. The boolean will be
        set to True if an expected argument is missing. This is considered
        a fail.
    """
    fun_args = []
    fail = False
    for key in fun_params.keys():
        arg_name = fun_params[key].name
        arg_passed = request.args.get(arg_name)
        if arg_passed is None:
            fail = True
            break
        expected_type = str(fun_params[key].annotation)
        is_literal = expected_type[0:14] == 'typing.Literal'
        if is_literal:
            arg_to_pass = str(request.args.get(arg_name))
        else:
            arg_to_pass = cast_by_type(request.args.get(arg_name), expected_type)
        fun_args.append(arg_to_pass)
    return (fail, fun_args)


def clean_doc(text):
    """
    Attempt to format docstrings.

    Args:
        text: string, docstring.

    Returns:
        Docstring that's more appropriate for display on a webpage.
    """
    clean_text = re.sub('\\s+', ' ', text).strip()
    pattern = r'\b(?!Credit:|https?:|by:|Mustache:|article:)\w+:'
    cleaner_text = re.sub(pattern, '\n\\g<0>', clean_text)
    formatted_text = cleaner_text.replace('Args: ', '\nArgs:').replace(
        'Returns: ', '\nReturns:\n'
    )
    return formatted_text


def beautiful(text):
    """
    Add HTML formatting to a docstring.

    Args:
        text: string, docstring.

    Returns:
        Beautiful docstring.
    """
    text = text.replace('Args:', '<h3>Args:</h3>')
    text = text.replace('Returns:', '<h3>Returns:</h3>')
    pattern = r'(?<=\n)\w+:'
    replacement = r'<strong>\g<0></strong>'
    text = re.sub(pattern, replacement, text)
    url_regex = re.compile(r'(https?://\S+)')
    text = url_regex.sub(r'<a href="\1">\1</a>', text)
    return f'<h3>Usage:</h3>\n{text}'


@app.route('/')
def home():
    """
    Homepage route.
    """
    return render_template('home.html')


@app.route('/json/')
def json_home():
    """
    JSON API home route.
    """
    api = {}
    for func in FUN_DICT:
        fun_params = signature(FUN_DICT[func]).parameters
        api[func] = {'args': {}, 'return_type': ''}
        for key in fun_params:
            api[func]['args'][key] = (
                str(fun_params[key].annotation),
                str(fun_params[key].default),
            )
        api[func]['return_type'] = str(signature(FUN_DICT[func]).return_annotation)
    return jsonify({'Available API Endpoints': api})


@app.route('/json/<fun_name>')
def api_json_endpoints(fun_name):
    """
    Endpoints for the JSON API.
    """
    fun_name = escape(fun_name)
    # Invalid endpoint
    if fun_name not in FUN_DICT:
        msg = 'Not a valid endpoint. Only the following endpoints are allowed'
        return error_msg(400, msg, list(FUN_DICT.keys()))
    # All good
    else:
        # Function from the FI library
        function_to_call = FUN_DICT[fun_name]
        fun_params = signature(function_to_call).parameters
        fail, fun_args = get_mod_func_args(fun_params)
        # Fail - missing GET params
        if fail:
            msg = 'You did not pass all of the required GET parameters. The following are required'
            return error_msg(400, msg, list(fun_params.keys()))
        # Success! Call the library function and jsonify the result
        else:
            rnd = request.args.get('round')
            fun = function_to_call(*fun_args)
            if rnd:
                try:
                    places = Decimal(10) ** -Decimal(rnd)
                    val = Decimal(fun).quantize(places, ROUND_HALF_UP).normalize()
                    if val % 1 == 0:
                        val = int(val)
                    # jsonify always returns a string for Decimals. Rather than
                    # convert Decimals to floats, converting all values to strings
                    # allows us to preserve accuracy and always return the same
                    # type (instead of sometimes ints, sometimes, floats, and
                    # sometimes strings).
                    return jsonify(str(val))
                except (TypeError):
                    # Happens with the big bank redeem points function which
                    # returns a dict and is a little different from the others.
                    return jsonify(fun)
            return jsonify(str(fun))


@app.route('/json/h/')
def all_help_json_endpoint():
    """
    Help endpoint for the JSON API.
    """
    is_beautiful = request.args.get('html') == 'true'

    # Help for all functions
    retval = {}
    for fun in FUN_DICT:
        text = clean_doc(FUN_DICT[fun].__doc__)
        if is_beautiful:
            text = beautiful(text)
        retval[fun] = text
    return jsonify(retval)


@app.route('/json/h/<fun_name>')
def help_json_endpoint(fun_name):
    """
    Help endpoint for the JSON API.
    """
    fun_name = escape(fun_name)
    # Invalid endpoint
    if fun_name not in FUN_DICT:
        msg = 'Not a valid endpoint. Only the following endpoints are allowed'
        return error_msg(400, msg, list(FUN_DICT.keys()))
    # Help endpoint
    else:
        function_to_call = FUN_DICT[fun_name]
        text = function_to_call.__doc__
        return jsonify(clean_doc(text))
