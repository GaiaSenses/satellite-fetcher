class ValidationError(Exception):
    def __init__(self, body, *args: object) -> None:
        super().__init__(*args)
        self.body = body


def handle_validation_error(err):
    return err.body, 400
