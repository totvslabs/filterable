class FilteringException(Exception):
    """Base Exception class raised for malformed filters
    """

    def __init__(self, error):
        self.message = error
        super().__init__(self.message)
