=================
``subscriptions``
=================

``subscriptions create``
========================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: subscriptions create

Example
-------

.. code-block:: console

   sh$ croud subscriptions create --type contract --org-id a0df2925-cc73-4365-8a10-7ef847632b81 --sudo
   +--------------------------------------+-------------------+---------+------------+
   | id                                   | name              | state   | provider   |
   |--------------------------------------+-------------------+---------+------------|
   | 4841eb8a-257d-460d-9dcf-c6a7f0dcc09d | contract-YeBfJLWA | active  | cloud      |
   +--------------------------------------+-------------------+---------+------------+
   ==> Success: Subscription created.

.. note::

   This command is only available for superusers.

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

``subscriptions delete``
========================

Cancel a Stripe or contract subscription in a user's organisation. Please note that this will delete
any clusters running in this subscription, so use carefully:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: subscriptions delete

Example
-------

.. code-block:: console

   sh$ croud subscriptions delete --subscription-id 035f1161-402e-44b4-9073-0749586091e0
   Are you sure you want to cancel this subscription? This will delete any clusters running in this subscription. [yN] y
   ==> Success: Subscription cancelled.
