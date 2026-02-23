.. _authentication:

====================
``login``/``logout``
====================

CrateDB Cloud uses OAuth2 for authentication.

You must authenticate yourself before interacting with your `CrateDB Cloud`_
account or its resources.

.. _login:

``login``
=========

Log in to your CrateDB Cloud account.

This will open a browser window that will present you with an authentication screen.

CrateDB Cloud offers four authentication methods: username and password (via
Amazon Cognito), Azure AD, GitHub and Google logins. By default username and password
authentication is used, but the login provider can be changed using the
``--idp`` (Identity Provider) argument.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: login

.. note::

   Your access token is cached locally, and all subsequent commands will be
   authenticated until you explicitly log out.

.. _logout:

``logout``
==========

Log out of your CrateDB Cloud account.

This will clear your access token. You will then be required to log in again
before interacting with your account or its resources.

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: logout

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
