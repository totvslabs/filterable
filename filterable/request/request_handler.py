from filterable.exceptions import NoRequestContextException

class RequestHandler:
    """
    Factory helper workaround to handle requests
    out of a controller context """

    __request = None

    @staticmethod
    def request():
        if RequestHandler.__request == None:
            try:
                from flask import request
                RequestHandler.__request = request
            except ImportError as e:
                raise NoRequestContextException()
        return RequestHandler.__request

    @staticmethod
    def inject_request(request) -> None:
        RequestHandler.__request = request
