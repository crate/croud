.. _data-import-export:

===================================
``import-jobs`` and ``export-jobs``
===================================

The ``clusters import-jobs`` and ``clusters export jobs`` commands let you manage,
respectively, the import and export jobs in your CrateDB Cloud cluster.

.. tip::

   Import jobs are the easiest way to get data into CrateDB Cloud. Use them to import
   from a local file, an arbitrary URL, or from an AWS S3-compatible service.

   Most JSON, CSV and Parquet files are supported.


``clusters import-jobs``
========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs
   :nosubcommands:



``clusters import-jobs create``
===============================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs create
   :nosubcommands:


``clusters import-jobs create from-url``
========================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs create from-url

Example
-------

.. code-block:: console

   sh$ croud clusters import-jobs create from-url --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400 \
       --file-format csv --table my_table_name --url https://s3.amazonaws.com/my.import.data.gz --compression gzip
   +--------------------------------------+--------------------------------------+------------+
   | id                                   | cluster_id                           | status     |
   |--------------------------------------+--------------------------------------+------------|
   | dca4986d-f7c8-4121-af81-863cca1dab0f | e1e38d92-a650-48f1-8a70-8133f2d5c400 | REGISTERED |
   +--------------------------------------+--------------------------------------+------------+
   ==> Info: Status: REGISTERED (Your import job was received and is pending processing.)
   ==> Info: Done importing 3 records and 36 Bytes.
   ==> Success: Operation completed.


``clusters import-jobs create from-file``
=========================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs create from-file

.. code-block:: console

   sh$ croud clusters import-jobs create from-file --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400 \
       --file-format csv --table my_table_name --file-id 2e71e5a6-a21a-4e99-ae58-705a1f15635c
   +--------------------------------------+--------------------------------------+------------+
   | id                                   | cluster_id                           | status     |
   |--------------------------------------+--------------------------------------+------------|
   | 9164f886-ae37-4a1b-b3fe-53f9e1897e7d | e1e38d92-a650-48f1-8a70-8133f2d5c400 | REGISTERED |
   +--------------------------------------+--------------------------------------+------------+
   ==> Info: Status: REGISTERED (Your import job was received and is pending processing.)
   ==> Info: Done importing 3 records and 36 Bytes.
   ==> Success: Operation completed.


``clusters import-jobs create from-s3``
=======================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs create from-s3

.. code-block:: console

   sh$ croud clusters import-jobs create from-s3 --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400 \
       --secret-id 71e7c5da-51fa-44f2-b178-d95052cbe620 --bucket cratedbtestbucket \
       --file-path myfiles/cratedbimporttest.csv --file-format csv --table my_table_name
   +--------------------------------------+--------------------------------------+------------+
   | id                                   | cluster_id                           | status     |
   |--------------------------------------+--------------------------------------+------------|
   | f29fdc02-edd0-4ad9-8839-9616fccf752b | e1e38d92-a650-48f1-8a70-8133f2d5c400 | REGISTERED |
   +--------------------------------------+--------------------------------------+------------+
   ==> Info: Status: REGISTERED (Your import job was received and is pending processing.)
   ==> Info: Done importing 3 records and 36 Bytes.
   ==> Success: Operation completed.


``clusters import-jobs list``
=============================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs list

Example
-------

.. code-block:: console

   sh$ ❯ croud clusters import-jobs list --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400
   +--------------------------------------+--------------------------------------+-----------+--------+-------------------+
   | id                                   | cluster_id                           | status    | type   | destination       |
   |--------------------------------------+--------------------------------------+-----------+--------+-------------------|
   | dca4986d-f7c8-4121-af81-863cca1dab0f | e1e38d92-a650-48f1-8a70-8133f2d5c400 | SUCCEEDED | url    | my_table_name     |
   | 00de6048-3af6-41da-bfaa-661199d1c106 | e1e38d92-a650-48f1-8a70-8133f2d5c400 | SUCCEEDED | s3     | my_table_name     |
   | 035f5ec1-ba9e-4a5c-9ce1-44e9a9cab6c1 | e1e38d92-a650-48f1-8a70-8133f2d5c400 | SUCCEEDED | file   | my_table_name     |
   +--------------------------------------+--------------------------------------+-----------+--------+-------------------+


