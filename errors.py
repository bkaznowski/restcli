class UserError(Exception):
    """Raised when a user makes a mistake"""
    pass

class RequestError(Exception):
    """Raised when a call does not return a 200 response"""
    pass
