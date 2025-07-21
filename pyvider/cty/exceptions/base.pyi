from _typeshed import Incomplete

class CtyError(Exception):
    message: Incomplete
    def __init__(self, message: str = 'An error occurred in the cty type system') -> None: ...

class CtyFunctionError(CtyError):
    def __init__(self, message: str = 'An error occurred during CTY function execution') -> None: ...
