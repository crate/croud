import difflib
import re
from doctest import _ellipsis_match  # type: ignore
from functools import partial

from croud.__main__ import get_parser

normalize = partial(re.sub, r"\s+", "")

UNDEFINED = object()


def ndiff(actual: str, expected: str) -> str:
    engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
    diff = list(engine.compare(expected.splitlines(True), actual.splitlines(True)))
    return "\n".join(line.rstrip() for line in diff)


def assert_ellipsis_match(actual: str, expected: str) -> None:
    diff = ndiff(expected.strip(), actual.strip())
    equality = _ellipsis_match(normalize(expected.strip()), normalize(actual.strip()))
    assert equality, diff


class CommandTestCase:
    def execute(self, argv) -> None:
        parser = get_parser()
        params = parser.parse_args(argv[1:])
        if "resolver" in params:
            fn = params.resolver
            del params.resolver
            fn(params)
        else:
            parser.print_help()

    def assertRest(
        self, mock_send, argv, method, endpoint, *, body=UNDEFINED, params=UNDEFINED
    ):
        self.execute(argv)

        args = [method, endpoint]
        kwargs = {}
        if body is not UNDEFINED:
            kwargs["body"] = body
        if params is not UNDEFINED:
            kwargs["params"] = params
        mock_send.assert_called_once_with(*args, **kwargs)
