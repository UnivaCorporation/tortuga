import cherrypy

from tortuga.auth.manager import AuthManager
from tortuga.auth.method import MultiAuthentionMethod
from tortuga.auth.principal import AuthPrincipal
from tortuga.exceptions.authenticationFailed import AuthenticationFailed
from .exceptions import TortugaHTTPAuthError


class CherryPyAuthenticator(MultiAuthentionMethod):
    """
    An authenticator designed to be run as a CherryPy tool.

    """
    def __call__(self, *args, **kwargs):
        if cherrypy.request.config.get('auth.required', False):
            self.authenticate(**kwargs)

    def authenticate(self, skip_callbacks: bool = False, **kwargs) -> str:
        try:
            return super().authenticate(skip_callbacks=skip_callbacks,
                                        **kwargs)
        except AuthenticationFailed:
            raise TortugaHTTPAuthError()

    def on_authentication_succeeded(self, username: str):
        super().on_authentication_succeeded(username)

        principal: AuthPrincipal = AuthManager().get_principal(username)
        principal_attributes: dict = principal.get_attributes()

        cherrypy.request.login = username
        cherrypy.session['admin_id']: int = \
            principal_attributes.get('id', None)

    def on_authentication_failed(self):
        cherrypy.request.login: str = None
        cherrypy.session['admin_id']: int = None
