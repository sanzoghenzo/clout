class DesertException(Exception):
    pass


class ValidationError(DesertException):
    pass


class MissingInput(DesertException):
    def __init__(self, group, string, found):
        self.group = group
        self.string = string
        self.found = found

    def __str__(self):
        return f"Parsing fails at {self.found}"
