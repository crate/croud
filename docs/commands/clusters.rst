.. _clusters:

============
``clusters``
============

The ``clusters`` command lets you manage your CrateDB clusters.

.. note::

   The clusters rely on an internal resource called ``project``. If you want to deploy
   a cluster, a default project will be created for you. You can also create projects
   yourself with the :ref:`projects` command.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters
   :nosubcommands:


``clusters list``
=================

Lists all clusters you have access to.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters list

Example
-------

.. code-block:: console

   sh$ croud clusters list
   +--------------------------------------+------------------------+-----------+---------------+---------------------------------------+-------------+-----------+--------------------------------------------------+---------+
   | id                                   | name                   | num_nodes | crate_version | project_id                            | username    | suspended | fqdn                                             | channel |
   |--------------------------------------+------------------------+-----------+---------------+---------------------------------------+-------------+-----------+--------------------------------------------------|---------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |         1 | 4.5.1         | 952cd102-91c1-4837-962a-12ecb71a6ba8  | default     | FALSE     | my-first-crate-cluster.eastus.azure.cratedb.net. | stable  |
   +--------------------------------------+------------------------+-----------+---------------+---------------------------------------+-------------+-----------+--------------------------------------------------+---------+


``clusters deploy``
===================

Deploys a new cluster.

.. tip::

   The minimum accepted length of password is 24 characters.

   Be careful when specifying passwords on the command line. Some
   non-alphanumeric characters may be interpreted in an unexpected way by your
   shell. Use `string delimitation`_ and escape characters as needed.

.. note::

   Free clusters can be deployed without a paid subscription. Therefore you can use
   ``--subscription-id free_tier --product-name crfree``.

.. warning::

   Some optional arguments and for Edge regions only. An Edge region allows you to
   host CrateDB instances in your own infrastructure however this feature is not
   maintained anymore. It is not recommended to use it.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters deploy

Example
-------

