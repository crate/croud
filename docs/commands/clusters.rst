============
``clusters``
============

The ``clusters`` command lets you manage cluster products.

.. tip::

   Be careful when specifying passwords on the command line. Some
   non-alphanumeric characters may be interpreted in an unexpected way by your
   shell. Use `string delimitation`_ and escape characters as needed.

.. WARNING::

    Some ``clusters`` commands are only available for CrateDB Cloud sysadmins
    (superusers). A warning will indicate at the bottom of the documentation
    for each command when this is the case. They are listed here solely to
    clarify their function. You can also get information on any command by
    appending ``--help``.

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
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        1 | 4.5.1        | 952cd102-91c1-4837-962a-12ecb71a6ba8 | default     | my-first-crate-cluster.eastus.azure.cratedb.net. |
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
       --cluster-name my-first-crate-cluster \
       --project-id 952cd102-91c1-4837-962a-12ecb71a6ba8 \
       --version 4.6.6 \
       --username default \
       --password "s3cr3t!"
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+
   | id                                   | name                   | numNodes | crateVersion | projectId                            | username    | fqdn                                             |
   |--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        1 | 4.6.6        | 952cd102-91c1-4837-962a-12ecb71a6ba8 | default     | my-first-crate-cluster.eastus.azure.cratedb.net. |
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+
   ==> Info: Cluster creation initiated. It may take a few minutes to complete.
   ==> Info: Status: REGISTERED (Your creation request was received and is pending processing.)
   ==> Info: Status: IN_PROGRESS (Cluster creation started. Waiting for the node(s) to be created and creating other required resources.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+
   | id                                   | name                   | numNodes | crateVersion | projectId                            | username    | fqdn                                             |
   |--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        1 | 4.6.6        | 952cd102-91c1-4837-962a-12ecb71a6ba8 | default     | my-first-crate-cluster.eastus.azure.cratedb.net. |
   +--------------------------------------+------------------------+----------+--------------+--------------------------------------+-------------+--------------------------------------------------+

.. note::

   This command is only available for superusers.

   To deploy a cluster please use the `CrateDB Cloud Console`_.

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
   |--------------------------------------+------------------------+----------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        2 |
   +--------------------------------------+------------------------+----------+
   ==> Info: Cluster scaling initiated. It may take a few minutes to complete the changes.
   ==> Info: Status: SENT (Your scaling request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Scaling up from 2 to 3 nodes. Waiting for new node(s) to be present.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+----------+
   | id                                   | name                   | numNodes |
   |--------------------------------------+------------------------+----------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        3 |
   +--------------------------------------+------------------------+----------+

.. note::

   This command will wait for the cluster scaling to finish or fail.


``clusters upgrade``
====================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters upgrade

Example
-------

.. code-block:: console

   sh$ croud clusters upgrade \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --version 4.6.7
   +--------------------------------------+------------------------+---------------+
   | id                                   | name                   | crate_version |
   |--------------------------------------+------------------------+---------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |         4.6.6 |
   +--------------------------------------+------------------------+---------------+
   ==> Info: Cluster upgrade initiated. It may take a few minutes to complete the changes.
   ==> Info: Status: SENT (Your upgrade request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Waiting for node 1/1 to be terminated...)
   ==> Info: Status: IN_PROGRESS (Waiting for node 1/1 to be restarted...)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+---------------+
   | id                                   | name                   | crate_version |
   |--------------------------------------+------------------------+---------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |         4.6.7 |
   +--------------------------------------+------------------------+---------------+

.. note::

   This command will wait for the cluster upgrade to finish or fail.


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

.. note::

   After deleting a cluster, existing backups will remain for 30 days since the
   last time a backup was made. While you won't be able to restore these
   backups yourself, you can reach out to our support_ to have them restore a
   backup for you.

   If you want a more recent backup, there are several options:

   - :ref:`Create an AWS S3 repository <crate-reference:sql-create-repository>`
     with a ``base_path`` of ``/<project_id>/<cluster_id>/<name>``.
     ``<project_id>`` and ``<cluster_id>`` refer to the "dashed" form of the
     corresponding ID (``XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX``). ``<name>``
     can be any alphanumeric string. Afterwards, :ref:`create a snapshot
     <crate-reference:sql-create-snapshot>` in your repository.

   - Alternatively, you can create a backup as documented in the
     CrateDB documentation about :ref:`snapshots <crate-reference:snapshot-restore>`
     on repositories and snapshots by e.g. providing your own AWS S3 bucket and
     credentials.

   - Lastly, the :ref:`COPY TO SQL statement <crate-reference:sql-copy-to>` can
     be used to export a table to an AWS S3 bucket as well.

.. important::

   When you provide your own external storage, please ensure that the location
   is not world readable or writable to prevent unauthorized access to your
   data!


``clusters restart-node``
=========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters restart-node

Example
-------

.. code-block:: console

   sh$ croud clusters restart-node \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --ordinal 1
       --sudo
   +--------+----------+
   |   code | status   |
   |--------+----------|
   |    200 | Success  |
   +--------+----------+
   ==> Success: Node restarted. It may take a few minutes to complete the changes.

.. note::

   This command is only available for superusers.


``clusters set-deletion-protection``
====================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters set-deletion-protection

Example
-------

.. code-block:: console

   sh$ croud clusters set-deletion-protection \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --value true
   +--------------------------------------+------------------------+----------------------+
   | id                                   | name                   | deletion_protected   |
   |--------------------------------------+------------------------+----------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | TRUE                 |
   +--------------------------------------+------------------------+----------------------+
   ==> Success: Cluster deletion protection status successfully updated

.. note::

   This command is only available for superusers and organization admins.

.. _support: support@crate.io
.. _string delimitation: https://en.wikipedia.org/wiki/Delimiter
.. _CrateDB Cloud Console: https://console.cratedb.cloud


``clusters set-ip-whitelist``
====================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters set-ip-whitelist

Example
-------

.. code-block:: console

   sh$ croud clusters set-ip-whitelist \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --net "10.1.2.0/24,192.168.1.0/24"
   This will overwrite all existing CIDR restrictions. Continue? [yN] y
   +--------------------------------------+------------------------+----------------+
   | id                                   | name                   | ip_whitelist   |
   |--------------------------------------+------------------------+----------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | NULL           |
   +--------------------------------------+------------------------+----------------+
   ==> Info: Updating the IP Network whitelist initiated. It may take a few minutes to complete the changes.
   ==> Info: Status: SENT (Your update request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Updating IP Network Whitelist.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+-------------------------------------------------------------------------------------------------+
   | id                                   | name                   | ip_whitelist                                                                                    |
   |--------------------------------------+------------------------+-------------------------------------------------------------------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | [{"cidr": "10.1.2.0/24", "description": null}, {"cidr": "192.168.1.0/24", "description": null}] |
   +--------------------------------------+------------------------+-------------------------------------------------------------------------------------------------+

.. note::

   This command will wait for the operation to finish or fail.


``clusters expand-storage``
===========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters expand-storage

Example
-------

.. code-block:: console

   sh$ croud clusters expand-storage \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --disk-size-gb 512
   +--------------------------------------+------------------------+------------------------------------+
   | id                                   | name                   | hardware_specs                     |
   |--------------------------------------+------------------------+------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | Disk size: 256.0 GiB               |
   +--------------------------------------+------------------------+------------------------------------+
   ==> Info: Cluster storage expansion initiated. It may take a few minutes to complete the changes.
   ==> Info: Status: REGISTERED (Your storage expansion request was received and is pending processing.)
   ==> Info: Status: SENT (Your storage expansion request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Suspending cluster and waiting for Persistent Volume Claim(s) to be resized.)
   ==> Info: Status: IN_PROGRESS (Starting cluster. Scaling back up to 3 nodes. Waiting for node(s) to be present.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+------------------------------------+
   | id                                   | name                   | hardware_specs                     |
   |--------------------------------------+------------------------+------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | Disk size: 512.0 GiB               |
   +--------------------------------------+------------------------+------------------------------------+

.. note::

   This command will wait for the operation to finish or fail. It is only available for superusers and organization admins.
