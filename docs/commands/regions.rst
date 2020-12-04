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

   The region is specified for each profile in the :doc:`../configuration` file.
   The region for specific actions can be overridden using the ``--region`` argument to list/deploy resources in that region.


Example
=======

.. code-block:: console

   sh$ croud regions list
   +--------------------------------+-----------------------+
   | description                    | name                  |
   |--------------------------------+-----------------------|
   | Azure East US 2                | aks1.eastus2.azure    |
   | Azure West Europe              | aks1.westeurope.azure |
   | AWS West Europe (Ireland)      | eks1.eu-west-1.aws    |
   +--------------------------------+-----------------------+

