=================
Changes for croud
=================

Unreleased
==========


0.2.0 - 2018/12/12
==================

- Added subcommand `clusters list` that prints clusters from a region, and can be filtered by project ID

- Added subcommand `projects list` that prints project details within a specified region (for logged in user)

- Removed name field from `me` subcommand

- Added `env` flag to commands to temporarily override auth context

- Added a subcommand `env` that allows you to switch env (so you can be logged into multiple environments. E.g. ``croud env prod``

0.1.0 - 2018/11/28
==================

- Load croud commands from a ``croud_commands`` `entry points
  <https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins>`__
  section.

- Added a tabular format to the list of possible output formats in subcommands.

- Added subcommand `me` that allows to print info about the current
  logged-in user.

- Added subcommand `login` that allows to login to https://cratedb.cloud
  using OAuth. It will open a browser to start the authentication process.

- Added a subcommand `logout` that clears the stored login token, and clears the
  OAuth session

- The environment used to logged to in is now stored in config, so it is only
  necessary to provide the ``--env`` flag on the ``login`` subcommand
