from mimetypes import init


class Command:
    def __init__(self, command: str, value: int) -> None:
        self._command = command
        self._value = value
