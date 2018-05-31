from logging import getLogger
import os
from typing import List

import jwt
from passlib.hash import pbkdf2_sha256

from tortuga.auth.principal import AuthPrincipal
from tortuga.config.configManager import ConfigManager
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

    def do_authentication(self, **kwargs) -> str:
        """
        An authentication implementation that requires a username and
        password.

        :return str: the username
        :raises AuthenticationFailed:

        """
        username: str = kwargs.get('username', None)
        password: str = kwargs.get('password', None)

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


class JwtAuthenticationMethod(AuthenticationMethod):
    """
    Authenticate a user via JWT tokens.

    """
    ALGORITHMS = ['HS256', 'RS256']
    #
    # The path to the JWT secret file, as found under $TORTUGA_HOME/etc
    #
    SECRET_FILE_NAME = 'jwt.secret'

    def __init__(self):
        self._secret: str = None
        self._load_secret()

    def do_authentication(self, **kwargs) -> str:
        if not self._secret:
            logger.debug('No secret set for JWT authentication')
            raise AuthenticationFailed()

        token: str = kwargs.get('token', None)
        if not token:
            raise AuthenticationFailed()

        decoded = jwt.decode(token, self._secret,
                             algorithms=self.ALGORITHMS)

        username = decoded.get('username', None)
        if not username:
            raise AuthenticationFailed()

        principal: AuthPrincipal = AuthManager().get_principal(username)
        if not principal:
            raise AuthenticationFailed()

        return username

    def _load_secret(self):
        """
        Loads the JWT shared secret from the secret file, if it exists.

        """
        cm = ConfigManager()

        secret_file_path = os.path.join(
            cm.getRoot(),
            'etc',
            self.SECRET_FILE_NAME
        )

        if not os.path.exists(secret_file_path):
            logger.info('No JWT secret found, JWT authentication will not '
                        'work: {}'.format(secret_file_path))
            return

        with open(secret_file_path) as fp:
            self._secret = fp.read().strip()
