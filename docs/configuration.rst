=============
Configuration
=============

``croud`` uses a configuration to store user specific data, such as profiles
or authentication tokens, to disk so they can be persisted. The configuration
file is located inside the user's config directory, e.g. on a Linux system it
would be the following path::

   $HOME/.config/Crate/croud.yaml

To determine the location of the config files ``croud`` uses the `appdirs`_
package. Please refer to package documentation for further details.


Configuration file formatting
=============================

The contents of the configuration file of a fresh ``croud`` installation are
`YAML`_ formatted and look like this:

.. code-block:: yaml

   current-profile: dev
   default-format: table
   profiles:
     bregenz.a1:
       auth-token: NULL
       endpoint: https://bregenz.a1.cratedb.cloud
       format: table
     eastus2.azure:
       auth-token: null
       endpoint: https://eastus2.azure.cratedb.cloud
       format: table
     westeurope.azure:
       auth-token: null
       endpoint: https://westeurope.azure.cratedb.cloud
       format: table


Configuration file keys
=======================

The keys have the following meaning:

:``current-profile``:

    The name of the profile that is used for making API requests. This value
    needs to correspond to one of the items of ``profiles``.

:``default-format``:

    The default output format for API requests. This can be either ``table``
    (default), ``json``, or ``yaml``. This value is only used if the current
    profile does not specify a ``format``.

:``profiles``:

    A dictionary of available profiles. There are three default profiles available
    (see :ref:`available-profiles`).
    Each profile consists of ``auth-token``, ``endpoint``, and ``format``.

    ``auth-token`` is populated with the API token upon login.

    ``endpoint`` is the full URL of the API endpoint that is used for requests.

    ``format`` is the output format for this profile. This key is optional and
    if it is missing, the output format will fall back on ``default-format``.


Manage configuration via CLI
============================

``croud`` offers the possibility to manage its configuration and profiles using
the ``croud config {show | profiles}`` commands.

Please refer to the :doc:`commands/config` command reference for further
details.


.. _available-profiles:

Available profiles
==================

==================== ====================================== ===========
Profile              Endpoint                               Format
==================== ====================================== ===========
bregenz.a1           https://bregenz.a1.cratedb.cloud       table
eastus2.azure        https://eastus2.azure.cratedb.cloud    table
westeurope.azure     https://westeurope.azure.cratedb.cloud table
==================== ====================================== ===========


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

.. _appdirs: https://pypi.org/project/appdirs/
.. _YAML: https://yaml.org
