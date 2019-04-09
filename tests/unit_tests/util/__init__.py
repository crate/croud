from croud.__main__ import command_tree
from croud.cmd import CMD


class CommandTestCase:
    croud = CMD(command_tree)

    def assertGql(self, mock_run, argv, expected_body, expected_vars=None):
        func, args = self.croud.resolve(argv)
        func(args)
        mock_run.assert_called_once_with(expected_body, expected_vars)

    def assertREST(
        self,
        mock_run,
        mock_init,
        argv,
        expected_method,
        expected_endpoint,
        expected_params,
    ):
        func, args = self.croud.resolve(argv)
        func(args)
        mock_run.assert_called_once_with(expected_params)
        mock_init.assert_called_once_with(args, expected_method, expected_endpoint)
