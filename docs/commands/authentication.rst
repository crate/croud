====================
``login``/``logout``
====================

CrateDB Cloud uses OAuth2 for authentication.

You must authenticate yourself before interacting with your `CrateDB Cloud`_
account or its resources.

.. _login:

``login``
=========

Log in, like so:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: login

This will open a browser window that will present you with an authentication
screen.

.. note::

   Your access token is cached locally, and all subsequent commands will be
   authenticated until you explicitly log out.

CrateDB Cloud offers four authentication methods: username and password (via
Amazon Cognito), Azure AD, GitHub and Google logins. By default username and password
authentication is used, but the login provider can be changed using the
``--idp`` (IdentityProvider) argument.

.. _logout:

``logout``
==========

To log out, run:

.. argparse::
   :module: croud.__main__
   :func: get_parser
   :prog: croud
   :path: logout

This will clear your access token. You will then be required to log in again
before interacting with your account or its resources.


.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
