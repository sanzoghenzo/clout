import click
import click._compat


class CloutException(Exception):
    pass


class ValidationError(CloutException):
    pass


class MissingInput(CloutException):
    def __init__(self, group, string, found):
        self.group = group
        self.string = string
        self.found = found

    def __str__(self):
        return f"Parsing fails at {self.found}"


class UsageError(CloutException):
    """An internal exception that signals a usage error.  This typically
    aborts any further handling.

    :param message: the error message to display.
    :param ctx: optionally the context that caused this error.  Click will
                fill in the context automatically in some situations.
    """

    exit_code = 2

    def __init__(self, message, ctx=None):
        super().__init__(self, message)
        self.ctx = ctx
        self.cmd = self.ctx.command if self.ctx else None

    def show(self, file=None):
        if file is None:
            file = click._compat.get_text_stderr()
        color = None
        hint = ""
        if self.cmd is not None and self.cmd.get_help_option(self.ctx) is not None:
            hint = 'Try "%s %s" for help.\n' % (
                self.ctx.command_path,
                self.ctx.help_option_names[0],
            )
        if self.ctx is not None:
            color = self.ctx.color
            click.echo(self.ctx.get_usage() + "\n%s" % hint, file=file, color=color)
        click.echo("Error: %s" % self.format_message(), file=file, color=color)
