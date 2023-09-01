from filterable.exceptions import NoRequestContextException

class RequestHandler:
    """
    Factory helper workaround to handle requests
    out of a controller context """

    __request = None

    @staticmethod
    def request() -> any:
        """Get the current request context if available."""
        if RequestHandler.__request == None:
            # If request context wasn't provided previously, try to recover it from somewhere
            RequestHandler.__request = RequestHandler.__recovery_request()
        return RequestHandler.__request

    @staticmethod
    def inject_request(request) -> None:
        """
        Inject a request object into the RequestHandler.

        Args:
            request: The request object to inject.
        """
        RequestHandler.__request = request
        
    @staticmethod
    def __recovery_request() -> any:
        """
        Attempt to recover the request object, typically from a web framework like Flask.

        Returns:
            The recovered request object.
        
        Raises:
            NoRequestContextException: If no request context can be found.
        """
        try:
            # Try to load Flask
            from flask import request
            # Base Flask installed, it's possible to get request context from it!
            return request
        except ImportError:
            raise NoRequestContextException()
