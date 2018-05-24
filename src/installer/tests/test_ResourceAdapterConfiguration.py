import pytest

from tortuga.exceptions.resourceAlreadyExists import ResourceAlreadyExists
from tortuga.resourceAdapterConfiguration.manager import \
    ResourceAdapterConfigurationManager
from tortuga.exceptions.resourceNotFound import ResourceNotFound


mgr = ResourceAdapterConfigurationManager()


def test_create_duplicate(dbm):
    with dbm.session() as session:
        with pytest.raises(ResourceAlreadyExists):
            mgr.create(session, 'aws', 'default')

        session.commit()


def test_create_unique(dbm):
    cfg_name = 'test_default'

    with dbm.session() as session:
        mgr.create(session, 'aws', cfg_name, {
            'test_default_key': 'test_default_value',
        })

        session.commit()

        cfg = mgr.get(session, 'aws', cfg_name)

        assert cfg.name == cfg_name

        for setting in cfg.settings:
            if setting.key == 'test_default_key':
                break
        else:
            assert 0, "Setting not found"

        mgr.delete(session, 'aws', cfg_name)

        session.commit()

        with pytest.raises(ResourceNotFound):
            mgr.get(session, 'aws', cfg_name)
