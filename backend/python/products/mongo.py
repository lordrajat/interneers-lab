from django.conf import settings
from mongoengine import connect

_IS_CONNECTED = False


def connect_mongo() -> None:
    global _IS_CONNECTED
    if _IS_CONNECTED:
        return

    connect(alias="default", **settings.MONGODB_SETTINGS)
    _IS_CONNECTED = True
