import logging
from flask_restful import Resource
from flask import request
from werkzeug.exceptions import HTTPException
from jsonschema import Draft4Validator
from lib.schema import JsonSchema


def exception_guard(method):
    """
    Exception guard catches all unhanhled exceptions thrown when processing the method and formats them to valid JSON.
     This avoids generic error messages.
    :param method: Method to wrap.
    :return: Wrapper for the method that catches the exceptions.
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper that catches exceptions.
        """
        try:
            return method(*args, **kwargs)
        except HTTPException as e:
            logging.exception("Method %s failed with exception %r" % (method.__qualname__, e, ))
            return {
                "error": str(e.description)
            }, e.code
        except Exception as e:
            logging.exception("Method %s failed with exception %r" % (method.__qualname__, e, ))
            return {
                "error": str(e)
            }, 500
    return wrapper


class SafeResource(Resource):
    """
    Resource that is wrapped in exception_guard automatically. That means, that any exception thrown when executing
    the API call will be formatted to JSON.
    """
    def __init__(self):
        super(SafeResource, self).__init__()
        self.method_decorators.append(exception_guard)


def validate_input(schema: JsonSchema):
    """
    Decorator. Input JSON params validation. By specifying this decorator, you are also telling, that the request
    should contain JSON payload, that validates against specified schema.
    :param schema: Schema to validate against.
    """
    built_schema = schema()
    Draft4Validator.check_schema(built_schema)

    v = Draft4Validator(built_schema)

    def input_decorator(method):
        """
        Decorator that uses parametrized validator to validate input json params.
        """
        def wrapper(*args, **kwargs):
            """
            Wrapper that validates input JSON params and only proceeds with the method execution if they are valid.
            """
            errors = {
                "input.%s" % (".".join(map(str, error.absolute_path)), ): error.message
                for error in v.iter_errors(request.json)
            }
            if not errors:
                return method(*args, **kwargs)
            else:
                return errors, 400
        return wrapper
    return input_decorator


def validate_response(schema: JsonSchema):
    """
    Decorator. Output response validation.
    :param schema: Schema to validate against.
    """
    built_schema = schema()
    Draft4Validator.check_schema(built_schema)

    v = Draft4Validator(built_schema)

    def output_decorator(method):
        """
        Decorator uses parametrized validator to validate output JSON params. Only validates if status=2**.
        """
        def wrapper(*args, **kwargs):
            """
            Wrapper that validates output of method agains specified JSON schema. Only validates if method returns
            HTTP status=200, otherwise, it passes the response directly.
            """
            status = 200
            response = method(*args, **kwargs)

            if isinstance(response, tuple):
                response = response[0]
                status = response[1]

            if status / 100 != 2:
                return response, status
            else:
                errors = {
                    "response.%s" % (".".join(map(str, error.absolute_path)), ): error.message
                    for error in v.iter_errors(response)
                }
                if not errors:
                    return response, status
                else:
                    return errors, 400
        return wrapper
    return output_decorator
