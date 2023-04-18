import re
from inspect import signature

import fi
from diablo_utils import cast_by_type, functs_from_mod
from flask import Flask, escape, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
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
        arg_to_pass = cast_by_type(request.args.get(arg_name), expected_type)
        fun_args.append(arg_to_pass)
    return (fail, fun_args)


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
        api[func] = {}
        for key in fun_params:
            api[func][key] = str(fun_params[key].annotation)
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
            return jsonify(function_to_call(*fun_args))


@app.route('/json/h/<fun_name>')
def help_json_endpoint(fun_name):
    """
    Help endpoint for the JSON API.
    """
    fun_name = escape(fun_name)
    print(fun_name)
    # Invalid endpoint
    if fun_name not in FUN_DICT:
        msg = 'Not a valid endpoint. Only the following endpoints are allowed'
        return error_msg(400, msg, list(FUN_DICT.keys()))
    # Help endpoint
    else:
        function_to_call = FUN_DICT[fun_name]
        text = function_to_call.__doc__
        clean_text = re.sub('\\s+', ' ', text).strip()
        formatted_text = clean_text.replace('Args: ', '\n\nArgs:\n').replace(
            'Returns: ', '\n\nReturns:\n'
        )
        return jsonify(formatted_text)
