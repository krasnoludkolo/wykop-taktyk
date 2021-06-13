import time

from wykop import WykopAPI


class ApiClientWrapper(WykopAPI):
    def __getattribute__(self, item):
        method = object.__getattribute__(self, item)
        if not method:
            raise Exception("Method %s not implemented" % item)
        if callable(method):
            time.sleep(0.3)
        return method
