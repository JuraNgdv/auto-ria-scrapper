
class MissingRequiredField(Exception):
    def __init__(self, field_name: str, message: str = None):
        if message is None:
            message = f"Required field '{field_name}' is missing."
        super().__init__(message)
        self.field_name = field_name
