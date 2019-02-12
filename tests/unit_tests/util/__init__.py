from croud.__main__ import command_tree
from croud.cmd import CMD


class CommandTestCase:
    croud = CMD(command_tree)

    def assertGql(self, mock_run, argv, expected_body, expected_vars):
        func, args = self.croud.resolve(argv)
        func(args)
        mock_run.assert_called_once_with(expected_body, expected_vars)
