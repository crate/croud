=============
Configuration
=============

``croud`` uses a configuration to store user specific data, such as profiles
or authentication tokens, to disk so they can be persisted. The configuration
file is located inside the user's config directory, e.g. on a Linux system it
would be the following path::

   $HOME/.config/Crate/croud.yaml

To determine the location of the config files ``croud`` uses the `platformdirs`_
package. Please refer to package documentation for further details.

Configuration file formatting
=============================

The contents of the configuration file of a fresh ``croud`` installation are
`YAML`_ formatted and look like this:

.. code-block:: yaml

   current-profile: aks1.westeurope.azure
   default-format: table
   profiles:
     cratedb.cloud:
       auth-token: NULL
       key: NULL
       secret: NULL
       endpoint: https://console.cratedb.cloud
       region: _any_


Configuration file keys
=======================

The keys have the following meaning:

:``current-profile``:

    The name of the profile that is used for making API requests. This value
    needs to correspond to one of the items of ``profiles``.

:``default-format``:

    The default output format for API requests. This can be either ``table``
    (default, displays the most important fields), ``wide`` (a table format
    displaying all fields), ``json``, or ``yaml``. This value is only used if
    the current profile does not specify a ``format``.

:``profiles``:

    A dictionary of available profiles. There is just one profile configured in the
    default configuration file. You would only need different profiles if you want to
    authenticate as different users or use different default organizations.

    Each profile consists of an ``auth-token``, ``key``, ``secret``, ``endpoint``,
    ``region``, and ``format``.

    ``auth-token`` is populated with the API token upon login.

    ``key`` is optional and can be used when authenticating to the API using an API key.

    ``secret`` is the secret that goes with the API key above.

    ``endpoint`` is the full URL of the API endpoint that is used for requests.

    ``region`` is the specific region within which CrateDB Cloud resources are accessed.

    ``format`` is the output format for this profile. This key is optional and
    if it is missing, the output format will fall back on ``default-format``.

    If both ``auth-token`` and ``key/secret`` are specified, the ``auth-token`` will
    take precedence. Keep this in mind if you get unexpected authorization errors -
    you might need to explicitly set the ``auth-token`` to NULL.


Manage configuration via CLI
============================

``croud`` offers the possibility to manage its configuration and profiles using
the ``croud config {show | profiles}`` commands.

Please refer to the :doc:`commands/config` command reference for further
details.


Headless authentication
=======================

If no ``croud.yaml`` configuration file exists, the program also accepts the
``CRATEDB_CLOUD_API_KEY`` and ``CRATEDB_CLOUD_API_SECRET`` environment variables
to support headless authentication per `CrateDB Cloud API keys`_.


Incompatible versions
=====================

The configuration file format changed in version ``0.23.0`` when profiles were
introduced.

If you have an older version of ``croud`` installed already, you will get the
following message upon execution of a command with the new version of
``croud``:

.. code-block:: console

   $ croud me
   ==> Error: Your configuration file is incompatible with the current version of croud.
   ==> Info: Please delete the file '/home/<user>/.config/Crate/croud.yaml' or update it manually.

You can either delete the old configuration file, or manually edit the content
by pasting the default configuration stated above.


.. _platformdirs: https://pypi.org/project/platformdirs/
.. _CrateDB Cloud API keys: https://cratedb.com/docs/cloud/en/latest/organization/api.html
.. _YAML: https://yaml.org
