=========
Cloud-CLI
=========

A command line interface for CrateDB Cloud ☁

Install
=======

Using git
---------

Alternatively, you can "git clone" this repository to any directory, create a
virtual environment and link the binary in your ``PATH``::

    $ git clone git@github.com:crate/croud.git && cd croud/
    $ python3.6 -m venv env
    $ env/bin/pip install -e .
    $ ln -s $(pwd)/env/bin/croud /usr/local/bin/croud


Usage
=====

Use the command ``croud -h`` to list all available subcommands or
``croud <subcommand> -h`` to see the their detailed usage::

    $ croud [subcommand] {parameters}


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


.. _contribution docs: CONTRIBUTING.rst
.. _developer docs: DEVELOP.rst
.. _Crate.io: http://crate.io/
.. _StackOverflow: https://stackoverflow.com/tags/crate
.. _Slack: https://crate.io/docs/support/slackin/
.. _paid support: https://crate.io/pricing/