.. code-block:: console

   sh$ croud clusters deploy \
       --product-name cr1 \
       --tier default \
       --cluster-name my-first-crate-cluster \
       --org-id 952cd102-91c1-4837-962a-12ecb71a6ba8 \
       --region aks1.westeurope.azure \
       --version 6.2.1 \
       --username admin \
       --password "8Hed#kd$8^9i4Q#65fT4GKQI" \
       --subscription-id 782dfc00-7b25-4f48-8381-b1b096dd1619
   ==> Info: Cluster creation initiated. It may take a few minutes to complete.
   ==> Info: Status: REGISTERED (Your creation request was received and is pending processing.)
   ==> Info: Status: IN_PROGRESS (Cluster creation started. Waiting for the node(s) to be created and creating other required resources.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+-----------------------------------------------------------+-----------------------------------------------------------------------+
   | id                                   | name                   | fqdn                                                      | url                                                                   |
   |--------------------------------------+------------------------+-----------------------------------------------------------+-----------------------------------------------------------------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | my-first-crate-cluster.aks1.westeurope.azure.cratedb.net. | https://my-first-crate-cluster.aks1.westeurope.azure.cratedb.net:4200 |
   +--------------------------------------+------------------------+-----------------------------------------------------------+-----------------------------------------------------------------------+

Deployment of testing/nightly versions
--------------------------------------

For the users that want to get their hands on new features early, it is
possible to deploy versions from our ``testing`` and ``nightly`` channels.

``testing`` - These are versions that are being evaluated for promotion
to a stable release.

``nightly`` - These are built every night with the latest changes. They
will possibly contain newer features, but they also have potential to be less
stable than ``testing`` channel.

Both ``testing`` and ``nightly`` channel releases are available `here`_.

We want to emphasize the following about ``testing`` and ``nightly`` channels:

* They are for advanced users only.

* They are not suitable for production deployments.

* It is not possible to switch channels, e.g from ``testing`` to ``nightly``,
  or from ``testing`` to ``stable``.

Example
~~~~~~~

.. code-block:: console

   sh$ croud clusters deploy
       --product-name cr1
       --tier default
       --cluster-name test-deployment
       --project-id bdf523d0-ebc8-4f67-8e15-67d4225a20f9
       --version nightly-5.4.0-20230531
       --username "admin"
       --password "vogRjkY3TR$$P@UvogRjkY3TR$$P@U7vogRjkY3TR$$P@U7"
       --subscription-id 7598dc2b-a12e-123b-b776-a5123d4a123d
       --channel nightly
       --unit 0

``clusters scale``
==================

Scale an existing cluster up or down by changing the number of nodes.

.. note::

   The ``--unit`` argument specifies the total number of nodes desired, rather than
   adding to the existing count. For example, if your cluster has three nodes and you
   run the ``croud clusters scale --unit 1`` command, the cluster will be scaled
   down to two nodes, not up to four.

   This command will wait for the cluster scaling to finish or fail.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scale

Example
-------

.. code-block:: console

   sh$ croud clusters scale \
       --cluster-id 34813eb4-0a91-443e-af77-33fb91a0b04c \
       --unit 1
   +--------------------------------------+------------------------+-----------+
   | id                                   | name                   | num_nodes |
   |--------------------------------------+------------------------+-----------|
   | 34813eb4-0a91-443e-af77-33fb91a0b04c | emerald-taun-we        |         1 |
   +--------------------------------------+------------------------+-----------+
   ==> Info: Cluster scaling initiated. It may take a few minutes to complete
   the changes.
   ==> Info: Status: SENT (Your scaling request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Scaling up from 1 to 2 nodes. Waiting for new node(s) to be present.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+-----------+
   | id                                   | name                   | num_nodes |
   |--------------------------------------+------------------------+-----------|
   | 34813eb4-0a91-443e-af77-33fb91a0b04c | emerald-taun-we        |         2 |
   +--------------------------------------+------------------------+-----------+

``clusters upgrade``
====================

Upgrade the CrateDB version of an existing cluster.

.. note::

   This command will wait for the cluster upgrade to finish or fail.

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

``clusters delete``
===================

Deletes an existing cluster.

.. note::

   After deleting a cluster, all backups are removed as well, however, you can reach
   out to our support_ to have them restore a backup for you within 14 days since
   the last time a backup was made.

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

``clusters restart-node``
=========================

Restarts a node in the cluster.

Please wait for the node to be restarted before
restarting another one. Restarting a node might cause downtime on single-node clusters.

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
   +--------+----------+
   |   code | status   |
   |--------+----------|
   |    200 | Success  |
   +--------+----------+
   ==> Success: Node restarted. It may take a few minutes to complete the changes.


``clusters set-deletion-protection``
====================================

Changes the deletion protection status of a cluster.

When deletion protection is enabled, the cluster cannot be deleted until the
protection is removed. This can help prevent accidental deletions of clusters.

.. note::

   This command is only available for organization admins and superusers.

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

``clusters set-ip-whitelist``
=============================

Changes the IP Network whitelist of a cluster.

The whitelist is a list of CIDR blocks that are allowed to access the cluster.

When you set a new whitelist, it will overwrite the existing one. If you want to add
or remove CIDR blocks from the existing whitelist, you can first get the current
whitelist with ``cloud clusters get <cluster_id>`` command.

.. note::

   This command will wait for the operation to finish or fail.

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

``clusters expand-storage``
===========================

Expands the storage of an existing cluster.

.. NOTE::

    This command will wait for the operation to finish or fail.

    It is only available for organization admins and superusers.

    Note that for clusters in Azure regions, any storage increase exceeding a given
    increment (32, 64, etc.) will be priced at the level of the next increment.

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

``clusters set-suspended-state``
================================

Suspends or resumes an existing cluster.

When a cluster is suspended, it is not running and cannot be accessed, however storage
is still retained. This can help save costs when you don't need to use the cluster
for a while. When you want to use the cluster again, you can resume it.

.. note::

   This command will wait for the operation to finish or fail.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters set-suspended-state

Example
-------

.. code-block:: console

   sh$ croud clusters set-suspended-state \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --value true
   +--------------------------------------+------------------------+----------------+
   | id                                   | name                   | suspended      |
   |--------------------------------------+------------------------+----------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | FALSE          |
   +--------------------------------------+------------------------+----------------+
   ==> Info: Updating the cluster status initiated. It may take a few minutes to complete the changes.
   ==> Info: Status: SENT (Your update request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Suspending cluster.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+----------------+
   | id                                   | name                   | suspended      |
   |--------------------------------------+------------------------+----------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | TRUE           |
   +--------------------------------------+------------------------+----------------+

``clusters set-product``
========================

Sets a new product for an existing cluster, which can be used to change the
compute (vCPU and RAM) of the cluster.

.. NOTE::

    This command will wait for the operation to finish or fail.

    It is only available to organization and project admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters set-product

Example
-------

.. code-block:: console

   sh$ croud clusters set-product \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --product-name cr2
   +--------------------------------------+------------------------+----------------+
   | id                                   | name                   | product_name   |
   |--------------------------------------+------------------------+----------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | cr1            |
   +--------------------------------------+------------------------+----------------+
   ==> Info: Changing the cluster product initiated. It may take a few minutes to complete the changes.
   ==> Info: Status: REGISTERED (Your change compute cluster request was received and is pending processing.)
   ==> Info: Status: SENT (Your change compute request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Waiting for node 1/1 to be terminated...)
   ==> Info: Status: IN_PROGRESS (Waiting for node 1/1 to be restarted...)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+----------------+
   | id                                   | name                   | product_name   |
   |--------------------------------------+------------------------+----------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster | cr2            |
   +--------------------------------------+------------------------+----------------+

``clusters set-backup-schedule``
================================

Sets a new backup schedule for an existing cluster.

More information about the backup schedule can be found in
the `backup documentation`_.

.. NOTE::

    This command will wait for the operation to finish or fail.

    It is only available to organization and project admins and superusers.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters set-backup-schedule

Example
-------

.. code-block:: console

   sh$ ❯ croud clusters set-backup-schedule --cluster-id 705a7012-3f89-441d-a10e-b3749d05e993 --backup-hours 2,4,6
   +--------------------------------------+------------------------+-------------------+
   | id                                   | name                   | backup_schedule   |
   |--------------------------------------+------------------------+-------------------|
   | 705a7012-3f89-441d-a10e-b3749d05e993 | my-cratedb-cluster     | 55 6 * * *        |
   +--------------------------------------+------------------------+-------------------+
   ==> Info: Changing the cluster backup schedule. It may take a few minutes to complete the changes.
   ==> Info: Status: REGISTERED (Your update backup schedule request was received and is pending processing.)
   ==> Success: Operation completed.
   +--------------------------------------+------------------------+-------------------+
   | id                                   | name                   | backup_schedule   |
   |--------------------------------------+------------------------+-------------------|
   | 705a7012-3f89-441d-a10e-b3749d05e993 | my-cratedb-cluster     | 55 2,4,6 * * *    |
   +--------------------------------------+------------------------+-------------------+

``clusters snapshots``
======================

When a backup is created, a snapshot of the cluster is created in the backup repository.
The ``clusters snapshots`` command allows you to list and restore these snapshots.

Snapshots are rotated. More information about backups can be found in
the `backup documentation`_.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters snapshots
   :nosubcommands:


``clusters snapshots list``
---------------------------

Lists all snapshots of a cluster.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters snapshots list

Example
~~~~~~~

.. code-block:: console

   sh$ ❯ croud clusters snapshots list --cluster-id 705a7012-3f89-441d-a10e-b3749d05e993
   +------------------------+-------------------------------+-------------------+
   | created                | repository                    | snapshot          |
   |------------------------+-------------------------------+-------------------|
   | 2022-12-10 12:34:56    | system_backup_20221002123456  | 20221210123456    |
   | 2022-12-10 11:34:54    | system_backup_20221002123456  | 20221210113454    |
   +------------------------+-------------------------------+-------------------+


``clusters snapshots restore``
------------------------------

Restores a snapshot of a cluster.

It is possible to partially restore the snapshot by specifying the type of data
to restore. For example, you can choose to only restore the data and not the metadata,
or just a table.

.. note::

    This command will wait for the operation to finish or fail.

    It is only available to organization and project admins and superusers.

.. tip::

   It is possible to restore a snapshot from a cluster into another cluster.
   The source and target clusters must be in the same organization and region.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters snapshots restore

Example
~~~~~~~

.. code-block:: console

   sh$ ❯ croud clusters snapshots restore --cluster-id 705a7012-3f89-441d-a10e-b3749d05e993 \
         --repository system_backup_20221002123456 --snapshot 20221210123456 --type all
   ==> Info: Restoring the snapshot. Depending on the amount of data you have, this might take a very long time.
   ==> Success: Operation completed.
   +------------------------+-------------------------------+-------------------+
   | created                | repository                    | snapshot          |
   |------------------------+-------------------------------+-------------------|
   | 2022-12-10 12:34:56    | system_backup_20221002123456  | 20221210123456    |
   +------------------------+-------------------------------+-------------------+

``clusters subscription``
=========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters subscription
   :nosubcommands:

``clusters subscription update``
--------------------------------

Transfers a cluster between subscriptions.

.. note::

   This command is only available for superusers.

   Not all subscriptions are eligible to have clusters transferred to them.
   Please refer to internal documentation for more details.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters subscription update

.. _here: https://hub.docker.com/r/crate/crate/tags
.. _support: https://support.cratedb.com
.. _string delimitation: https://en.wikipedia.org/wiki/Delimiter
.. _backup documentation: https://cratedb.com/docs/cloud/en/latest/cluster/backups.html