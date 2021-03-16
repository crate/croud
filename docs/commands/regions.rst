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

   Only superusers can create Cloud regions. Organization admins can create Edge regions that belong to an organization.

Example
=======

.. code-block:: console

   sh$ croud regions create --org-id 11111111-1111-1111-1111-111111111111 --description "Edge region" --provider EDGE
   +---------------+---------------------------------------------------+
   | description   | name                                              |
   |---------------+---------------------------------------------------|
   | Edge region   | 2c0d0e22b0e846b2a7acdcbf092e54a3.edge.cratedb.net |
   +---------------+---------------------------------------------------+
   ==> Success: You have successfully created a region.

   To install the edge region run the following command:

     $ bash <( wget -qO- https://console.cratedb-dev.cloud/edge/cratedb-cloud-edge.sh) <install-token>
