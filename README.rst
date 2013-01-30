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

The product includes a South migration, so I found that the following works when using the standard Praekelt setup:

* Backup.

* Run a level 2 deploy. This will pull in the product and dependencies. The server will either not start up or will throw 503 errors, since the migration is not run yet.

* Do a South migration::
    ./bin/{yoursite}-qa-web-site migrate janrain

* Run a level 1 install. Everything should now start up. You might want to add the stuff above into all the settings files.

Find the complete set of `Jmbo docs here <http://jmbo.readthedocs.org/>`_

