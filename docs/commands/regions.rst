.. _regions:

================
``regions``
================

``regions list``
================

.. note::

   The region is specified for each profile in the :doc:`../configuration` file.

   The region for specific actions can be overridden using the ``--region`` argument to list or deploy resources in that region.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions list

Example
-------

.. code-block:: console

   sh$ croud regions list
   +-----------------------+---------------------------------------+--------------------------------------+
   | name                  | description                           | organization_id                      |
   |---------------------------------------+-----------------------|--------------------------------------|
   | aks1.eastus2.azure    | Azure East US 2                       |                                      |
   | aks1.westeurope.azure | Azure West Europe                     |                                      |
   | eks1.eu-west-1.aws    | AWS West Europe (Ireland)             |                                      |
   | my-edge-region        | 055be5e4a8f744b9bfac25f507496d16.edge | 70b56aab-2ba1-4378-88b9-5b6123513e47 |
   +-----------------------+---------------------------------------+--------------------------------------+

``regions create``
==================

.. warning::

   An Edge region allows you to host CrateDB instances in your own infrastructure
   however this feature is not maintained anymore. It is not recommended to use it.

.. note::

   Organization admins can create Edge regions that belong to an organization.

Create a new Edge region.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions create
   :nodescription:

Example
-------

.. code-block:: console

   sh$ croud regions create --org-id 11111111-1111-1111-1111-111111111111 --description "Edge region"
   +---------------+---------------------------------------------------+
   | description   | name                                              |
   |---------------+---------------------------------------------------|
   | Edge region   | 2c0d0e22b0e846b2a7acdcbf092e54a3.edge.cratedb.net |
   +---------------+---------------------------------------------------+
   ==> Success: You have successfully created a region.

   To install the edge region run the following command:

   $ bash <( wget -qO- https://console.cratedb.cloud/edge/cratedb-cloud-edge.sh) <install-token>


``regions delete``
==================

.. warning::

   Edge regions allow you to host CrateDB instances in your own infrastructure however
   this feature is not maintained anymore. It is not recommended to use it.

.. note::

    Only organization admins can delete Edge regions that belong to their organizations.
    Deleting a region does not imply that all the Kubernetes resources will be automatically deleted.
    This command only unregisters the region from Crate Cloud.

Delete an existing Edge region.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: regions delete
   :nodescription:

Example
-------

.. code-block:: console

   sh$ croud regions delete --name 2c0d0e22b0e846b2a7acdcbf092e54a3.edge.cratedb.net
   ==> Success: You have successfully deleted a region.
