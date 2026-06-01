import sys


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
    gen_version_number.gen_version_info()

try:
    from version_info import __git_hash__, __git_raw_hash__
except ImportError:
    __git_hash__ = "***version info unavalible***"
    __git_raw_hash__ = None

def get_version_number():
    return __git_hash__

def get_hash():
    return __git_raw_hash__