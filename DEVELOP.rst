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

To run linting and unit tests across the whole test suite with the supported
python versions run::

    tox

Alongside ``--`` it's possible to pass ``pytest`` args e.g. to run only a
fraction of tests with python3.6::

    tox -e py36 -- tests/unit_tests/

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

.. _pytest: https://docs.pytest.org/en/latest/
.. _tox: https://tox.readthedocs.io
.. _Generating distribution archives: https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives
.. _PyPI: https://pypi.org/project/croud/
.. _Test PyPI: https://packaging.python.org/guides/using-testpypi/


Writing Documentation
=====================

The docs live under the ``docs/`` directory.

The docs are written with ReStructuredText_ and processed with Sphinx_.

First, install the additional dependencies by running::

    $ pip install -Ur requirements-docs.txt

Then build the documentation by running::

    $ bin/sphinx

The output can then be found in the ``docs/out/html/`` directory.

If you would like to live-reload the docs as you edit them, you can run::

    $ bin/sphinx dev

The docs are automatically built from Git by `Read the Docs`_ and there is
nothing special you need to do to get the live docs to update.

.. _Read the Docs: http://readthedocs.org
.. _ReStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/
