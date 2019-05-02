from croud.__main__ import command_tree
from croud.cmd import CMD


class CommandTestCase:
    croud = CMD(command_tree)

    def assertGql(self, mock_run, argv, expected_body, expected_vars=None):
        func, args = self.croud.resolve(argv)
        func(args)
        mock_run.assert_called_once_with(expected_body, expected_vars)

    def assertRest(self, mock_send, argv, method, endpoint, body=None):
        func, args = self.croud.resolve(argv)
        func(args)

        params = [method, endpoint]
        if body is not None:
            params.append(body)
        mock_send.assert_called_once_with(*params)
