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
   The region for specific actions can be overridden using the ``--region`` argument to list or deploy resources in that region.


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



``regions create``
==================

Creates a new Edge or Cloud region:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions create

.. note::

   Only superusers can create regions.

Example
=======

.. code-block:: console

   sh$ croud regions create --org-id 926d4e6b-5967-4ab4-8f46-82a90150ab31 --description "Edge region" --provider EDGE --aws-bucket backup-bucket --aws-region eu-west-1 --sudo
   +---------------+---------------------------------------------------+
   | description   | name                                              |
   |---------------+---------------------------------------------------|
   | Edge region   | 2c0d0e22b0e846b2a7acdcbf092e54a3.edge.cratedb.net |
   +---------------+---------------------------------------------------+