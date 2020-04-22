import os
import traceback


def exceptHook(errType, errMsg, errTraceback):
    error = dict()
    error["type"] = errType.__name__
    error["message"] = str(errMsg)
    try:
        error["file"] = os.path.split(errTraceback.tb_frame.f_code.co_filename)[1]
        error["line"] = errTraceback.tb_lineno
        error["traceback"] = "".join(traceback.format_tb(errTraceback))
    except AttributeError:
        pass
    print("ERROR:")
    for k, v in error.items():
        if k is "traceback":
            print("{}:\n{}".format(k.title(), v))
        else:
            print("{}: {}".format(k.title(), v))
