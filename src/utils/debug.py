import os
import traceback


def except_hook(err_type, err_msg, err_traceback):
    error = dict()
    error["type"] = err_type.__name__
    error["message"] = str(err_msg)
    try:
        error["file"] = os.path.split(err_traceback.tb_frame.f_code.co_filename)[1]
        error["line"] = err_traceback.tb_lineno
        error["traceback"] = "".join(traceback.format_tb(err_traceback))
    except AttributeError:
        pass
    print("ERROR:")
    for k, v in error.items():
        if k is "traceback":
            print("{}:\n{}".format(k.title(), v))
        else:
            print("{}: {}".format(k.title(), v))
