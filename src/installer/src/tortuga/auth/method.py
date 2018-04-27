from logging import getLogger
from typing import List

from passlib.hash import pbkdf2_sha256

from tortuga.exceptions.authenticationFailed import AuthenticationFailed
from .manager import AuthManager


logger = getLogger(__name__)


class AuthenticationMethod:
    """
    Base authentication method class.

    """
    def authenticate(self, skip_callbacks: bool = False, **kwargs) -> str:
        """
        Performs the authentication, and returns the username.

        :param bool skip_callbacks: do not call the
                                    on_authentication_succeeded and
                                    on_authentication_failed callbacks

        :return: the username of the authenticated user.
        :raises AuthenticationFailed:

        """
        try:
            username: str = self.do_authentication(**kwargs)
            logger.debug(
                'Authentication succeeded: {} -> {}'.format(
                    username,
                    self.__class__
                )
            )
            if not skip_callbacks:
                self.on_authentication_succeeded(username)
            return username

        except AuthenticationFailed:
            logger.debug('Authentication failed: {}'.format(self.__class__))
            if not skip_callbacks:
                self.on_authentication_failed()
            raise

    def do_authentication(self, **kwargs) -> str:
        """
        Does the actual authentication, imeplement the actual mechanics of
        your method here.

        :return: the username of the authenticated user.
        :raises AuthenticationFailed:

        """
        pass

    def on_authentication_succeeded(self, username: str):
        """
        A callback that is called when a successful authentication has
        occurred, either via this authenticator, or any other one in the
        chain.

        :param username: the username of the successfully authenticated user

        """
        pass

    def on_authentication_failed(self):
        """
        A callback that is called when all authentication methods in the
        chain have failed.

        """
        pass


class MultiAuthentionMethod(AuthenticationMethod):
    """
    The Authentication method that supports attempting to authenticate
    against a number of other authentication methods, in order until it
    finds one that succeeds.

    """
    def __init__(self, methods: List[AuthenticationMethod] = None):
        """
        Initializer.

        :param methods List[AuthenticationMethod]: the list of authentication
                                                   methods to use

        """
        if not methods:
            methods = []
        self._methods: List[AuthenticationMethod] = methods

    def do_authentication(self, **kwargs) -> str:
        """
        Authenticates trying all authentication methods in order, and stopping
        after the first one succeeds.

        """
        username = None
        for method in self._methods:
            try:
                #
                # Skip the callbacks so that we can defer calling them
                # until we know for sure the final result of the
                # authentication chain
                #
                username = method.authenticate(skip_callbacks=True, **kwargs)
                if username:
                    break
            except AuthenticationFailed:
                pass

        if username:
            self.on_authentication_succeeded(username)
            return username
        else:
            self.on_authentication_failed()
            raise AuthenticationFailed()

    def on_authentication_succeeded(self, username: str):
        """
        A callback that is called every time a user has successfully
        authenticated.

        :param username: the username of the successfully authenticated user

        """
        for method in self._methods:
            method.on_authentication_succeeded(username)

    def on_authentication_failed(self):
        """
        A callback that is called every time a all authentication methods
        fail.

        """
        for method in self._methods:
            method.on_authentication_failed()


class UsernamePasswordAuthenticationMethod(AuthenticationMethod):
    """
    An authentication method that uses a username/password passed in as
    keyword arguments.

    """
    def __init__(self):
        super().__init__()
        self._auth_manager: AuthManager = AuthManager()

    def do_authentication(self, username: str = None,
                          password: str =None) -> str:
        """
        An authentication implementation that requires a username and
        password.

        :param str username:        the username to authenticate
        :param str password:        the password to authenticate

        :return str: the username
        :raises AuthenticationFailed:

        """
        if not username or not password:
            raise AuthenticationFailed()

        principal = self._auth_manager.get_principal(username)

        if not principal:
            #
            # See if there is a new admin available
            #
            AuthManager().reloadPrincipals()
            principal = AuthManager().get_principal(username)

        if not principal:
            raise AuthenticationFailed()

        if pbkdf2_sha256.verify(password, principal.get_password()):
            return username

        raise AuthenticationFailed()
