======
``me``
======

Print the username and email address of the currently authenticated user:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: me

Example
=======

.. code-block:: console

   sh$ croud me
   +----------------+-----------------+---------+
   | email          | username        | idp     |
   |----------------+-----------------|---------|
   | me@example.com | User_1234567890 | azuread |
   +----------------+-----------------+---------+


``me edit``
===========

Change your own email address:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: me edit

Example
=======

.. code-block:: console

   sh$ croud me edit --email new@crate.io
   +---------+---------+-----------------------------------------------------------+
   | success | status  | message                                                   |
   |---------+---------+-----------------------------------------------------------|
   | True    | pending | A confirmation email was sent to new@crate.io. Please     |
   |         |         | follow its instructions to verify your new email address. |
   +---------+---------+-----------------------------------------------------------+
