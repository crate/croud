=========
Cloud-CLI
=========

A command line interface for CrateDB Cloud ☁

Usage
=====

Use the command ``croud -h`` to list all available subcommands or
``croud <subcommand> -h`` to see the their detailed usage.


Development
===========

Python >= 3.6 is required. Run ``croud`` within a virtual python environment::

    python -m venv env
    source env/bin/activate

Install the ``croud`` package::

    pip install -e .
    pip install -e ".[development]"

Run it::

    croud -h

Environment Variables
---------------------

:``CLOUD_SESSION``: The session-cookie that is used to authenticate a user
                    against CrateDB Cloud. As long as the OAuth2 mechanism in
                    ``CROUD`` is not in place this needs to be set to simulate
                    the login. Copy the value of the cookie ``session`` from
                    the browser that has been used for OAuth on CrateDB cloud.


Testing
-------

Install the dependencies used for testing::

    pip install -e ".[testing]"

Tests run with `pytest <https://docs.pytest.org/en/latest/>`_::

    pytest tests/
