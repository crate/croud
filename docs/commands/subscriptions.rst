=================
``subscriptions``
=================

``subscriptions list``
======================

Print the subscriptions in a user's organization:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: subscriptions list

Example
=======

.. code-block:: console

   sh$ croud subscriptions list
   +--------------------------------------+---------------------------------------+--------+----------+
   | id                                   | name                                  | state  | provider |
   |--------------------------------------+---------------------------------------+--------+----------|
   | 56149db0-ea40-4616-88d1-885f6a491989 | my-azure-subscription                 | active | azure    |
   | b01b93e0-fd18-4896-ba88-288efe759bf0 | x43z8qxk9nh7l7mq7nxd3907z-zWG1GEiPuM4 | active | aws      |
   +--------------------------------------+---------------------------------------+--------+----------+
