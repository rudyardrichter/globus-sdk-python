Deprecations
============

The Globus SDK uses python ``DeprecationWarning`` and
``PendingDeprecationWarning`` classes to indicate deprecated and soon-to-be
deprecated behaviors.  In order to see these warnings, run python with the
flags:

::

 python -Wonce::DeprecationWarning \
        -Wonce::PendingDeprecationWarning

Note: The ``-W`` flag must precede any module you are passing to ``python``,
or it will be fed into ``sys.argv`` inside of the module.
