import time
from functools import wraps

from wykop import WykopAPI, WykopAPIError
from taktyk.base_logger import logger

errors_dict = {}


def repeat(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        n = 0
        e = None
        while n < 20:
            try:
                result = fn(*args, **kwargs)
                if n > 0:
                    logger.info(f"Recover with {fn}")
                    logger.info(f"errors_count: {sum(errors_dict.values())} | Errors dict: {errors_dict}")
                return result
            except WykopAPIError as ex:
                logger.info(f"Error during {fn}: {ex}")
                key = ex.args[1]
                if key in errors_dict:
                    errors_dict[key] += 1
                else:
                    errors_dict[key] = 1
                n = n + 1
                e = ex
                time.sleep(1)
                pass
        raise e

    return wrapper


def for_all_methods(decorator):
    def decorate(cls):
        for attr in dir(cls):
            if callable(getattr(cls, attr)) and not attr.startswith("_"):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


@for_all_methods(repeat)
class ApiClientWrapper(WykopAPI):
    pass
