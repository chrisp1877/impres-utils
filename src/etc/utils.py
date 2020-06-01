from functools import wraps
from pathlib import Path
import timeit
import logging
from PIL import Image

# Note: Only use Paths for when things are being opened.
# Store path attributes as their original string

logger = logging.Logger('catch_all')

def validate_path(func):
    def validate_path_wrapper(*args):
        path, path_str = Path(args[1]), args[1]
        func.__qualname__.split(".")
        obj, action = tuple(func.__qualname__.split("."))
        if "dir" not in action:
            filetype = "file"
            ext = ".demo" if obj == "Demo" else ".docx"
        else:
            action = action.split("_")[0]
            filetype, ext = "directory", ""
        err = lambda e: "Cannot {} {} {}: {} at location {}."\
                    .format(action, obj.capitalize(), filetype, e, path_str)
        if action == "load":
            if path_str == "":
                raise FileNotFoundError(err("Empty path."))
            if not path.exists():
                raise FileNotFoundError(err(f"No {filetype} exists"))
            if path.is_dir():
                if filetype =="file":
                    raise IsADirectoryError(err(f"Need {ext} file, not directory"))
                if not path.glob(ext):
                    raise NameError(err(f"No {ext} files found"))
            if path.is_file():
                if filetype == "directory":
                    raise NotADirectoryError(err("Found file, not directory"))
                if not path.name.endswith(ext):
                    raise NameError(err(f"File is not of type {ext}"))
        if action == "write": #empty string -> overwrie fail, is OK
            raise NotImplementedError()
        return(func(*args))
    return validate_path_wrapper
    
def debug(func):
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()] 
        signature = ", ".join(args_repr + kwargs_repr) 
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}") 
        return value
    return wrapper_debug

def timefunc(func):
    def wrap(*args):
        t0 = timeit.default_timer()
        func(*args)
        t1 = timeit.default_timer()
        print(f"Function '{func.__qualname__}, args: {args}:' took {1000*(t1-t0)}ms.")
    return wrap