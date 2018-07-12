import pytest

from tortuga.resourceAdapterConfiguration import settings


def test_boolean():
    bs = settings.BooleanSetting()

    #
    # Assert that a non boolean value raises a validation error
    #
    with pytest.raises(settings.SettingValidationError):
        bs.validate('1')

    #
    # Assert that a boolean value does not raise a validation error
    #
    bs.validate('True')
    bs.validate('False')

    #
    # Assert that list validation works too
    #
    bs.list = True
    bs.validate('True, False')
    bs.list = False

    #
    # Assert value is in values list
    #
    bs.values = ['True']
    with pytest.raises(settings.SettingValidationError):
        bs.validate('False')
    bs.validate('True')

    #
    # Assert dump returns valid values
    #
    assert bs.dump('True') is True
    bs.list = True
    assert bs.dump('True, False') == [True, False]


def test_string():
    ss = settings.StringSetting()

    #
    # Assert that a non-string value raises a validation error
    #
    with pytest.raises(settings.SettingValidationError):
        ss.validate(1)

    #
    # Assert that a string value does not raise a validation error
    #
    ss.validate('abc')

    #
    # Assert value is in values list
    #
    ss.values = ['abc', 'def']
    with pytest.raises(settings.SettingValidationError):
        ss.validate('ghi')
    ss.validate('def')

    #
    # Assert dump returns valid values
    #
    assert ss.dump('abc') == 'abc'
    ss.list = True
    assert ss.dump('abc, def') == ['abc', 'def']


def test_integer():
    is_ = settings.IntegerSetting()

    #
    # Assert that a non-integer value raises a validation error
    #
    with pytest.raises(settings.SettingValidationError):
        is_.validate('abc')

    #
    # Assert that an integer value does not raise a validation error
    #
    is_.validate('3')

    #
    # Assert that list validation works too
    #
    is_.list = True
    is_.validate('3, 4, 5')
    is_.list = False

    #
    # Assert value is in values list
    #
    is_.values = ['1', '2']
    with pytest.raises(settings.SettingValidationError):
        is_.validate('3')
    is_.validate('1')

    #
    # Assert dump returns valid values
    #
    assert is_.dump('1') == 1
    is_.list = True
    assert is_.dump('1, 2') == [1, 2]


def test_file():
    fs = settings.FileSetting(must_exist=False)

    #
    # Assert that a non-string value raises a validation error
    #
    with pytest.raises(settings.SettingValidationError):
        fs.validate(1)

    #
    # Assert that a string value does not raise a validation error
    #
    fs.validate('abc')

    #
    # Assert that if a file doesn't exist, a validation error is raised
    #
    fs.must_exist = True
    with pytest.raises(settings.SettingValidationError):
        fs.validate('abc')

    #
    # Assert that if a file does exist, nothing happens
    #
    fs.must_exist = True
    fs.validate(__file__)

    #
    # Assert value is in values list
    #
    fs.must_exist = False
    fs.values = ['abc', 'def']
    with pytest.raises(settings.SettingValidationError):
        fs.validate('ghi')
    fs.validate('def')
