===============
Developer Guide
===============


Setup
=====


Pip
---

Python >= 3.6 is required. Run ``croud`` within a virtual python environment::

    python -m venv env
    source env/bin/activate

Install the ``croud`` package::

    pip install -e .
    pip install -e ".[development]"

Run it::

    croud -h


Git
---

Alternatively, you can clone this repository, install it into a virtualenv and
add the executable to your PATH environment variable::

    git clone git@github.com:crate/croud.git && cd croud/
    python3.6 -m venv env
    env/bin/pip install -e .
    export PATH=$PATH:$(pwd)/env/bin/croud


Testing
-------

Install the dependencies used for testing::

    pip install -e ".[testing]"

Tests run with `pytest`_ inside a `tox`_ environment.

To run unit tests across the whole test suite with the supported python
versions run::

    tox

Alongside ``--`` it's possible to pass ``pytest`` args e.g. to run only a
fraction of tests with python3.6::

    tox -e py36 -- -k test_rest

The test setup uses `pytest-random-order`_ to ensure better test separation.
By default, the order will be random on the Python module level. That means,
essentially, the order of ``*.py`` files will be randomized when running tests.

When running tests using ``tox`` or ``py.test``, `pytest-random-order`_ will
emit a seed value at the beginning which can be used to rerun tests with the
specific order::

    $ tox -e py37
    ...
    py37 run-test-pre: PYTHONHASHSEED='2789788418'
    py37 run-test: commands[0] | pytest
    ======================== test session starts =========================
    platform linux -- Python 3.7.3, pytest-3.10.1, py-1.8.0, pluggy-0.12.0
    Using --random-order-bucket=module
    Using --random-order-seed=240261
    ...

One can rerun a random test setup by passing ``--random-order-seed=<seed>`` to
py.test::

    $ tox -e py37 -- --random-order-seed=240261


Code style checks and static analysis
-------------------------------------

This project uses pre-commit_ to ensure linting, code formatting, and type
checking. Tools, such as black_, flake8_, isort_, and mypy_ can be run as
hooks upon committing and/or pushing code.
When at least one of the hooks fails, committing or pushing changes is aborted
and manual intervention is necessary.

Install pre-commit_ for your user and verify that the installation worked:

.. code-block:: console

   $ python -m pip install --user pre-commit

After the successful installation, install the hooks for this project:

.. code-block:: console

   $ pre-commit install -t pre-commit -t pre-push --install-hooks
   pre-commit installed at .git/hooks/pre-commit
   pre-commit installed at .git/hooks/pre-push
  ...

From now on, each time you run ``git commit`` or ``git push``, hooks defined in
the file ``.pre-commit-config.yaml`` will run on staged files.


Release
=======

#. Create a new branch named ``<prefix>/prepare-x.y.z``.

#. Update the ``__version__`` in ``setup.py``.

#. Add new section to ``CHANGES.rst`` with the version and release date in the
   format ``x.y.z - yyyy/mm/dd``.

#. Create a PR against ``master`` or version branch (e.g. ``0.1``).

#. After PR is merged, tag the release by running::

    ./dev/tools/create_tag.sh


Upload to `PyPI`_
-----------------

See the instructions for `Generating distribution archives`_ for more details.

.. note::

    It is recommended to upload the package to `Test PyPI`_ first which is intended
    for experimentation and testing.


Documentation
=============

The documentation is written using `Sphinx`_ and `ReStructuredText`_.


Working on the documentation
----------------------------

Python 3.7 is required.

Change into the ``docs`` directory:

.. code-block:: console

    $ cd docs

For help, run:

.. code-block:: console

    $ make

    Crate Docs Utils

    Run `make <TARGET>`, where <TARGET> is one of:

      dev     Run a Sphinx development server that builds and lints the
              documentation as you edit the source files

      html    Build the static HTML output

      check   Build, test, and lint the documentation

      delint  Remove any `*.lint` files

      reset   Reset the build cache

You must install `fswatch`_ to use the ``dev`` target.


Continuous integration and deployment
-------------------------------------

|utils| |travis| |rtd|

Travis CI is `configured`_ to run ``make check`` from the ``docs`` directory.
Please do not merge pull requests until the tests pass.

`Read the Docs`_ automatically deploys the documentation whenever a configured
branch is updated.

To make changes to the RTD configuration (e.g., to activate or deactivate a
release version), please contact the `@crate/docs`_ team.


.. _@crate/docs: https://github.com/orgs/crate/teams/docs
.. _black: https://github.com/psf/black
.. _configured: https://github.com/crate/croud/blob/master/.travis.yml
.. _flake8: https://gitlab.com/pycqa/flake8
.. _fswatch: https://github.com/emcrisostomo/fswatch
.. _Generating distribution archives: https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives
.. _isort: https://github.com/timothycrosley/isort
.. _mypy: https://github.com/python/mypy
.. _pre-commit: https://pre-commit.com
.. _PyPI: https://pypi.org/project/croud/
.. _pytest-random-order: https://pypi.org/project/pytest-random-order/
.. _pytest: https://docs.pytest.org/en/latest/
.. _Read the Docs: http://readthedocs.org
.. _ReStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/
.. _Test PyPI: https://packaging.python.org/guides/using-testpypi/
.. _tox: https://tox.readthedocs.io


.. |utils| image:: https://img.shields.io/endpoint.svg?color=blue&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcrate%2Fcroud%2Fmaster%2Fdocs%2Futils.json
    :alt: Utils version
    :target: https://github.com/crate/croud/blob/master/docs/utils.json

.. |travis| image:: https://img.shields.io/travis/crate/croud.svg?style=flat
    :alt: Travis CI status
    :target: https://travis-ci.org/crate/croud

.. |rtd| image:: https://readthedocs.org/projects/croud/badge/?version=latest
    :alt: Read The Docs status
    :target: https://readthedocs.org/projects/croud
