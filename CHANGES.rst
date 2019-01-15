=================
Changes for croud
=================

Unreleased
==========

0.4.0 - 2018/01/15
==================

- Added `users roles add` sub command that assigns a role to user (super users only).

- Fixed `config get output-fmt` command

- Added `organizations list` sub command that lists organizations

- Removed region arg from `me` command

- Added `organizations create` sub command that creates an organization (super users only)

0.3.0 - 2018/01/09
==================

- SECURITY: prevented arbitrary code execution when loading the config file
  (ref. `CVE-2017-18342 <https://nvd.nist.gov/vuln/detail/CVE-2017-18342>`_)

- Fix: Login page needs to be picked according to the env set in current_context.

- Removed `env` subcommand (replaced with `config set --env [prod|env]`)

- Added subcommand `config get` that prints out a specified default config setting

- Added subcommand `config set` that sets a specified default config setting

0.2.1 - 2018/12/12
==================

- Fixed `ModuleNotFoundError`.

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
