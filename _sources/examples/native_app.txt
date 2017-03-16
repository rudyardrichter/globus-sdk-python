Native App Login
----------------

This is an example of the use of the Globus SDK to carry out an OAuth2
Native App Authentication flow.

The goal here is to have a user authenticate in Globus Auth, and for the SDK
to procure tokens which may be used to authenticate SDK calls against various
services for that user.

Get a Client
~~~~~~~~~~~~

In order to complete an OAuth2 flow to get tokens, you must have a client
definition registered with Globus Auth.
To do so, follow the relevant documentation for the
`Globus Auth Service <https://docs.globus.org/api/auth/>`_ or go directly to
`developers.globus.org <https://developers.globus.org/>`_ to do the
registration.

Make sure, when registering your application, that you enter
``https://auth.globus.org/v2/web/auth-code`` into the "Redirect URIs" field.
This is necessary to leverage the default behavior of the SDK, and is typically
sufficient for this type of application.


Do the Flow
~~~~~~~~~~~

If you want to copy-paste an example, you'll need at least a ``client_id`` for
your ``AuthClient`` object.
You should also specifically use the :class:`NativeAppAuthClient
<globus_sdk.NativeAppAuthClient>` type of ``AuthClient``, as it has been
customized to handle this flow.

The shortest version of the flow looks like this:

.. code-block:: python

    import globus_sdk

    # you must have a client ID
    CLIENT_ID = '...'

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow()

    authorize_url = client.oauth2_get_authorize_url()
    print('Please go to this URL and login: {0}'.format(authorize_url))

    # or just input() on python3
    auth_code = raw_input(
        'Please enter the code you get after login here: ').strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # the useful values that you want at the end of this
    globus_auth_data = token_response.by_resource_server['auth.globus.org']
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    globus_auth_token = globus_auth_data['access_token']
    globus_transfer_token = globus_transfer_data['access_token']


Do It With Refresh Tokens
~~~~~~~~~~~~~~~~~~~~~~~~~

The flow above will give you access tokens (short-lived credentials), good for
one-off operations.
However, if you want a persistent credential to access the logged-in user's
Globus resources, you need to request a long-lived credential called a Refresh
Token.

``refresh_tokens`` is a boolean option to the ``oauth2_start_flow`` method.
When False, the flow will terminate with a collection of Access Tokens, which
are simple limited lifetime credentials for accessing services. When True, the
flow will terminate not only with the Access Tokens, but additionally with a
set of Refresh Tokens which can be used **indefinitely** to request new Access
Tokens. The default is False.

Simply add this option to the example above:

.. code-block:: python

    client.oauth2_start_flow_native_app(refresh_tokens=True)
