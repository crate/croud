============
``clusters``
============

The ``clusters`` command lets you manage cluster products.

.. tip::

   Be careful when specifying passwords on the command line. Some
   non-alphanumeric characters may be interpreted in an unexpected way by your
   shell. Use `string delimitation`_ and escape characters as needed.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters
   :nosubcommands:

``clusters list``
=================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters list

Example
-------

.. code-block:: console

   sh$ croud clusters list
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+
   | id                                   | name                   | numNodes | crateVersion | projectId                            | username    | fqdn                                             |
   |--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        1 | 3.2.6        | 952cd102-91c1-4837-962a-12ecb71a6ba8 | default     | my-first-crate-cluster.eastus.azure.cratedb.net. |
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+

``clusters deploy``
===================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters deploy

Example
-------

.. code-block:: console

   sh$ croud clusters deploy \
       --product-name cratedb.az1 \
       --tier xs \
       --name my-first-crate-cluster \
       --project-id 952cd102-91c1-4837-962a-12ecb71a6ba8 \
       --version 3.2.6 \
       --username default \
       --password "s3cr3t!"
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+
   | id                                   | name                   | numNodes | crateVersion | projectId                            | username    | fqdn                                             |
   |--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        1 | 3.2.6        | 952cd102-91c1-4837-962a-12ecb71a6ba8 | default     | my-first-crate-cluster.eastus.azure.cratedb.net. |
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+

``clusters scale``
==================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scale

Example
-------

.. code-block:: console

   sh$ croud clusters scale \
       --project-id 952cd102-91c1-4837-962a-12ecb71a6ba8 \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --unit 1
   +--------------------------------------+------------------------+----------+
   | id                                   | name                   | numNodes |
   |--------------------------------------+------------------------+----------+
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        5 |
   +--------------------------------------+------------------------+----------+

``clusters delete``
===================
.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters delete

Example
-------

.. code-block:: console
   sh$ croud clusters delete \
       --cluster-id dc40090f-e1df-4974-b751-9fc27c824368
   Are you sure you want to delete the cluster? [yN] y
   ==> Success: Cluster deleted.

.. _string delimitation: https://en.wikipedia.org/wiki/Delimiter
