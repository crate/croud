=================
Changes for croud
=================

Unreleased
==========

- Added subcommand `me` that allows to print info about the current
  logged-in user.

- Added subcommand `login` that allows to login to https://cratedb.cloud
  using OAuth. It will open a browser to start the authentication process.

- Added a subcommand `logout` that clears the stored login token, and clears the OAuth session

- The environment used to logged to in is now stored in config, so it is only necessary to provide the ``--env`` flag on the ``login`` subcommand
