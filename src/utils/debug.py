import fnmatch
import os
import shutil
import traceback
from enum import Enum


def remove_all_pycache_dir():
    try:
        for root, dirs, files in os.walk(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir))):
            for dir in dirs:
                pattern = "__pycache__"
                if fnmatch.fnmatch(dir, pattern):
                    pycache_dir_path = os.path.join(root, dir)
                    shutil.rmtree(pycache_dir_path)
    except FileNotFoundError:
        print("\"__pycache__\" directory is not found.")


class EnumNoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


# Debug console color code
class ColorCode(EnumNoValue):
    COLOR_RED = '\033[31m'
    COLOR_GREEN = '\033[32m'
    COLOR_YELLOW = '\033[33m'
    COLOR_BLUE = '\033[34m'
    COLOR_MAGENTA = '\033[35m'
    COLOR_CYAN = '\033[36m'
    COLOR_WHITE = '\033[37;1m'
    COLOR_END = '\033[0m'


def except_hook(err_type, err_msg, err_traceback):
    error = dict()
    error["type"] = err_type.__name__
    error["message"] = str(err_msg)
    try:
        error['file'] = os.path.split(err_traceback.tb_frame.f_code.co_filename)[1]
        error['line'] = err_traceback.tb_lineno
        error['traceback'] = ''.join(traceback.format_tb(err_traceback))
    except AttributeError:
        pass
    # print(str(ColorCode.COLOR_RED.value) + "ERROR:" + str(ColorCode.COLOR_END.value))
    print("ERROR:")
    for k, v in error.items():
        # if k is "traceback":
        #     print("{}{}:\n{}{}".format(str(ColorCode.COLOR_RED.value), k.title(),
        #                                str(ColorCode.COLOR_WHITE.value), v) + str(ColorCode.COLOR_END.value))
        # else:
        #     print("{}{}: {}{}".format(str(ColorCode.COLOR_RED.value), k.title(),
        #                               str(ColorCode.COLOR_WHITE.value), v) + str(ColorCode.COLOR_END.value))
        if k is "traceback":
            print("{}:\n{}".format(k.title(), v))
        else:
            print("{}: {}".format(k.title(), v))


if __name__ == "__main__":
    remove_all_pycache_dir()
