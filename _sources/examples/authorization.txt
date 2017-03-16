.. _examples-authorization:

API Authorization
-----------------

Using a ``GlobusAuthorizer`` is hard to grasp without a few examples to reference.
The basic usage should be to create these at client instantiation time.

Access Token Authorization on AuthClient and TransferClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perhaps you're in a part of your application that only sees Access Tokens.
Access Tokens are used to directly authenticate calls against Globus APIs, and
are limited-lifetime credentials.
You have distinct Access Tokens for each Globus service which you want to
access.

With the tokens in hand, it's just a simple matter of wrapping the tokens in
:class:`AccessTokenAuthorizer <globus_sdk.AccessTokenAuthorizer>` objects.

.. code-block:: python

    from globus_sdk import AuthClient, TransferClient, AccessTokenAuthorizer

    AUTH_ACCESS_TOKEN = '...'
    TRANSFER_ACCESS_TOKEN = '...'

    # note that we don't provide the client ID in this case
    # if you're using an Access Token you can't do the OAuth2 flows
    auth_client = AuthClient(
        authorizer=AccessTokenAuthorizer(AUTH_ACCESS_TOKEN))

    transfer_client = TransferClient(
        authorizer=AccessTokenAuthorizer(TRANSFER_ACCESS_TOKEN))

Refresh Token Authorization on AuthClient and TransferClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Refresh Tokens are long-lived credentials used to get new Access Tokens
whenever they expire.
However, it would be very awkward to create a new client instance every time
your credentials expire!

Instead, use a :class:`RefreshTokenAuthorizer
<globus_sdk.RefreshTokenAuthorizer>` to automatically re-up your credentials
whenever they near expiration.

Re-upping credentials is an operation that requires having client credentials
for Globus Auth, so creating the authorizer is more complex this time.

.. code-block:: python

    from globus_sdk import (AuthClient, TransferClient, ConfidentialAppAuthClient,
                            RefreshTokenAuthorizer)

    # for doing the refresh
    CLIENT_ID = '...'
    CLIENT_SECRET = '...'

    # the actual tokens
    AUTH_REFRESH_TOKEN = '...'
    TRANSFER_REFRESH_TOKEN = '...'

    # making the authorizer requires that we have an AuthClient which can talk
    # OAuth2 to Globus Auth
    internal_auth_client = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)

    # now let's bake a couple of authorizers
    auth_authorizer = RefreshTokenAuthorizer(AUTH_REFRESH_TOKEN,
                                             internal_auth_client)
    transfer_authorizer = RefreshTokenAuthorizer(TRANSFER_REFRESH_TOKEN,
                                                 internal_auth_client)

    # auth_client here is totally different from "internal_auth_client" above
    # the former is being used to request new tokens periodically, while this
    # one represents a user authenticated with those tokens
    auth_client = AuthClient(authorizer=auth_authorizer)
    # transfer_client doesn't have to contend with this duality -- it's always
    # representing a user
    transfer_client = TransferClient(authorizer=transfer_authorizer)

Basic Auth on an AuthClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're using an :class:`AuthClient <globus_sdk.AuthClient>` to do OAuth2
flows, you likely want to authenticate it using your client credentials -- the
client ID and client secret.

The preferred method is to use the ``AuthClient`` subclass which automatically
specifies its authorizer.
Internally, this will use a ``BasicAuthorizer`` to do Basic Authentication.

By way of example:

.. code-block:: python

    from globus_sdk import ConfidentialAppAuthClient

    CLIENT_ID = '...'
    CLIENT_SECRET = '...'

    client = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)

and you're off to the races!

Under the hood, this is implicitly running

.. code-block:: python

    AuthClient(authorizer=BasicAuthorizer(CLIENT_ID, CLIENT_SECRET))

but don't do this yourself -- ``ConfidentialAppAuthClient`` has different
methods from the base ``AuthClient``.
