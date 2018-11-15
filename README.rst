=========
Cloud-CLI
=========

A command line interface for CrateDB Cloud ☁


Installation
============

Python >= 3.6 is required.

Using git
---------

You can ``git clone`` this repository to any directory and install them Using
`pip <https://pip.pypa.io/en/stable/>`_::

    git clone https://github.com/crate/croud
    python3.6 -m pip install --user croud


Usage
=====

Use the command ``croud -h`` to list all available subcommands or
``croud <subcommand> -h`` to see the their detailed usage.


Development
===========

Run ``croud`` within a virtual python environment::

    python -m venv env
    source env/bin/activate

Install the ``croud`` package::

    pip install -e .
    pip install -e ".[development]"

Run it::

    ``croud -h``


Testing
-------

Install the dependencies used for testing::

    pip install -e ".[testing]"

Tests run with `pytest <https://docs.pytest.org/en/latest/>`_::

    pytest tests/
