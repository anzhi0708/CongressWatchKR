#!/usr/bin/env python3

from STOPWORDS import SKIP
from pprint import pp
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Union, Callable, Optional, NewType, NamedTuple
from abc import ABC, abstractmethod
from os import get_terminal_size
from collections import namedtuple
import os
import subprocess
from dearAJ import *
from dearAJ import ConfDescription
import pickle
from enum import Enum, auto
import fire


COLUMNS, ROWS = get_terminal_size()

Index = NewType("Index", int)


"""
- plotting
- analysing word frequency
- reading conf descriptions
"""


class Gender(Enum):
    MALE = auto()
    FEMALE = auto()
    BOTH = auto()


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


# Read local binary data files
for file in os.listdir(_DATA_PATH):
    if file.startswith("Description"):
        DATA_FILES.append(file)


def get_desc(filename: str) -> list[ConfDescription]:
    with open(filename, "rb") as file:
        data = file.read()
        return pickle.loads(data)


def get_desc_by_year(year: int) -> list[ConfDescription]:
    filename = f"{_DATA_PATH}/Description_{year}.pickle"
    result = get_desc(filename)
    return result


def print_confdesc_of_year(year: int) -> None:
    desc = get_desc_by_year(year)
    print("\r", end="", flush=True)
    print(desc)


