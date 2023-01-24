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
   +---------------------------------------+-----------------------+--------------------------------------+
   | description                           | name                  | organization_id                      |
   |---------------------------------------+-----------------------|--------------------------------------|
   | Azure East US 2                       | aks1.eastus2.azure    |                                      |
   | Azure West Europe                     | aks1.westeurope.azure |                                      |
   | AWS West Europe (Ireland)             | eks1.eu-west-1.aws    |                                      |
   | 055be5e4a8f744b9bfac25f507496d16.edge | my-edge-region        | 70b56aab-2ba1-4378-88b9-5b6123513e47 |
   +---------------------------------------+-----------------------+--------------------------------------+



``regions create``
==================

Creates a new Edge region:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions create

.. note::

   Organization admins can create Edge regions that belong to an organization.

Example
=======

.. code-block:: console

   sh$ croud regions create --org-id 11111111-1111-1111-1111-111111111111 --description "Edge region"
   +---------------+---------------------------------------------------+
   | description   | name                                              |
   |---------------+---------------------------------------------------|
   | Edge region   | 2c0d0e22b0e846b2a7acdcbf092e54a3.edge.cratedb.net |
   +---------------+---------------------------------------------------+
   ==> Success: You have successfully created a region.

   To install the edge region run the following command:

     $ bash <( wget -qO- https://console.cratedb-dev.cloud/edge/cratedb-cloud-edge.sh) <install-token>


``regions delete``
==================

Deletes an existing Edge region:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions delete

.. note::

    Only organization admins can delete Edge regions that belong to their organizations.
    Deleting a region does not imply that all the Kubernetes resources will be automatically deleted.
    This command only unregisters the region from Crate Cloud, in order to clean the region Kubernetes
    cluster the following script can be be used:



Example
=======

.. code-block:: console

   sh$ croud regions create --name 2c0d0e22b0e846b2a7acdcbf092e54a3.edge.cratedb.net
   ==> Success: You have successfully deleted a region.
