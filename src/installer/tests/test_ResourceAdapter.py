import pytest

from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter


def test_failed_instantiation():
    class MyResourceAdapter(ResourceAdapter):
        pass

    with pytest.raises(NotImplementedError):
        MyResourceAdapter() 


def test_failed_instantiation():
    class MyResourceAdapter(ResourceAdapter):
        __adaptername__ = 'testadapter'

    MyResourceAdapter()
