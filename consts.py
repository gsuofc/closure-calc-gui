import os
import sys

AUTHORS = ['Gavin Schultz']

FILE_PROG_MAGIC = "GS_CLOSURE_CALC_GUI"

REPORT_VERSION = 3
FILE_VERSION = 2 # Prior to 1.3, files did not have any headers. 
MIN_FILE_VERSION = 1

SUPPORT_LEGACY_FILE_FORMAT = True # In case we ever want to drop support for this, we can prevent opening files without the header

FIELDS_NEEDED = [
            "deg", "min", "sec",
            "distance", "radius", "arc",
            "rb_deg", "rb_min", "rb_sec"
        ]

def is_frozen():
    return getattr(sys, 'frozen', False)

if not is_frozen():
    import gen_version_number
    gen_version_number.gen_version_info("Running as .py")

try:
    from version_info import __git_hash__, __git_raw_hash__, __time_built__, __build_method__
except ImportError:
    __git_hash__ = "***version info unavalible***"
    __git_raw_hash__ = None
    __time_built__ = "***info unavalible***"
    __build_method__ = "Not Built (Running as .py)"

def get_version_number():
    return __git_hash__

def get_hash():
    return __git_raw_hash__

def build_date():
    return __time_built__

def build_method():
    return __build_method__

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)