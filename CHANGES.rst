=================
Changes for croud
=================

Unreleased
==========

0.14.1 - 2019/07/04
===================

- Fixed a bug that caused commands to always use the access token from the
  ``current_context`` setting to be used, even though a context / environemnt
  had been passed via ``--env``.

0.14.0 - 2019/06/06
===================

- Added ``clusters upgrade`` command to update an existing cluster to a later
  version.

0.13.2 - 2019/06/04
===================

- Made the ``config set`` command print out a help when no attributes are set.

- Removed unneeded ``--project-id`` argument from ``clusters scale`` command.

- Fixed an issue that caused empty query results to print "Success" to
  the console instead of an empty table.

0.13.1 - 2019/05/29
===================

- Updated ``clusters delete`` documentation.

0.13.0 - 2019/05/28
===================

- Added ``clusters delete`` command to delete existing clusters.

- Added ``clusters scale`` command to scale existing clusters.

- Added ``consumers delete`` command to delete existing consumers.

- Added ``croud products list`` command to list all available products
  in the current region.

0.12.3 - 2019/05/28
===================

- Fixed region support in ``consumers edit`` command.

0.12.2 - 2019/05/24
===================

- Fix client session so it stores the refreshed access token in the
  configuration. This prevents the server from refreshing the access token sent
  by the client in case it was already expired.

0.12.1 - 2019/05/22
===================

- Removed the redundant printed error JSON from the error message,
  only the message is provided. When the message is not available,
  the full error JSON is then printed.

0.12.0 - 2019/05/21
===================

- Updated the API calls from the deprecated ``v1`` to ``v2``.

- Make the ``config get`` commands respect the output format option.

0.11.1 - 2019/05/02
===================

- Fixed API redirect and error response bug for ``monitoring grafana`` command.

0.11.0 - 2019/04/17
===================

- Added the commands ``monitoring grafana`` that can enable and
  disable Grafana dashboards for a project.

0.10.0 - 2019/04/01
===================

- Added the commands ``consumers deploy``, ``consumers list`` and
  ``consumers edit``. The ``deploy`` command deploys a new consumer,
  the ``edit`` command edits an existing consumer and the ``list``
  command lists existing consumers.

- [Breaking] Removed the commands ``product deploy``, ``consumer-sets list``
  and ``consumer-sets edit``.

0.9.0 - 2019/03/20
==================

- Added ``clusters deploy`` command that allows users to deploy a new
  CrateDB cluster.

- Make ``--org-id`` and ``--no-org`` arguments mutually exclusive for the
  ``users list`` command and print an error if both arguments are provided.

- Refactored removing users from organizations commands to parse the
  ``user`` argument so that users can be removed via their email address
  or user ID.

0.8.1 - 2019/02/22
==================

- Fixed argument description of ``--role`` to reflect the current state.

- Fixed ``products deploy`` command which led to an exception in the command
  line argument parsing.

0.8.0 - 2019/02/20
==================

- Added ``consumer-sets edit`` command that allows users to edit their consumer
  sets.

- Added ``consumer-sets list`` command that allows users to list their consumer
  sets and filter them by project ID, cluster ID and product ID.

- Added ``projects users add`` command that allows users with permission
  to add users to projects by specifying a project ID and a user email or
  ID.

- Added ``projects users remove`` command that allows users with permission
  to remove users from projects by specifying a project ID and a user email or
  ID.

- Added ``organizations users remove`` command that allows organization
  admins to remove users from organizations that they are admins for, by
  specifying an organization ID, and a user email address or ID. Super
  users can remove users from any organization.

- Added ``organizations users add`` command that allows organization admins
  to add new users to organizations they are admins for, by specifying
  an organization ID, and a user email address or ID. Super users can
  add users to any organization.

0.7.0 - 2019/02/06
==================

- Added ``products deploy`` command that allows super users to deploy new
  CrateDB Cloud for Azure IoT products.

0.6.0 - 2019/02/05
==================

- Added ``projects create`` command that allows organization admins and
  super users to create new projects. Super users are able to create projects
  in all organizations, organization admins only in the organization that
  the user is part of.

- Added ``users list`` sub command that lists all users within organizations
  that a user is part of. For super users it will list all users from all
  organizations. Super users can also filter by organization ID, and list
  all users who are not part of any organization.

- Required/Optional arguments are shown separated in help

- Added eastus2 to available regions.

0.5.0 - 2019/01/22
==================

- Fix: Delegate all occurring error messages to the console output

- Added `users roles remove` sub command that allows to remove a role from a
  user.

- Improved help output.

- refactored `assignRoleToUser` to `addRoleToUser`

0.4.0 - 2019/01/15
==================

- Added `users roles add` sub command that assigns a role to user (super users only).

- Fixed `config get output-fmt` command

- Added `organizations list` sub command that lists organizations

- Removed region arg from `me` command

- Added `organizations create` sub command that creates an organization (super users only)

0.3.0 - 2019/01/09
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
