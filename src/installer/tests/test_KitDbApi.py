from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.db.kitDbApi import KitDbApi


def test_getKitList(dbm):
    result = KitDbApi().getKitList()

    assert isinstance(result, TortugaObjectList)
