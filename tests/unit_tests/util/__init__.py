import argparse
import difflib
import re
from doctest import _ellipsis_match  # type: ignore
from functools import partial

from croud.__main__ import get_parser

normalize = partial(re.sub, r"\s+", "")


def ndiff(actual: str, expected: str) -> str:
    engine = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
    diff = list(engine.compare(expected.splitlines(True), actual.splitlines(True)))
    return "\n".join(line.rstrip() for line in diff)


def assert_ellipsis_match(actual: str, expected: str) -> None:
    diff = ndiff(expected.strip(), actual.strip())
    equality = _ellipsis_match(normalize(expected.strip()), normalize(actual.strip()))
    assert equality, diff


class CommandTestCase:
    parser = get_parser()

    def parse(self, argv) -> argparse.Namespace:
        return self.parser.parse_args(argv[1:])

    def execute(self, argv) -> None:
        params = self.parse(argv)
        if "resolver" in params:
            fn = params.resolver
            del params.resolver
            fn(params)
        else:
            self.parser.print_help()

    def assertGql(self, mock_run, argv, expected_body, expected_vars=None):
        self.execute(argv)
        mock_run.assert_called_once_with(expected_body, expected_vars)

    def assertRest(self, mock_send, argv, method, endpoint, *, body=None, params=None):
        self.execute(argv)

        args = [method, endpoint]
        kwargs = {}
        if body is not None:
            kwargs["body"] = body
        if params is not None:
            kwargs["params"] = params
        mock_send.assert_called_once_with(*args, **kwargs)
