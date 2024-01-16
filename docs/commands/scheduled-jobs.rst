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
   :path: scheduled-jobs
   :nosubcommands:


``scheduled-jobs create``
=========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: scheduled-jobs create

Example
-------

.. code-block:: console

   sh$ croud scheduled-jobs create \
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

``scheduled-jobs list``
=======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: scheduled-jobs list

Example
-------

.. code-block:: console

   sh$ croud scheduled-jobs list \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1
   +----------+---------------+-----------+-------------------+-----------+---------------------------+
   | name     | id            | cron      | sql               | enabled   | next_run_time             |
   |----------+---------------+-----------+-------------------+-----------+---------------------------|
   | test-job | 0EW7SX3ND87DY | 1 1 * * * | DELETE FROM test  | TRUE      | 2024-01-20T01:01:00+00:00 |
   +----------+---------------+-----------+-------------------+-----------+---------------------------+

``scheduled-jobs logs``
=======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: scheduled-jobs logs

Example
-------

.. code-block:: console

   sh$ croud scheduled-jobs logs \
       --job-id 0EW7SX3ND87DY \
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1
   +---------------+----------------------------+----------------------------+---------+-----------------------------------------------------------------------+
   | job_id        | start                      | end                        | error   | statements                                                            |
   |---------------+----------------------------+----------------------------+---------+-----------------------------------------------------------------------|
   | 0EW7SX3ND87DY | 2024-01-20T08:52:00.008000 | 2024-01-29T08:52:00.014000 | NULL    | {"0": {"duration": 0.0021747201681137085, "sql": "DELETE FROM test"}} |
   +---------------+----------------------------+----------------------------+---------+-----------------------------------------------------------------------+

``scheduled-jobs delete``
=========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: scheduled-jobs delete

Example
-------

.. code-block:: console

   sh$ croud scheduled-jobs delete \
       --job-id 0EW7SX3ND87DY
       --cluster-id 8d6a7c3c-61d5-11e9-a639-34e12d2331a1
   ==> Success: Scheduled job deleted.
