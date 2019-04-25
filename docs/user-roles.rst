.. _roles:

==========
User Roles
==========

This is an overview over the user roles users can have in the `CrateDB Cloud`_.

.. tip::

   The ``users roles list`` command provides a list of fully qualified role names.

.. rubric:: Table of Contents

.. contents::
   :local:

.. _organization-roles:

Organization Roles
==================

.. _org-admin:

Organization Admin
------------------

The admin of an organization has the following privileges:

* Organization admin has access to all projects in the organization, even if
  added to a project with a non-admin role.
* Privileges to manage organization settings.
* Privileges to add and remove users to and from an organization.
* Privileges of all the other roles combined.

.. _org-member:

Organization Member
-------------------

* Organization member has read-only access to the organization (settings, users).

.. _project-roles:

Project Roles
=============

.. _project-admin:

Project Admin
-------------

The admin of a project has the following privileges:

* Privileges to manage project settings.
* Privileges to add and remove users to and from a project. (The user has to
  be part of the organization)
* Privileges to administer products (clusters, consumer, ...).

.. _project-member:

Project Member
--------------

* Project member has read-only access to the project (settings, products,
  users).


.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
