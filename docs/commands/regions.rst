================
``regions``
================

``regions list``
================

Print the available regions to the user:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions list

.. note::

   Listed region names can used in the ``--region`` argument to list/deploy resources in that region.

Example
=======

.. code-block:: console

   sh$ croud regions list
   +--------------------+-------------------+
   | name               | description       |
   |--------------------+-------------------|
   | bregenz.a1         | Bregenz           |
   | eastus2.azure      | Azure East-US-2   |
   | westeurope.azure   | Azure West-Europe |
   +--------------------+-------------------+