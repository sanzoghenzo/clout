import ast
import functools
import typing as t

import attr
import jedi
import pygments
import pygments.formatters
import pygments.lexers
import sphinx.ext.intersphinx
import sphinx.highlighting


@attr.dataclass
class Pair:
    type: pygments.token._TokenType
    code: str
    link: t.Optional[str] = None

    def __iter__(self):
        yield from attr.astuple(self)[:2]


class LinkingPython3Lexer(pygments.lexers.Python3Lexer):
    def __init__(self, *args, app: sphinx.application.Sphinx, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def get_tokens(self, text: str, unfiltered: bool = False):
        tokens = super().get_tokens(text, unfiltered=unfiltered)
        import q

        try:
            _ = ast.parse(text)
        except SyntaxError:
            return tokens
        import q

        q(text)
        line = 1
        column = 0
        for token_type, code in tokens:

            script = jedi.Script(text, line, column)
            try:
                defs = script.goto_definitions()
            except:
                name = "FOO"
            else:
                name = defs[0].full_name if defs else None

            link = f"https://zombo.com/{name}"

            yield (token_type, code.upper())
            line += code.count("\n")
            if code.endswith("\n"):
                column = 0


def setup(app, **kw):
    sphinx.highlighting.lexer_classes["python3"] = functools.partial(
        LinkingPython3Lexer, app=app
    )
    # sphinx.highlighting.HtmlFormatter = LinkingHtmlFormatter
    # sphinx.highlighting.PygmentsBridge.html_formatter = LinkingHtmlFormatter
