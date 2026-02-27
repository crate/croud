.. _index:

=========
Croud CLI
=========

*Croud* is a *command-line interface* (CLI) tool for interacting with `CrateDB
Cloud`_. It is maintained as a pip package.

Croud allows you to manage various CrateDB Cloud resources, such as clusters,
projects, organizations, users, and more:

- **Organizations** are the top-level entities in CrateDB Cloud. They can contain multiple
  CrateDB clusters. It is where the organization admins can manage users, billing, etc.
- **Clusters** are the main resources in CrateDB Cloud. They represent the actual CrateDB
  instances that you can deploy, manage, scale and monitor.
- **Projects** are internal resources that contain clusters. They are automatically
  created when you create a cluster, but you can also create them manually and assign
  clusters to them. A project can contain many clusters but we recommand using one
  project per cluster for better organization. You can assign user permissions on the
  project level to manage access to clusters.
- **Users** are the individual accounts that can access CrateDB Cloud. They can have
  different roles and permissions within an organization, such as organization admin,
  organization member, etc.
- **Subscriptions** represent the billing plans for your CrateDB Cloud resources. They
  can be free (e.g., free clusters) or paid (e.g., Stripe, Marketplace or contract
  subscriptions).
- **Regions** represent the geographical locations where you can deploy your CrateDB
  clusters. They can be public (managed by CrateDB Cloud) or private (hosted in your
  own infrastructure, also known as Edge regions. Please note that this feature is not
  maintained anymore and we don't recommend to use it).
- **API keys** are used for authentication and authorization when using Croud in
  headless environments.
- **File import** (import/export jobs) allows you to import data into your CrateDB
  clusters from various file formats, such as CSV or JSON.
- **Automation** (scheduled jobs) allows you schedule regular SQL queries execution
  in your CrateDB clusters.
- **Products** represent the different offerings available in CrateDB Cloud.

.. rubric:: Table of Contents

.. contents::
   :local:

.. toctree::
   :maxdepth: 1

   getting-started
   configuration
   commands/index
   user-roles

.. _CrateDB Cloud: https://crate.io/products/cratedb-cloud/
