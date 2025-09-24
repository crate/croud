=============
Configuration
=============

Croud stores user-specific data (such as authentication tokens, profiles, and settings) in a configuration 
file on disk to persist across sessions.

Config File Location
====================

The configuration file is located inside your system's user-specific config directory. 
On Linux, for example, the path is:

.. code-block:: console
   
   sh$ $HOME/.config/Crate/croud.yaml

Croud uses the `platformdirs`_ Python package to determine the correct config directory for your operating system.

Config File Format
==================

The configuration file is in YAML format. A default configuration might look like this:

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


Config File Keys
=======================

Here's what each key means:


Top-Level Keys
^^^^^^^^^^^^^^

:``current-profile``:

    The name of the profile that is used for making API requests. This value
    needs to correspond to one of the items of ``profiles``.

:``default-format``:

    Default output format if a profile doesn't define one. Valid values:

    * table -- (default) most relevant fields

    * wide -- all fields in table format

    * json

    * yaml

:``profiles``:

    There is just one profile configured in the default configuration file. 
    You would only need different profiles if you want to authenticate as 
    different users or use different default organizations.

    Each profile includes the following settings:

    * ``auth-token`` Set automatically on login. Takes precedence over ``key``/ ``secret``.

    * ``key`` Optional. API key for headless authentication.

    * ``secret`` Secret corresponding to the API key.

    * ``endpoint`` full URL of the API endpoint that is used for requests.

    * ``region`` The CrateDB Cloud region to use (e.g. ``westeurope.azure``).

    * ``format`` Optional. Output format for this profile (overrides ``default-format``).

.. TIP::

   If both ``auth-token`` and ``key`` / ``secret`` are present, ``auth-token`` takes precedence. 
   If you face unexpected authorization errors, try to force key-based auth, explicitly set ``auth-token: NULL``.


Manage Configuration via CLI
============================

You can manage your configuration and profiles using the following commands:

.. code-block:: console

    sh$ croud config show
    sh$ croud config profiles

Refer to the :doc:`commands/config` command reference for more details.


Headless authentication
=======================

If no ``croud.yaml`` configuration file exists, the program also accepts the
``CRATEDB_CLOUD_API_KEY`` and ``CRATEDB_CLOUD_API_SECRET`` environment variables
to support headless authentication per `CrateDB Cloud API keys`_.

In environments where no ``croud.yaml`` exists (e.g., CI pipelines), 
you can authenticate using environment variables:

.. code-block:: console

    sh$ export CRATEDB_CLOUD_API_KEY=your-api-key
    sh$ export CRATEDB_CLOUD_API_SECRET=your-secret 

Check `CrateDB Cloud API keys`_ for the instructions on how to generate a key and secret.

Incompatible versions
=====================

Versions prior to ``0.23.0`` are incompatible with the current configuration file format.

If you are in that scenario, you will get the following error message:

.. code-block:: console

   sh$ croud me
   ==> Error: Your configuration file is incompatible with the current version of croud.
   ==> Info: Please delete the file '/home/<user>/.config/Crate/croud.yaml' or update it manually.

To solve it, either delete the old configuration file, or manually edit the content
by pasting the default configuration stated above.


.. _platformdirs: https://pypi.org/project/platformdirs/
.. _CrateDB Cloud API keys: https://cratedb.com/docs/cloud/en/latest/organization/api.html
.. _YAML: https://yaml.org
