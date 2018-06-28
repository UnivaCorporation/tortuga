import pytest

from tortuga.resourceAdapterConfiguration.validator import \
    ConfigurationValidator, ValidationError
from tortuga.resourceAdapterConfiguration import \
    settings as settings


def test_defaults():
    s = {
        'integer': settings.IntegerSetting(default=3),
        'string': settings.StringSetting(default='abc')
    }
    p = ConfigurationValidator(s)

    #
    # Assert default values are set
    #
    assert p['integer'] == 3
    assert p['string'] == 'abc'


def test_required():
    s = {
        'integer': settings.IntegerSetting(required=True),
        'string': settings.StringSetting()
    }
    p = ConfigurationValidator(s)

    #
    # Assert that a required value, if not provided, throws an validation
    # error
    #
    with pytest.raises(ValidationError) as err_info:
        p.validate()
    err: ValidationError = err_info.value
    #
    # Should not raise a validation error, because it is not marked as
    # required
    #
    assert 'string' not in err.errors.keys()
    #
    # Should raise a validation error, because it is required
    #
    assert str(err.errors['integer']) == 'Setting is required'

    #
    # Assert that if the value is in fact provided, no errors are raised
    #
    p['integer'] = 5
    p.validate()


def test_validate_mutually_exclusive():
    s = {
        'integer': settings.IntegerSetting(mutually_exclusive=['string']),
        'string': settings.StringSetting()
    }
    p = ConfigurationValidator(s)

    #
    # Assert no validation errors raised
    #
    p['integer'] = 1
    p.validate()

    #
    # Assert mutually exclusive validation error raised
    #
    p['string'] = 'abc'
    with pytest.raises(ValidationError) as err_info:
        p.validate()
    err: ValidationError = err_info.value
    #
    # Should not raise a validation error, because mutually exclusive flag is
    # set on integer only
    #
    assert 'string' not in err.errors.keys()
    #
    # Should raise a validation error, because it has mutually exclusive
    # setting
    #
    assert str(err.errors['integer']) == 'Mutually exclusive with string'


def test_validate_requires():
    s = {
        'integer': settings.IntegerSetting(requires=['string']),
        'string': settings.StringSetting()
    }
    p = ConfigurationValidator(s)

    #
    # Assert requires validation error raised
    #
    p['integer'] = 1
    with pytest.raises(ValidationError) as err_info:
        p.validate()
    err: ValidationError = err_info.value
    #
    # Should not raise a validation error, because requires flag is
    # set on integer only
    #
    assert 'string' not in err.errors.keys()
    #
    # Should raise a validation error, because it has a requires setting
    #
    assert str(err.errors['integer']) == 'Requires string'

    #
    # Assert no validation errors
    #
    p['string'] = 'abc'
    p.validate()


def test_dump_load():
    s = {
        'bool': settings.BooleanSetting(),
        'integer': settings.IntegerSetting(),
        'string': settings.StringSetting(),
        'file': settings.FileSetting(must_exist=False)
    }
    p = ConfigurationValidator(s)

    p['bool'] = True
    p['integer'] = 3
    p['string'] = 'abc'
    p['file'] = 'file.txt'

    #
    # Assert that what we dump is what we would expect
    #
    expected_data = {
        'bool': True,
        'integer': 3,
        'string': 'abc',
        'file': 'file.txt'
    }
    assert p.dump() == expected_data

    #
    # Make sure that loading the data does the same thing
    #
    p2 = ConfigurationValidator(s)
    p2.load(expected_data)
    assert p2.dump() == expected_data


def test_secret():
    s = {
        'string': settings.StringSetting(secret=True)
    }
    p = ConfigurationValidator(s)
    p['string'] = 'abc123'

    #
    # Assert that fields marked as secret are redacted in a secure dump
    #
    expected_data = {
        'string': ConfigurationValidator.REDACTED_STRING
    }
    assert p.dump() == expected_data

    #
    # Assert that fields are marked as secred are revealed in an insecure
    # dump
    #
    expected_data = {
        'string': 'abc123'
    }
    assert p.dump(secure=False) == expected_data
