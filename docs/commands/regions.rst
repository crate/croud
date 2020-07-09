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
   +---------------------------+--------------------+
   | description               | name               |
   |---------------------------+--------------------|
   | Bregenz                   | bregenz.a1         |
   | Azure East-US-2           | eastus2.azure      |
   | AWS West Europe (Ireland) | eks1.eu-west-1.aws |
   | Azure West-Europe         | westeurope.azure   |
   +---------------------------+--------------------+
