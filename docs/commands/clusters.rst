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
   |--------------------------------------+------------------------+----------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |        5 |
   +--------------------------------------+------------------------+----------+

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
       --version 3.3.3
   +--------------------------------------+------------------------+---------------+
   | id                                   | name                   | crate_version |
   |--------------------------------------+------------------------+---------------|
   | 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 | my-first-crate-cluster |         3.3.3 |
   +--------------------------------------+------------------------+---------------+

.. note::

   This command is only available for superusers.

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

   - `Create an AWS S3 repository`_ with a ``base_path`` of
     ``/<project_id>/<cluster_id>/<name>``. ``<project_id>`` and
     ``<cluster_id>`` refer to the "dashed" form of the corresponding ID
     (``XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX``). ``<name>`` can be any
     alphanumeric string. Afterwards, `create a snapshot`_ in your repository.

   - Alternatively, you can create a backup as documented in the
     `CrateDB documentation`_ on repositories and snapshots by e.g. providing your own
     AWS S3 bucket and credentials.

   - Lastly, the `COPY TO SQL statement`_ can be used to export a table to an
     AWS S3 bucket as well.

.. important::

   When you provide your own external storage, please ensure that the location
   is not world readable or writable to prevent unauthorized access to your
   data!

.. _support: support@crate.io
.. _Create an AWS S3 repository: https://crate.io/docs/crate/reference/en/latest/sql/statements/create-repository.html
.. _create a snapshot: https://crate.io/docs/crate/reference/en/latest/sql/statements/create-snapshot.html
.. _CrateDB documentation: https://crate.io/docs/crate/reference/en/latest/admin/snapshots.html
.. _COPY TO SQL statement: https://crate.io/docs/crate/reference/en/latest/sql/statements/copy-to.html
.. _string delimitation: https://en.wikipedia.org/wiki/Delimiter
