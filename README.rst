=====
Croud
=====

.. image:: https://travis-ci.org/crate/croud.svg?branch=master
    :target: https://travis-ci.org/crate/croud
    :alt: Travis CI

.. image:: https://badge.fury.io/py/croud.svg
    :target: http://badge.fury.io/py/croud
    :alt: Version

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: https://crate.io/docs/cloud/en/latest/
    :alt: Documentation

.. image:: https://coveralls.io/repos/github/crate/croud/badge.svg?branch=master
    :target: https://coveralls.io/github/crate/croud?branch=master
    :alt: Coverage

|

*Croud* is a *command-line interface* (CLI) tool for CrateDB Cloud ☁.

Installation
============

Using pip
---------

``croud`` can be installed using pip_::

    $ python3 -m pip install --user -U croud


To update, run::

    $ pip install -U croud

Usage
=====

Use the command ``croud -h`` to list all available subcommands or
``croud <subcommand> -h`` to see the their detailed usage::

    $ croud [subcommand] {parameters}

.. note::

    ``Croud`` stores the login credentials inside ``<UserDataDir>/Crate/croud.yaml``.
    The storage format across versions < 1.x is incompatible. This means that it
    might be necessary to remove the config after an upgrade.


Contributing
============

This project is primarily maintained by Crate.io_, but we welcome community
contributions!

See the `developer docs`_ and the `contribution docs`_ for more information.


Help
====

Looking for more help?

- Check `StackOverflow`_ for common problems
- Chat with us on `Slack`_
- Get `paid support`_


.. _pip: https://pip.pypa.io/en/stable/
.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _contribution docs: https://github.com/crate/croud/blob/master/CONTRIBUTING.rst
.. _developer docs: https://github.com/crate/croud/blob/master/DEVELOP.rst
.. _Crate.io: http://crate.io/
.. _StackOverflow: https://stackoverflow.com/tags/crate
.. _Slack: https://crate.io/docs/support/slackin/
.. _paid support: https://crate.io/pricing/
