import sys
import pathlib

MODULE_PATH = pathlib.Path(__file__).parent.absolute()

sys.path.append(str(MODULE_PATH))

from local import *
import ajconsole
from ajcore import (
    GEN_PERIOD_DICT,
    FemaleMP,
    FEMALE_MP_LIST,
    get_gen_by_year,
    get_year_by_gen,
)


__version__ = "22.10.22"

__all__ = [
    "ajconsole",
    "GEN_PERIOD_DICT",
    "FEMALE_MP_LIST",
    "MPSpeechRecord",
    "core",
    "Conference",
    "Conferences",
    "MP",
    "FemaleMP",
    "MPList",
    "Assembly",
    "Speak",
    "Movie",
    "PDFText",
    "ConfBuilder",
    "period",
    "get_gen_by_year",
    "get_year_by_gen",
    "get_mp_speech_record",
    "get_conf_from_keys",
    "pdf_to_dict",
]
