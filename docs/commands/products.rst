.. _products:

============
``products``
============

The ``products`` command allows you to view the available products.

The product represents the compute configuration and the scale and storage options
that you can choose from when creating a cluster.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: products
   :nosubcommands:
   :nodescription:


``products list``
=================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: products list

Example
-------

.. code-block:: console

   sh$ croud products list --region eks1.eu-west-1.aws
   +---------+--------+---------+------------------------------------------------------------------------------+-----------------------+--------------+-----------+---------------+---------------+
   | kind    | name   | tier    | description                                                                  | scale_summary         |   vcpu_cores | ram       | min_storage   | max_storage   |
   |---------+--------+---------+------------------------------------------------------------------------------+-----------------------+--------------+-----------+---------------+---------------|
   | cluster | cr1    | default | Clusters suited for development and smaller scale workloads                  | 0 - 8 (1 - 9 nodes)   |            2 | 7.0 GiB   | 32.0 GiB      | 8196.0 GiB    |
   | cluster | cr2    | default | Ideal for your small to medium-sized production environments                 | 0 - 8 (1 - 9 nodes)   |            4 | 14.0 GiB  | 32.0 GiB      | 8196.0 GiB    |
   | cluster | s12    | default | S12                                                                          | 0 - 0 (1 - 1 nodes)   |            8 | 12.0 GiB  | 8.0 GiB       | 1024.0 GiB    |
   | cluster | s2     | default | S2                                                                           | 0 - 0 (1 - 1 nodes)   |            2 | 2.0 GiB   | 8.0 GiB       | 1024.0 GiB    |
   | storage | aws    | default | Storage product for AWS                                                      | N/A                   |         NULL | NULL      | NULL          | NULL          |
   +---------+--------+---------+------------------------------------------------------------------------------+-----------------------+--------------+-----------+---------------+---------------+