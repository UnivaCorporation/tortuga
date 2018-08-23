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

import pytest
from mock import MagicMock

from tortuga.exceptions.authenticationFailed import AuthenticationFailed


@pytest.fixture
def SuccessAuthenticationMethod(request):
    from tortuga.auth.methods import AuthenticationMethod

    method = AuthenticationMethod()
    method.do_authentication = MagicMock()
    method.on_authentication_succeeded = MagicMock()
    method.on_authentication_failed = MagicMock()

    yield method


@pytest.fixture
def FailedAuthenticationMethod():
    from tortuga.auth.methods import AuthenticationMethod

    def raise_authentication_failure_exception(username, **kwargs):
        raise AuthenticationFailed()

    method = AuthenticationMethod()
    method.do_authentication = MagicMock(
        side_effect=raise_authentication_failure_exception)
    method.on_authentication_failed = MagicMock()
    method.on_authentication_succeeded = MagicMock()

    yield method


def test_on_authentication_succeeded(SuccessAuthenticationMethod):
    #
    # Assert that the on_authentication_succeeded method is called
    # when authentication has succeeded
    #

    username = 'username'

    assert SuccessAuthenticationMethod.authenticate(username=username)

    SuccessAuthenticationMethod.do_authentication.assert_called_with(
        username=username)

    SuccessAuthenticationMethod.on_authentication_succeeded.assert_called()
    SuccessAuthenticationMethod.on_authentication_failed.assert_not_called()


def test_on_authentication_succeeded_without_callbacks(
        SuccessAuthenticationMethod):
    username = 'username'

    #
    # Try skipping callbacks...
    #
    assert SuccessAuthenticationMethod.authenticate(username='username',
                                             skip_callbacks=True)

    SuccessAuthenticationMethod.do_authentication.assert_called_with(
        username=username)

    SuccessAuthenticationMethod.on_authentication_succeeded.assert_not_called()
    SuccessAuthenticationMethod.on_authentication_failed.assert_not_called()


def test_on_authentication_failed(FailedAuthenticationMethod):

    #
    # Assert that the on_authentication_failed method is called when
    # authentication has failed
    #
    with pytest.raises(AuthenticationFailed):
        FailedAuthenticationMethod.authenticate(username='username')

    FailedAuthenticationMethod.on_authentication_failed.assert_called()


def test_on_authentication_failed_without_callback(FailedAuthenticationMethod):
    #
    # Try skipping callbacks...
    #
    with pytest.raises(AuthenticationFailed):
        FailedAuthenticationMethod.authenticate(username='username',
                                                skip_callbacks=True)

    FailedAuthenticationMethod.on_authentication_failed.assert_not_called()
    FailedAuthenticationMethod.on_authentication_succeeded.assert_not_called()


def test_multi_authentication_method(
        SuccessAuthenticationMethod, FailedAuthenticationMethod):
    from tortuga.auth.methods import MultiAuthentionMethod

    #
    # Assert that at least one success in a chain of authentication methods
    # results in a success
    #
    methods = [
        SuccessAuthenticationMethod,
        FailedAuthenticationMethod,
    ]
    method = MultiAuthentionMethod(methods)
    assert method.authenticate(username='username')

    #
    # Make sure on_authentication_succeeded is called on all methods
    #
    for m in methods:
        m.on_authentication_succeeded.assert_called()
        m.on_authentication_failed.assert_not_called()


def test_multi_authentication_method_variation1(
        SuccessAuthenticationMethod, FailedAuthenticationMethod):
    from tortuga.auth.methods import MultiAuthentionMethod

    #
    # Try with methods reversed...
    #
    methods = [
        FailedAuthenticationMethod,
        SuccessAuthenticationMethod,
    ]
    method = MultiAuthentionMethod(methods)
    assert method.authenticate(username='username')

    #
    # Make sure on_authentication_succeeded is called on all methods
    #
    for m in methods:
        m.on_authentication_succeeded.assert_called()
        m.on_authentication_failed.assert_not_called()


def test_multi_authentication_method_variation2(
        SuccessAuthenticationMethod, FailedAuthenticationMethod):
    from tortuga.auth.methods import MultiAuthentionMethod

    #
    # Make sure that all falurese results in a failure
    #
    methods = [
        FailedAuthenticationMethod,
        FailedAuthenticationMethod,
    ]
    method = MultiAuthentionMethod(methods)
    with pytest.raises(AuthenticationFailed):
        method.authenticate(username='username')

    #
    # Make sure on_authentication_failed is called on all methods
    #
    for m in methods:
        m.on_authentication_failed.assert_called()
        m.on_authentication_succeeded.assert_not_called()


def test_username_password_authentication_method(dbm):
    from tortuga.auth.methods import UsernamePasswordAuthenticationMethod

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
