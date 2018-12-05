=====
Croud
=====

A command line interface for CrateDB Cloud ☁

Installation
============

Using pip
---------

``croud`` can be installed using pip_::

    $ python3 -m pip install --user -U croud

Using git
---------

Alternatively, you can clone this repository, install it into a virtualenv_ and
add the executable to your ``PATH`` environment variable::

    $ git clone git@github.com:crate/croud.git && cd croud/
    $ python3.6 -m venv env
    $ env/bin/pip install -e .
    $ export PATH=$PATH:$(pwd)/env/bin/croud


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
