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
   +----------------+-----------------+
   | email          | username        |
   |----------------+-----------------|
   | me@example.com | User_1234567890 |
   +----------------+-----------------+