def get_word_freq_of_year(year: int) -> tuple[dict[str, int]]:
    with open(f"{_DATA_PATH}/{_WORD_FREQ_FILE_PREFIX}{year}.pickle", "rb") as file:
        data = file.read()
        objekt = pickle.loads(data)
        _male_wordfreq: dict = objekt[0]
        _female_wordfreq: dict = objekt[1]
        without_single_char_male: dict = {
            k: v for k, v in _male_wordfreq.items() if len(k) > 1 and k not in SKIP
        }
        without_single_char_female: dict = {
            k: v for k, v in _female_wordfreq.items() if len(k) > 1 and k not in SKIP
        }
        sorted_male: dict = {
            k: v
            for k, v in sorted(
                without_single_char_male.items(), key=lambda item: item[1], reverse=True
            )
        }
        sorted_female: dict = {
            k: v
            for k, v in sorted(
                without_single_char_female.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        }
        return (sorted_male, sorted_female)


def word_freq_look_up(
    fn_and_kwargs: tuple[Callable, dict], key: str, gender: Gender = Gender.BOTH
):
    LookUpResult: NamedTuple = namedtuple("LookUpResult", ["index", "count"])
    func: Callable = fn_and_kwargs[0]
    kwargs: dict = fn_and_kwargs[1]
    tup: tuple[dict[str, int]] = func(**kwargs)
    count_shown: Optional[int] = kwargs.get("top")

    class LookUpStrategy(ABC):
        @abstractmethod
        def execute(self, key: str, target: Union[dict, tuple]):
            pass

        pass

    class MaleOrFemale(LookUpStrategy):
        def execute(self, key: str, target: dict) -> tuple[Index, dict[str, int]]:
            """In this case, `target` is a dict."""
            index: Index = Index(0)
            for k in target:
                if k == key:
                    return LookUpResult(index=index, count={k: target[k]})
                else:
                    index += 1
                    continue

    class BothMaleAndFemale(LookUpStrategy):
        def execute(self, key: str, target: tuple):
            """In this case, `target` is a tuple[dict]."""
            result_male = MaleOrFemale().execute(key, target[0])
            result_female = MaleOrFemale().execute(key, target[1])
            return (result_male, result_female)

    target: Union[dict, tuple, None] = None
    if gender == Gender.MALE:
        target = tup[0]
        return MaleOrFemale().execute(key, target), {"count_shown[MALE]": count_shown}

    elif gender == Gender.FEMALE:
        target = tup[1]
        return MaleOrFemale().execute(key, target), {"count_shown[FEMALE]": count_shown}

    else:
        target = tup
        return BothMaleAndFemale().execute(key, target), {
            "count_shown[BOTH]": count_shown
        }


def get_word_freq(
    *,
    year: int,
    top: int = 0,
    min_male: int = 0,
    min_female: int = 0,
    greater_than: int = 0,
) -> tuple:
    objekt = get_word_freq_of_year(year)
    word_freq_male: dict[str, int] = objekt[0]
    word_freq_female: dict[str, int] = objekt[1]
    # If `top` is set, then ignore `min_male`, `min_female` and `greater_than`.
    if top > 0:
        i: int = 0
        result_male: dict = dict()
        result_female: dict = dict()
        for key in word_freq_male:
            result_male[key] = word_freq_male[key]
            i += 1
            if i == top:
                break
        i = 0  # reset `i` to 0
        for key in word_freq_female:
            result_female[key] = word_freq_female[key]
            i += 1
            if i == top:
                break
        return result_male, result_female

    if (min_male > 0) or (greater_than > 0):
        for word in word_freq_male:
            if word_freq_male[word] <= max(min_male, greater_than):
                word_freq_male.pop(word)
    if (min_female > 0) or (greater_than > 0):
        for word in word_freq_female:
            if word_freq_female[word] <= max(min_female, greater_than):
                word_freq_female.pop(word)

    return word_freq_male, word_freq_female


def print_word_freq_of_year(year: int):
    word_freq = get_word_freq_of_year(year)
    print("\r", end="", flush=True)
    pp(word_freq)


def print_word_freq(
    *,
    year: int,
    top: int = 0,
    min_male: int = 0,
    min_female: int = 0,
    greater_than: int = 0,
) -> None:
    word_freq = get_word_freq(
        year=year,
        top=top,
        min_male=min_male,
        min_female=min_female,
        greater_than=greater_than,
    )
    print("\r", end="", flush=True)
    pp(word_freq)


def plot_word_freq(
    *,
    year: int,
    top: int = 0,
    min_male: int = 0,
    min_female: int = 0,
    greater_than: int = 0,
    title: str = "Word Freq",
) -> None:
    font_location: str = "/Library/Fonts/NanumGothic-regular.ttf"
    font_name = fm.FontProperties(fname=font_location).get_name()
    matplotlib.rc("font", family=font_name, size=9)
    word_freq = get_word_freq(
        year=year,
        top=top,
        min_male=min_male,
        min_female=min_female,
        greater_than=greater_than,
    )
    male_word_freq = word_freq[0]
    female_word_freq = word_freq[1]
    # need 2 graphs
    pp(male_word_freq)
    plt.figure(figsize=(48, 8))
    plt.title(f"{year} {title} - Male (total:{len(male_word_freq)})")
    x_axis = [key for key in male_word_freq]
    y_axis = [item[1] for item in male_word_freq.items()]
    bar = plt.bar(x_axis, y_axis)
    plt.xticks(rotation=45)  # 旋转x轴标签
    plt.show()

    pp(female_word_freq)
    plt.figure(figsize=(48, 8))
    plt.title(f"{year} {title} - Female (total:{len(female_word_freq)})")
    x_axis = [key for key in female_word_freq]
    y_axis = [item[1] for item in female_word_freq.items()]
    bar = plt.bar(x_axis, y_axis)
    plt.xticks(rotation=45)  # 旋转x轴标签
    plt.show()


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


class Main:
    def wordfreq(
        self,
        year: int,
        top: int = 20,
        min_male: int = 0,
        min_female: int = 0,
        greater_than: int = 0,
        title: str = "Word Freq",
    ):
        """
        This command will plot the word frequency of parliamentary speeches in the specified year.
        e.g. `wordfreq 2020`
        """
        plot_word_freq(year=year, top=top)

    def comm(self, name: str):
        """
        This command takes in the name of a committee and then plots the historical changes in the proportion of female parliamentarians' speeches in meetings of that committee.
        e.g. `comm '환노위'`
        """
        plot_by_comm_name(name)

    def lookup(self, year: int, top: int, key: str):
        """
        This command, after arranging the word frequency and keywords in descending order, informs you of the position of the specified vocabulary in this ranking.
        """
        pp({"year": year, "top": top, "key": key})
        pp(word_freq_look_up((get_word_freq, {"year": year, "top": top}), key=key))

    def printwordfreqandclassification(self, year: int, top: int) -> None:
        """
        This command will display the word frequency along with the corresponding categories for each word.
        """
        word_freq = get_word_freq(
            year=year, top=top, min_male=0, min_female=0, greater_than=0
        )
        freq_male = word_freq[0]
        freq_female = word_freq[1]
        from classification import Word

        for key in freq_male:
            _word = Word(key)
            freq_male[key] = {
                "count": freq_male[key],
                "classification": [
                    k for k in _word.__dict__ if _word.__dict__[k] is True
                ],
            }
        pp(freq_male)
        print()
        for key in freq_female:
            _word = Word(key)
            freq_female[key] = {
                "count": freq_female[key],
                "classification": [
                    k for k in _word.__dict__ if _word.__dict__[k] is True
                ],
            }
        pp(freq_female)


if __name__ == "__main__":
    print("Data Files Found".center(COLUMNS, "="))
    pp(DATA_FILES)
    print("=" * COLUMNS)
    print()
    """
    plot_word_freq(year=2006, top=20)
    # Instead of using something like this to get a word's position:
    # word_freq_look_up(get_word_freq(year=2013, top=20), key="제도")
    # Use this:
    # word_freq_look_up((get_word_freq, {"year": 2013, "top": 20}, key=""제도)
    pp(word_freq_look_up((get_word_freq, {"year": 2013, "top": 20}), key="제도"))
    """
    fire.Fire(Main)
