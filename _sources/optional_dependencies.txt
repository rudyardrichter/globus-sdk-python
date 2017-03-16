Optional Dependencies
=====================

In order to maintain portability while supporting a robust feature set, certain
features of the Globus SDK rely upon optional dependencies.
These dependencies are python packages which are *not* required by the SDK, but
*are* required by specific features.
If you attempt to use such a feature without installing the relevant
dependency, you will get a ``GlobusOptionalDependencyError``.

OIDC ID Tokens
--------------

The :class:`OAuthTokenResponse
<globus_sdk.auth.token_response.OAuthTokenResponse>` may include an ID token
conforming to the Open ID Connect specification.
If you wish to decode this token via :meth:`decode_id_token
<globus_sdk.auth.token_response.OAuthTokenResponse.decode_id_token>`, you must
install ``python-jose``, which we use to implement ID Token verification.
