.. _clients:

Service Clients
===============

The Globus SDK provides a client class for every public Globus API.
Each client object takes authentication credentials from config files,
environment variables, or programmatically via :ref:`GlobusAuthorizers <authorization>`.

Once instantiated, a Client gives you high-level interface to make API calls,
without needing to know Globus API endpoints or their various parameters.

For example, you could use the ``TransferClient`` to list your task history
very simply::

    from globus_sdk import TransferClient

    # you must have transfer_token in your config for this to work
    tc = TransferClient()

    print("My Last 25 Tasks:")
    # `filter` to get Delete Tasks (default is just Transfer Tasks)
    for task in tc.task_list(num_results=25, filter="type:TRANSFER,DELETE"):
        print(task["task_id"], task["type"], task["status"])

.. rubric:: Client Types

.. toctree::
   :maxdepth: 1

   clients/transfer
   clients/auth
   clients/base
