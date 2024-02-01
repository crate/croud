==================
``scheduled-jobs``
==================

The ``scheduled-jobs`` command lets you manage scheduled sql jobs for your cluster.

.. tip::

   Scheduled sql jobs are an easy way to setup sql statements that need
   to be run in a certain interval to manage your clusters data.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scheduled-jobs
   :nosubcommands:


``clusters scheduled-jobs create``
==================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scheduled-jobs create

Example
-------

.. code-block:: console

   sh$ croud clusters scheduled-jobs create \
       --name test-job \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --cron "1 1 * * *" \
       --sql "DELETE * FROM TABLE test" \
       --enabled True
   +----------+---------------+-----------+-------------------+-----------+
   | name     | id            | cron      | sql               | enabled   |
   |----------+---------------+-----------+-------------------+-----------|
   | test-job | 0EW7SX3ND87DY | 1 1 * * * | DELETE FROM test  | TRUE      |
   +----------+---------------+-----------+-------------------+-----------+

``clusters scheduled-jobs list``
================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scheduled-jobs list

Example
-------

.. code-block:: console

   sh$ croud clusters scheduled-jobs list \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1
   +----------+---------------+-----------+-------------------+-----------+---------------------------+
   | name     | id            | cron      | sql               | enabled   | next_run_time             |
   |----------+---------------+-----------+-------------------+-----------+---------------------------|
   | test-job | 0EW7SX3ND87DY | 1 1 * * * | DELETE FROM test  | TRUE      | 2024-01-20T01:01:00+00:00 |
   +----------+---------------+-----------+-------------------+-----------+---------------------------+

``clusters scheduled-jobs logs``
================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scheduled-jobs logs

Example
-------

.. code-block:: console

   sh$ croud clusters scheduled-jobs logs \
       --job-id 0EW7SX3ND87DY \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1
   +---------------+----------------------------+----------------------------+---------+-----------------------------------------------------------------------+
   | job_id        | start                      | end                        | error   | statements                                                            |
   |---------------+----------------------------+----------------------------+---------+-----------------------------------------------------------------------|
   | 0EW7SX3ND87DY | 2024-01-20T08:52:00.008000 | 2024-01-29T08:52:00.014000 | NULL    | {"0": {"duration": 0.0021747201681137085, "sql": "DELETE FROM test"}} |
   +---------------+----------------------------+----------------------------+---------+-----------------------------------------------------------------------+

``clusters scheduled-jobs edit``
================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scheduled-jobs edit

Example
-------

.. code-block:: console

   sh$ croud clusters scheduled-jobs edit \
       --job-id 0EW7SX3ND87DY \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1 \
       --name test-job-1 \
       --cron "3 2 * * *" \
       --sql "SELECT 1;" \
       --enabled False
   +------------+---------------+-----------+-----------+-----------+
   | name       | id            | sql       | cron      | enabled   |
   |------------+---------------+-----------+-----------+-----------|
   | test-job-1 | 0EW7SX3ND87DY | SELECT 1; | 3 2 * * * | FALSE     |
   +------------+---------------+-----------+-----------+-----------+

``clusters scheduled-jobs delete``
==================================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: clusters scheduled-jobs delete

Example
-------

.. code-block:: console

   sh$ croud clusters scheduled-jobs delete \
       --job-id 0EW7SX3ND87DY
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1
   ==> Success: Scheduled job deleted.
