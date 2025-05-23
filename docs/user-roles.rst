.. _roles:

==========
User Roles
==========

This is an overview of the user roles in `CrateDB Cloud`_ for
the purposes of the Croud CLI.

.. tip::

   The ``users roles list`` command provides a list of fully qualified role
   names.

.. _organization-roles:

Organization roles
==================

.. _org-admin:

Organization admin
------------------

The admin of an organization has the following privileges:

* Organization admin has access to all projects in the organization, even if
  added to a project with a non-admin role.
* Privileges to manage organization settings.
* Privileges to add and remove users to and from an organization.
* Privileges of all the other roles combined.

.. _org-member:

Organization member
-------------------

* Organization member has read-only access to the organization (settings, users).

.. _project-roles:

Project roles
=============

.. _project-admin:

Project admin
-------------

The admin of a project has the following privileges:

* Privileges to manage project settings.
* Privileges to add and remove users to and from a project. (The user has to
  be part of the organization)
* Privileges to administer clusters.

.. _project-member:

Project member
--------------

* Project member has read-only access to the project (settings, products,
  users).

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
