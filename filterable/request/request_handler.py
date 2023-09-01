class AppHelper:
    """
    Factory helper workaround to handle requests
    out of a controller context """

    __request = None

    @staticmethod
    def request():
        if AppHelper.__request == None:
            try:
                from flask import request
                AppHelper.__request = request
            except ImportError as e:
                pass 
        return AppHelper.__request

    @staticmethod
    def inject_request(request) -> None:
        AppHelper.__request = request
