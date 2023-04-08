#!/usr/bin/env python3

import os
import re
from dearAJ import *
import pickle

"""
`Description*` files under `dearAJ/src/`
contains all the conferences that includes
female MP speeches.
"""

_DATA_PATH = "./dearAJ/src"

DATA_FILES: list[str] = []

for file in os.listdir(_DATA_PATH):
    if file.startswith("Description"):
        DATA_FILES.append(file)


def get_desc(filename: str) -> dict:
    with open(filename, "rb") as file:
        return pickle.load(file)


def get_desc_by_year(year: int) -> dict:
    filename = f"{_DATA_PATH}/Description_{year}.pickle"
    return get_desc(filename)


if __name__ == "__main__":
    print(DATA_FILES)
    print(get_desc_by_year(2015))
