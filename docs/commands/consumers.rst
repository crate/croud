=============
``consumers``
=============

The ``consumers`` command lets you manage consumer products.

.. tip::

   Be careful when specifying passwords on the command line. Some
   non-alphanumeric characters may be interpreted in an unexpected way by your
   shell. Use `string delimitation`_ and escape characters as needed.


``consumers deploy``
====================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: consumers deploy

Example
-------

.. code-block:: console

   sh$ croud consumers deploy \
       --project-id 664e6556-5734-449c-a717-f3533e5f86cf \
       --product-name eventhub-consumer \
       --tier s \
       --consumer-name my-first-consumer \
       --num-instances 1 \
       --cluster-id c95fe9bb-1a95-453d-9edc-30ffe7d8eb03 \
       --consumer-schema doc \
       --consumer-table raw__parted \
       --eventhub-dsn "Endpoint=sb://example.servicebus.windows.net/;SharedAccessKeyName=user;SharedAccessKey=...;EntityPath=myhub" \
       --eventhub-consumer-group username \
       --lease-storage-container username \
       --lease-storage-dsn "DefaultEndpointsProtocol=https;AccountName=storageaccountname;AccountKey=...;EndpointSuffix=core.windows.net"
   +--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+-------------+---------------+
   | id                                   | name              | projectId                            | clusterId                            | productName       | productTier   |   instances | tableName   | tableSchema   |
   |--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+-------------+---------------|
   | dc40090f-e1df-4974-b751-9fc27c824368 | my-first-consumer | 664e6556-5734-449c-a717-f3533e5f86cf | c95fe9bb-1a95-453d-9edc-30ffe7d8eb03 | eventhub-consumer | s             |           1 | raw__parted | doc           |
   +--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+-------------+---------------+


``consumers list``
==================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: consumers list

Example
-------

.. code-block:: console

   sh$ croud consumers list
   +--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+-------------+---------------+
   | id                                   | name              | projectId                            | clusterId                            | productName       | productTier   |   instances | tableName   | tableSchema   |
   |--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+-------------+---------------|
   | dc40090f-e1df-4974-b751-9fc27c824368 | my-first-consumer | 664e6556-5734-449c-a717-f3533e5f86cf | c95fe9bb-1a95-453d-9edc-30ffe7d8eb03 | eventhub-consumer | s             |           1 | raw__parted | doc           |
   +--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+-------------+---------------+


``consumers edit``
==================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: consumers edit

Example
-------

.. code-block:: console

   sh$ croud consumers edit \
       --consumer-schema my_schema \
       --consumer-table ingest_table
   +--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+--------------+---------------+
   | id                                   | name              | projectId                            | clusterId                            | productName       | productTier   |   instances | tableName    | tableSchema   |
   |--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+--------------+---------------|
   | dc40090f-e1df-4974-b751-9fc27c824368 | my-first-consumer | 664e6556-5734-449c-a717-f3533e5f86cf | c95fe9bb-1a95-453d-9edc-30ffe7d8eb03 | eventhub-consumer | s             |           1 | ingest_table | my_schema     |
   +--------------------------------------+-------------------+--------------------------------------+--------------------------------------+-------------------+---------------+-------------+--------------+---------------+


``consumers delete``
====================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: consumers delete

Example
-------

.. code-block:: console

   sh$ croud consumers delete \
       --consumer-id dc40090f-e1df-4974-b751-9fc27c824368
   Are you sure you want to delete the consumer? [yN] y
   ==> Success: Consumer deleted.


.. _string delimitation: https://en.wikipedia.org/wiki/Delimiter
