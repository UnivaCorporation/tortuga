# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jwt
import pytest

from tortuga.auth.methods import AuthenticationMethod, \
    MultiAuthentionMethod, UsernamePasswordAuthenticationMethod,\
    JwtAuthenticationMethod
from tortuga.exceptions.authenticationFailed import AuthenticationFailed


class _TestAuthenticationMethod(AuthenticationMethod):
    """
    Test authentication method base class.

    """
    def __init__(self):
        super().__init__()
        self.on_authentication_succeeded_called = None
        self.on_authentication_failed_called = False

    def on_authentication_succeeded(self, username: str):
        self.on_authentication_succeeded_called = username

    def on_authentication_failed(self):
        self.on_authentication_failed_called = True


class SuccessAuthenticationMethod(_TestAuthenticationMethod):
    """
    An authentication method that always succeeds.

    """
    def __init__(self):
        super().__init__()
        self._on_authentication_succeeded_called = False

    def do_authentication(self, username: str = None, **kwargs) -> str:
        return username


class FailedAuthenticationMethod(_TestAuthenticationMethod):
    """
    An authentication method that always fails.

    """
    def do_authentication(self, **kwargs) -> str:
        raise AuthenticationFailed()


def test_on_authentication_succeeded():
    #
    # Assert that the on_authentication_succeeded method is called
    # when authentication has succeeded
    #
    method = SuccessAuthenticationMethod()
    method.authenticate(username='username')
    assert method.on_authentication_succeeded_called == 'username'
    assert method.on_authentication_failed_called is False

    #
    # Try skipping callbacks...
    #
    method = SuccessAuthenticationMethod()
    method.authenticate(username='username', skip_callbacks=True)
    assert method.on_authentication_succeeded_called is None
    assert method.on_authentication_failed_called is False


def test_on_authentication_failed():
    #
    # Assert that the on_authentication_failed method is called when
    # authentication has failed
    #
    method = FailedAuthenticationMethod()
    try:
        method.authenticate(username='username')
    except AuthenticationFailed:
        pass
    assert method.on_authentication_failed_called is True
    assert method.on_authentication_succeeded_called is None

    #
    # Try skipping callbacks...
    #
    method = FailedAuthenticationMethod()
    try:
        method.authenticate(username='username', skip_callbacks=True)
    except AuthenticationFailed:
        pass
    assert method.on_authentication_failed_called is False
    assert method.on_authentication_succeeded_called is None


def test_multi_authentication_method():
    #
    # Assert that at least one success in a chain of authentication methods
    # results in a success
    #
    methods = [
        SuccessAuthenticationMethod(),
        FailedAuthenticationMethod()
    ]
    method = MultiAuthentionMethod(methods)
    assert method.authenticate(username='username')

    #
    # Make sure on_authentication_succeeded is called on all methods
    #
    for m in methods:
        assert m.on_authentication_succeeded_called == 'username'
        assert m.on_authentication_failed_called is False

    #
    # Try with methods reversed...
    #
    methods = [
        FailedAuthenticationMethod(),
        SuccessAuthenticationMethod()
    ]
    method = MultiAuthentionMethod(methods)
    assert method.authenticate(username='username') == 'username'

    #
    # Make sure on_authentication_succeeded is called on all methods
    #
    for m in methods:
        assert m.on_authentication_succeeded_called == 'username'
        assert m.on_authentication_failed_called is False

    #
    # Make sure that all falurese results in a failure
    #
    methods = [
        FailedAuthenticationMethod(),
        FailedAuthenticationMethod()
    ]
    method = MultiAuthentionMethod(methods)
    with pytest.raises(AuthenticationFailed):
        method.authenticate(username='username')

    #
    # Make sure on_authentication_failed is called on all methods
    #
    for m in methods:
        assert m.on_authentication_failed_called is True
        assert m.on_authentication_succeeded_called is None


def test_username_password_authentication_method():
    method = UsernamePasswordAuthenticationMethod()

    #
    # Assert that a valid username/password combination returns the
    # username
    #
    assert method.authenticate(username='admin',
                               password='password') == 'admin'

    #
    # Assert that an invalid username/password combination raises
    # an AuthenticationFailed exception
    #
    with pytest.raises(AuthenticationFailed):
        method.authenticate(username='admin', password='invalid')


def test_jwt_authentication_method():
    token_data = {
        'username': 'admin'
    }
    secret = 'TestSecretKey'
    token = jwt.encode(token_data, secret)

    method = JwtAuthenticationMethod(secret=secret)

    #
    # Assert that a valid token returns the username
    #
    assert method.authenticate(token=token) == 'admin'

    #
    # Assert that an invalid token raises an AuthenticationFailed exception
    #
    with pytest.raises(AuthenticationFailed):
        method.authenticate(token='bad_token')
