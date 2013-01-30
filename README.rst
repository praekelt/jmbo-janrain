Installation instructions, until this is part of Jmbo:

Add jmbo-janrain to your buildout as part of the buildout eggs::

    [buildout]

    extensions=
        ...
        mr.developer

    eggs=
        ...
        jmbo-janrain

    [sources]
    jmbo-janrain = git git://github.com/praekelt/jmbo-janrain.git branch=develop

Add it to your INSTALLED_APPS::

    INSTALLED_APPS = (
    ...
    'janrain',
    ...
    )

Add the middleware::

    middleware_classes = (
    ...
    'janrain.middleware.JanrainMiddleware',
    ...
    )

Add the following parameters to your settings file::

    # URL given as your domain url by Janrain, including the https parts.
    JANRAIN_URL = 'JANRAIN_URL'
    
    # The janrain client ID, shown on the Janrain site.
    JANRAIN_CLIENT_ID = 'JANRAIN_CLIENT_ID'

    # The Janrain client secret, shown on the Janrain site.
    JANRAIN_CLIENT_SECRET = 'JANRAIN_CLIENT_SECRET'


Find the complete set of `Jmbo docs here <http://jmbo.readthedocs.org/>`_

