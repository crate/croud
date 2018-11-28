===============
Developer Guide
===============

Setup
=====

Python >= 3.6 is required. Run ``croud`` within a virtual python environment::

    python -m venv env
    source env/bin/activate

Install the ``croud`` package::

    pip install -e .
    pip install -e ".[development]"

Run it::

    croud -h


Testing
-------

Install the dependencies used for testing::

    pip install -e ".[testing]"

Tests run with `pytest`_::

    pytest tests/


Release
=======

This project uses `setuptools_scm`_ for managing the package version from scm
metadata.

1. Create a new branch named <prefix>/prepare-x.y.z

2. Add new section to ``CHANGES.rst`` with the version and release date in the
   format ``x.y.z - yyyy/mm/dd``

3. Create a PR against ``master`` or version branch (e.g. ``0.1``).

4. After PR is merged, tag the release::

    git tag -a "<VERSION>" -m "Tag for version <VERSION>"
    git push --tags


.. _pytest: https://docs.pytest.org/en/latest/
.. _setuptools_scm: https://github.com/pypa/setuptools_scm
