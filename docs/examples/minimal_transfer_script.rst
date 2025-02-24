.. _example_minimal_transfer:

Minimal File Transfer Script
----------------------------

The following is an extremely minimal script to demonstrate a file transfer
using the :class:`TransferClient <globus_sdk.TransferClient>`.

It uses the tutorial client ID from the :ref:`tutorial <tutorial>`.
For simplicity, the script will prompt for login on each use.

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "61338d24-54d5-408f-a10d-66c06b59f6d2"
    auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)

    # requested_scopes specifies a list of scopes to request
    # instead of the defaults, only request access to the Transfer API
    auth_client.oauth2_start_flow(requested_scopes=TransferScopes.all)
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

    # construct an AccessTokenAuthorizer and use it to construct the
    # TransferClient
    transfer_client = globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
    )

    # Globus Tutorial Endpoint 1
    source_endpoint_id = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"
    # Globus Tutorial Endpoint 2
    dest_endpoint_id = "ddb59af0-6d04-11e5-ba46-22000b92c6ec"

    # create a Transfer task consisting of one or more items
    task_data = globus_sdk.TransferData(
        transfer_client, source_endpoint_id, dest_endpoint_id
    )
    task_data.add_item(
        "/share/godata/file1.txt",  # source
        "/~/minimal-example-transfer-script-destination.txt",  # dest
    )

    # submit, getting back the task ID
    task_doc = transfer_client.submit_transfer(task_data)
    task_id = task_doc["task_id"]
    print(f"submitted transfer, task_id={task_id}")
