.. _roles:

==========
User Roles
==========

This page provides an overview of the user roles available in `CrateDB Cloud`_, 
specifically in the context of using the Croud CLI.

.. tip::

   To view all available role names, run:
   
   .. code-block:: console
    
    sh$ croud users roles list 

.. _organization-roles:

Organization Roles
==================

.. _org-admin:

Organization Admin
------------------

An **Organization Admin** has the highest level of privileges within the organization:

* Full access to all projects within the organization, regardless of project-specific roles.
* Ability to manage organization settings.
* Can add or remove users from the organization.
* Inherits all permissions from other roles.


.. _org-member:

Organization Member
-------------------

An **Organization Member** has limited, read-only access:

* Can view organization settings and user lists.
* Cannot make any modifications.

.. _project-roles:

Project Roles
=============

.. _project-admin:

Project Admin
-------------

A **Project Admin** has full control over a specific project:

* Can manage project settings.
* Can add or remove users from the project (as long as the user is already part of the organization).
* Full cluster administration rights within the project.

.. _project-member:

Project Member
--------------

A **Project Member** has view-only access within a project:

* Can view project settings, clusters, users, and deployed products.
* Cannot perform administrative tasks.

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
