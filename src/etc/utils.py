from functools import wraps
from pathlib import Path
import time

# Note: Only use Paths for when things are being opened.
# Store path attributes as their original string

def validate_path(path_str: str, 
                filetype: str = "file", 
                extension: str = "",
                obj: str = "",
                action: str = "open",
                exception: bool = False) -> bool:
    path = Path(path_str)
    error_msg = lambda err: "Cannot {} {} {}: {} at location {}."\
                    .format(action, obj, err, filetype, path_str)
    if path_str == "":
        print(msg := error_msg("Empty string.".format(filetype)))
        if exception:
            raise FileNotFoundError(msg)
        return False
    if action == "open":
        if not path.exists():
            print(msg := error_msg("No {} exists".format(filetype)))
            if exception:
                raise FileNotFoundError(msg)
            return False
        if path.is_dir():
            if filetype == "file":
                print(msg := error_msg("Found directory, not file"))
                if exception:
                    raise IsADirectoryError(msg)
                return False
            if not path.glob(extension):
                print(msg := error_msg("No {} files found".format(extension)))
                if exception:
                    raise NameError(msg)
                return False
        if path.is_file():
            if filetype == "directory":
                print(msg := error_msg("Found file, not directory"))
                if exception:
                    raise NotADirectoryError(msg)
                return False
            if not path.name.endswith(extension):
                print(msg := error_msg("File is not of type {}".format(extension)))
                if exception:
                    raise NameError(msg)
                return False
    if action == "write":
        if exception:
            raise NotImplementedError()
        return False
    return True

def debug(func):
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug

def timer(func):
    def time(*args):
        ts = time.time()
        result = func(*args)
        te = time.time()
        print('%r  %2.2f ms' % (func.__name__, (te-ts) * 1000))
        return result
    return time