``clusters import-jobs delete``
===============================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs delete

Example
-------

.. code-block:: console

   sh$ ❯ croud clusters import-jobs delete \
         --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400 \
         --import-job-id 00de6048-3af6-41da-bfaa-661199d1c106
   ==> Success: Success.


``clusters import-jobs progress``
=================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters import-jobs progress

Examples
--------

.. code-block:: console

   sh$ ❯ croud clusters import-jobs progress \
         --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400 \
         --import-job-id 00de6048-3af6-41da-bfaa-661199d1c106 \
         --summary true
   +-----------+-----------+------------------+-----------------+---------------+
   |   percent |   records |   failed_records |   total_records |   total_files |
   |-----------+-----------+------------------+-----------------+---------------+
   |       100 |       891 |                0 |             891 |             2 |
   +-----------+-----------+------------------+-----------------+---------------+


.. code-block:: console

   sh$ ❯ croud clusters import-jobs progress \
         --cluster-id e1e38d92-a650-48f1-8a70-8133f2d5c400 \
         --import-job-id 00de6048-3af6-41da-bfaa-661199d1c106 \
         --limit ALL
         --offset 0
   +-----------+-----------+-----------+------------------+-----------------+
   | name      |   percent |   records |   failed_records |   total_records |
   |-----------+-----------+-----------+------------------+-----------------|
   | file1.csv |       100 |       800 |                0 |             800 |
   | file2.csv |       100 |        91 |                0 |              91 |
   +-----------+-----------+-----------+------------------+-----------------+


``clusters export-jobs``
========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters export-jobs
   :nosubcommands:


``clusters export-jobs create``
===============================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters export-jobs create

Example
-------

.. code-block:: console

   sh$ ❯ croud clusters export-jobs create --cluster-id f6c39580-5719-431d-a508-0cee4f9e8209 \
         --table nyc_taxi --file-format csv
   +--------------------------------------+--------------------------------------+------------+
   | id                                   | cluster_id                           | status     |
   |--------------------------------------+--------------------------------------+------------|
   | 85dc0024-b049-4b9d-b100-4bf850881692 | f6c39580-5719-431d-a508-0cee4f9e8209 | REGISTERED |
   +--------------------------------------+--------------------------------------+------------+
   ==> Info: Status: SENT (Your creation request was sent to the region.)
   ==> Info: Status: IN_PROGRESS (Export in progress)
   ==> Info: Exporting... 2.00 K records and 19.53 KiB exported so far.
   ==> Info: Exporting... 4.00 K records and 39.06 KiB exported so far.
   ==> Info: Done exporting 6.00 K records and 58.59 KiB.
   ==> Success: Download URL: https://cratedb-file-uploads.s3.amazonaws.com/some/download
   ==> Success: Operation completed.


.. NOTE::

    This command will wait for the operation to finish or fail. It is only available
    to organization admins.


``clusters export-jobs list``
=============================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters export-jobs list

Example
-------

.. code-block:: console

   sh$ ❯ croud clusters export-jobs list \
         --cluster-id f6c39580-5719-431d-a508-0cee4f9e8209
   +--------------------------------------+--------------------------------------+-----------+---------------------+-----------------------------------------------+
   | id                                   | cluster_id                           | status    | source              | destination                                   |
   |--------------------------------------+--------------------------------------+-----------+---------------------+-----------------------------------------------|
   | b311ba9d-9cb4-404a-b58d-c442ae251dbf | f6c39580-5719-431d-a508-0cee4f9e8209 | SUCCEEDED | nyc_taxi            | Format: csv                                   |
   |                                      |                                      |           |                     | File ID: 327ad0e6-607f-4f99-a4cc-c1e98bf28e4d |
   +--------------------------------------+--------------------------------------+-----------+---------------------+-----------------------------------------------+


``clusters export-jobs delete``
===============================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters export-jobs delete

Example
-------

.. code-block:: console

   sh$ ❯ croud clusters export-jobs delete \
         --cluster-id f6c39580-5719-431d-a508-0cee4f9e8209 \
         --export-job-id 3b311ba9d-9cb4-404a-b58d-c442ae251dbf
   ==> Success: Success.

.. _here: https://hub.docker.com/r/crate/crate/tags
