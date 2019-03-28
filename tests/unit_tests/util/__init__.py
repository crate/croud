import argparse

from croud.__main__ import get_parser


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

    def assertRest(self, mock_send, argv, method, endpoint, body=None):
        self.execute(argv)
        mock_send.assert_called_once_with(method, endpoint, body)
