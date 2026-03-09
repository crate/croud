.. _subscriptions:

=================
``subscriptions``
=================

Subscriptions are the configured payment methods for an organization.

``subscriptions create``
========================

.. note::

   This command is only available for superusers.

Create a new contract subscription in an organization.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: subscriptions create
   :nodescription:

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

``subscriptions list``
======================

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: subscriptions list

Example
-------

.. code-block:: console

   sh$ croud subscriptions list
   +--------------------------------------+---------------------------------------+--------------------------------------+---------+----------+
   | id                                   | name                                  | organization_id                      | state   | provider |
   |--------------------------------------+---------------------------------------+--------------------------------------+---------+----------|
   | 56149db0-ea40-4616-88d1-885f6a491989 | my-azure-subscription                 | a0df2925-cc73-4365-8a10-7ef847632b81 | active  | azure    |
   | 99f26f04-5cef-4c82-b7bb-4a7d14b4b3c1 | contract-KFXfYlOX                     | a0df2925-cc73-4365-8a10-7ef847632b81 | active  | contract |
   +--------------------------------------+---------------------------------------+--------------------------------------+---------+----------+

``subscriptions delete``
========================

.. warning::

   Please note that this will delete any clusters running in this subscription,
   so use carefully.

Cancel a Stripe or contract subscription in an organisation.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: subscriptions delete
   :nodescription:

Example
-------

.. code-block:: console

   sh$ croud subscriptions delete --subscription-id 035f1161-402e-44b4-9073-0749586091e0
   Are you sure you want to cancel this subscription? This will delete any clusters running in this subscription. [yN] y
   ==> Success: Subscription cancelled.
