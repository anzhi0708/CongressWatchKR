#!/usr/bin/env python

from konlpy.tag import Kkma
from dearaj import *
import pickle
from pprint import pp


def get_confdescription_by_year(year: int) -> list[ConfDescription]:
    full_file_path = f"./Description_{year}.pickle"
    with open(full_file_path, "rb") as target:
        result = pickle.load(target)
    result.sort()
    return result
