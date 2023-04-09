#!/usr/bin/env python3

import os
import re
import subprocess
from dearAJ import *
from dearAJ import ConfDescription
import pickle

"""
`Description*` files under `dearAJ/src/`
contains all the conferences that includes
female MP speeches.
"""

_DATA_PATH: str = "./dearAJ/src"

_WORD_FREQ_FILE_PREFIX: str = "_test_abc_"

DATA_FILES: list[str] = []

TUI_LAUNCHER: str = "./app.py"

USER_PYTHON_INTERPRETER: str = "python3"


for file in os.listdir(_DATA_PATH):
    if file.startswith("Description"):
        DATA_FILES.append(file)


def get_desc(filename: str) -> list[ConfDescription]:
    with open(filename, "rb") as file:
        return pickle.load(file)


def get_desc_by_year(year: int) -> list[ConfDescription]:
    filename = f"{_DATA_PATH}/Description_{year}.pickle"
    result = get_desc(filename)
    return result


def print_confdesc_of_year(year: int) -> None:
    print(get_desc_by_year(year))


def get_word_freq_of_year(year: int) -> tuple:
    with open(f"{_DATA_PATH}/{_WORD_FREQ_FILE_PREFIX}{year}.pickle", "rb") as file:
        objekt = pickle.load(file)
        return objekt[0], type(objekt), len(objekt)


def print_word_freq_of_year(year: int):
    print(get_word_freq_of_year(year))


def plot_by_comm_name(query_name: str) -> None:
    current_path: str = os.getcwd()
    target_path: str = f"{current_path}/dearAJ/src"
    print(f"Entering {target_path}")
    os.chdir(target_path)
    command: list = [USER_PYTHON_INTERPRETER, "./plot_by_comm_name.py", query_name]
    print(f"Plotting {query_name}...")
    result = subprocess.run(command, stdout=subprocess.PIPE)
    print(result.stdout.decode("utf-8"))
    print(f"Leaving {target_path}")
    os.chdir(current_path)


def tui_show_pdf(filename: str) -> None:
    """Show the PDF analysis result in TUI mode"""
    command: list = [USER_PYTHON_INTERPRETER, TUI_LAUNCHER, filename]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    print(result.stdout.decode("utf-8"))


if __name__ == "__main__":
    print(DATA_FILES)
    print()
    get_desc_by_year(2014)
