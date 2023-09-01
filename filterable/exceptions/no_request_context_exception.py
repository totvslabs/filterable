class NoRequestContextException(Exception):
    """Exception raised when the Filterable has no request context to handle 
        with the incoming args
    """

    def __init__(self, error = None):
        self.message = error if error else "No request context provided"
        super().__init__(self.message)
