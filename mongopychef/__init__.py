from pyramid.config import Configurator
from pyramid.authentication import RemoteUserAuthenticationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

import ming.odm.middleware

from .resources import Root
from .security import ChefAuthorizationPolicy

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    ming.configure(**settings)
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['session_secret'])
    config = Configurator(
        settings=settings,
        root_factory=Root,
        session_factory=session_factory)
    config.set_authentication_policy(RemoteUserAuthenticationPolicy())
    config.set_authorization_policy(ChefAuthorizationPolicy())
    config.add_static_view('static', 'mongopychef:static')
    config.scan()
    app = config.make_wsgi_app()
    app = ming.odm.middleware.MingMiddleware(app)
    return app
