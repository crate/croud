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


.. _pytest: https://docs.pytest.org/en/latest/
