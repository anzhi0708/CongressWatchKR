#!/usr/bin/env python3

from STOPWORDS import SKIP
from pprint import pp
from stage_3 import sort_dict
from functools import reduce
from collections import defaultdict
from dearAJ.src.ajconsole import Message
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Union, Callable, Optional, NewType, NamedTuple
from abc import ABC, abstractmethod
from collections import namedtuple
import os
import subprocess
from dearAJ import *
from dearAJ import ConfDescription
import pickle
from enum import Enum, auto
from classification import Word
import fire


log = Message(enabled=True).log
PICKLE_BIN_CONF_DESC_BY_NTH: str = "./NthAsmDescription_{NTH}.pickle"
FREQ_NTH: dict[int, list] = {
    18: [
        "./_overlap/_second_half_of_2008.pickle",
        "./dearAJ/src/_test_abc_2009.pickle",
        "./dearAJ/src/_test_abc_2010.pickle",
        "./dearAJ/src/_test_abc_2011.pickle",
        "./_overlap/_first_half_of_2012.pickle",
    ],
    19: [
        "./_overlap/_second_half_of_2012.pickle",
        "./dearAJ/src/_test_abc_2013.pickle",
        "./dearAJ/src/_test_abc_2014.pickle",
        "./dearAJ/src/_test_abc_2015.pickle",
        "./_overlap/_first_half_of_2016.pickle",
    ],
    20: [
        "./_overlap/_second_half_of_2016.pickle",
        "./dearAJ/src/_test_abc_2017.pickle",
        "./dearAJ/src/_test_abc_2018.pickle",
        "./dearAJ/src/_test_abc_2019.pickle",
        "./_overlap/_first_half_of_2020.pickle",
    ],
}

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

_WORD_FREQ_FILE_PREFIX: str = "_test_abc_"  # WordFreq by YEAR

DATA_FILES: list[str] = []  # ConfDesc files

TUI_LAUNCHER: str = "./app.py"  # TUI interface

USER_PYTHON_INTERPRETER: str = "python3"


# Read local binary data files
for file in os.listdir(_DATA_PATH):
    if file.startswith("Description"):
        DATA_FILES.append(file)


def get_freq_by_file(filename: str):
    with open(filename, "rb") as p:
        data = pickle.load(p)
        print(f"{filename}: {len(data)=}, {type(data)=}, {type(data[0])=}")
    return data


# for nth in FREQ_NTH:
#     for each_file in FREQ_NTH[nth]:
#         tup = get_freq_by_file(each_file)


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


def get_word_freq_by_filename(filename: str) -> tuple:
    log(f"Reading {filename}, size={os.path.getsize(filename)}")
    with open(filename, "rb") as file:
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


def get_word_freq_of_year(year: int) -> tuple[dict[str, int]]:
    filename = f"{_DATA_PATH}/{_WORD_FREQ_FILE_PREFIX}{year}.pickle"
    return get_word_freq_by_filename(filename)


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


def get_word_freq_by_file(
    *,
    file: str,
    top: int = 0,
    min_male: int = 0,
    min_female: int = 0,
    greater_than: int = 0,
) -> tuple:
    objekt = get_word_freq_by_filename(file)
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


def filter_tuple_using_builtin_stopwords(t: tuple[dict, dict]) -> tuple[dict, dict]:
    _male_wordfreq: dict = t[0]
    _female_wordfreq: dict = t[1]
    log("filtering male freqs")
    filtered_male: dict = {
        k: v for k, v in _male_wordfreq.items() if len(k) > 1 and k not in SKIP
    }
    log("filtering female freqs")
    filtered_female: dict = {
        k: v for k, v in _female_wordfreq.items() if len(k) > 1 and k not in SKIP
    }
    log("done filtering")
    return (sort_dict(filtered_male), sort_dict(filtered_female))


def get_word_freq_by_tuple(
    *,
    obj: tuple[dict, dict],
    top: int = 0,
    min_male: int = 0,
    min_female: int = 0,
    greater_than: int = 0,
) -> tuple:
    objekt = obj
    word_freq_male: dict[str, int] = objekt[0]
    word_freq_female: dict[str, int] = objekt[1]
    # If `top` is set, then ignore `min_male`, `min_female` and `greater_than`.
    log("Sorting male dict")
    word_freq_male = sort_dict(word_freq_male)
    log("Sorting female dict")
    word_freq_female = sort_dict(word_freq_female)
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
    """CLI Utility of CongressWatch.

    Run `python3 main.py` to see help information.

    Copyright 2023 Anji Wong.
    """

    __word = Word(" ")
    __LABELS: list[str] = []
    for __k in __word.__dict__:
        __LABELS.append(__k)
    __LOW_POLITICS: list[str] = [
        "women_related",
        "child_related",
        "educational",
        "environmental",
        "social_welfare",
        "healthcare",
        "media",
    ]
    __HIGH_POLITICS: list[str] = [
        "military",
        "deplomatic",
    ]

    def showlabels(self) -> list[str]:
        """
        This command will display the categories to which each word belongs in the word frequency statistics.
        """
        return self.__LABELS

    @staticmethod
    def get_word_freq_by_file(
        *,
        file: str,
        top: int = 0,
        min_male: int = 0,
        min_female: int = 0,
        greater_than: int = 0,
    ) -> tuple:
        return get_freq_by_file(file)

    @staticmethod
    def merge_word_freq(
        source: tuple[dict, dict], target: tuple[dict, dict]
    ) -> tuple[dict, dict]:
        log("Merging 2 tuples")
        source_male = source[0]
        source_female = source[1]
        target_male = target[0]
        target_female = target[1]
        result_male = defaultdict(int)
        result_female = defaultdict(int)
        log("Merging freq (male, 1/2)")
        for key in source_male:
            result_male[key] += source_male[key]
        log("Merging freq (male, 2/2)")
        for key in target_male:
            result_male[key] += target_male[key]
        log("Merging freq (female, 1/2)")
        for key in source_female:
            result_female[key] += source_female[key]
        log("Merging freq (female, 2/2)")
        for key in target_female:
            result_female[key] += target_female[key]
        log("Done merging freqs")
        return (result_male, result_female)

    @staticmethod
    def merge_all_by_nth_freq_files() -> list[tuple]:
        freqs = []
        for nth in FREQ_NTH:
            parts = []
            for file in FREQ_NTH[nth]:
                log(f"Getting wordfreq from file {file}, size={os.path.getsize(file)}")
                part = Main.get_word_freq_by_file(file=file)  # returned None?
                parts.append(part)
            log(f"{len(parts)=}")
            for e in parts:
                log(f"{type(e)=}")
            parts_result = reduce(Main.merge_word_freq, parts)
            freqs.append(parts_result)
        return freqs

    def plotfreq(
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
        e.g. `plotfreq 2020`
        """
        plot_word_freq(year=year, top=top)

    def comm(self, name: str):
        """
        This command takes in the name of a committee and then plots the historical changes in the proportion of female parliamentarians' speeches in meetings of that committee.
        e.g. `comm '환노위'`
        """
        plot_by_comm_name(name)

    def printfreq(self, year: int, top: int):
        """
        This command will plot the word frequency of parliamentary speeches in the specified year.
        e.g. `printfreq 2020 20`
        """
        print_word_freq(year=year, top=top)

    def savefreq(self, year: int, top: int):
        """
        Saves word freq data to .csv file.
        """
        import csv

        print("\rReading wordfreq data...", end="", flush=True)
        male_freq, female_freq = get_word_freq(year=year, top=top)
        with open(f"./wordfreq_output_{year}_top{top}.csv", "w") as output:
            writer = csv.writer(output)
            writer.writerow(["Index", "Male", "Female"])
            row_male: list[str] = []
            print("\rProcessing male wordfreq...")
            for key in male_freq:
                word = key
                freq = male_freq[key]
                row_male.append(f"{word} {freq}")
            row_female: list[str] = []
            print("Processing female wordfreq...")
            for key in female_freq:
                word = key
                freq = female_freq[key]
                row_female.append(f"{word} {freq}")
            print("Saving data...")
            for i in range(top):
                writer.writerow([i + 1, row_male[i], row_female[i]])
        print("Done.")

    def lookup(self, year: int, top: int, key: str):
        """
        This command, after arranging the word frequency and keywords in descending order, informs you of the position of the specified vocabulary in this ranking.
        """
        pp({"year": year, "top": top, "key": key})
        pp(word_freq_look_up((get_word_freq, {"year": year, "top": top}), key=key))

    def detail(self, year: int, top: int) -> None:
        """
        Print word frequency, corresponding labels, and corresponding percentages. The calculation of percentages depends on the provided 'top' parameter, i.e., the percentage refers to the proportion of the word in the **printed vocabularies**.
        """
        male_freq, female_freq = self.__withlabels(year, top)
        male_word_count: int = 0
        female_word_count: int = 0
        male_word_types: dict[str, int] = dict()
        female_word_types: dict[str, int] = dict()

        for k in male_freq:
            male_word_count += (this_count := male_freq[k]["count"])
            labels: list[str | None] = male_freq[k]["classification"]
            if not labels:
                if "unknown" not in male_word_types:
                    male_word_types["unknown"] = this_count
                else:
                    male_word_types["unknown"] += this_count
            else:
                for label in labels:
                    if label not in male_word_types:
                        male_word_types[label] = this_count
                    else:
                        male_word_types[label] += this_count

        for k in female_freq:
            female_word_count += (this_count := female_freq[k]["count"])
            labels: list[str | None] = female_freq[k]["classification"]
            if not labels:
                if "unknown" not in female_word_types:
                    female_word_types["unknown"] = this_count
                else:
                    female_word_types["unknown"] += this_count
            else:
                for label in labels:
                    if label not in female_word_types:
                        female_word_types[label] = this_count
                    else:
                        female_word_types[label] += this_count

        print("Male\n")
        pp(male_freq)
        print()
        print("Female\n")
        pp(female_freq)

        for k in male_word_types:
            male_word_types[k] = (
                male_word_types[k],
                male_word_types[k] / male_word_count,
            )

        for k in female_word_types:
            female_word_types[k] = (
                female_word_types[k],
                female_word_types[k] / female_word_count,
            )

        male_word_types = dict(
            sorted(male_word_types.items(), key=lambda item: item[1][1], reverse=True)
        )

        female_word_types = dict(
            sorted(female_word_types.items(), key=lambda item: item[1][1], reverse=True)
        )
        print()
        print("Male\n")
        print(male_word_types)
        print()
        print("Female\n")
        print(female_word_types)
        print()

        high_male = 0
        low_male = 0
        high_female = 0
        low_female = 0

        for T in male_word_types:
            t = male_word_types[T]
            percentage = t[1]
            if T in self.__HIGH_POLITICS:
                high_male += percentage
            elif T in self.__LOW_POLITICS:
                low_male += percentage
            else:
                pass

        for T in female_word_types:
            t = female_word_types[T]
            percentage = t[1]
            if T in self.__HIGH_POLITICS:
                high_female += percentage
            elif T in self.__LOW_POLITICS:
                low_female += percentage
            else:
                pass

        print(f"Male\nHigh:{high_male}, Low:{low_male}")
        print(f"Female\nHigh:{high_female}, Low:{low_female}")

    def get_confdesc_by_nth(self, nth: int):
        """
        Internal Use Only
        """

        if nth not in (17, 18, 19, 20):
            raise AttributeError("Invalid arg: NTH")
        filename: str = PICKLE_BIN_CONF_DESC_BY_NTH.replace("{NTH}", nth.__str__())
        log(f"Reading '{filename}'")
        with open(filename, "rb") as pickle_bin:
            confdesc_objs = pickle.load(pickle_bin)
        log("", prefix="")
        log(f"{type(confdesc_objs) = }")
        log("", prefix="")
        log(f"{type(confdesc_objs[0]) = }), {len(confdesc_objs) = }")
        log("", prefix="")
        log(f"{confdesc_objs[0] = }")
        log("", prefix="")
        log(f"{dir(confdesc_objs[0]) = }")

    def __withlabels(self, year: int, top: int) -> tuple[dict]:
        """
        This command will display the word frequency along with the corresponding categories for each word.
        """
        word_freq = get_word_freq(
            year=year, top=top, min_male=0, min_female=0, greater_than=0
        )
        freq_male = word_freq[0]
        freq_female = word_freq[1]

        for key in freq_male:
            _word = Word(key)
            freq_male[key] = {
                "count": freq_male[key],
                "classification": [
                    k for k in _word.__dict__ if _word.__dict__[k] is True
                ],
            }
        for key in freq_female:
            _word = Word(key)
            freq_female[key] = {
                "count": freq_female[key],
                "classification": [
                    k for k in _word.__dict__ if _word.__dict__[k] is True
                ],
            }
        return (freq_male, freq_female)


if __name__ == "__main__":
    # print(f"{len(DATA_FILES)} data files (by YEAR) found")
    # DATAFILE_BY_NTH_COUNT: int = 0
    # for file in os.listdir():
    #     if file.startswith("NthAsmDescription") and file.endswith("pickle"):
    #         DATAFILE_BY_NTH_COUNT += 1
    # print(f"{DATAFILE_BY_NTH_COUNT} data files (by NTH) found")
    """
    plot_word_freq(year=2006, top=20)
    # Instead of using something like this to get a word's position:
    # word_freq_look_up(get_word_freq(year=2013, top=20), key="제도")
    # Use this:
    # word_freq_look_up((get_word_freq, {"year": 2013, "top": 20}, key=""제도)
    pp(word_freq_look_up((get_word_freq, {"year": 2013, "top": 20}), key="제도"))
    """
    freqs = Main.merge_all_by_nth_freq_files()
    log(
        f"{'Done initializing' if len(freqs) != 0 else type(freqs) + ' ' + 'len=' + str(len(freqs))}"
    )
    # pp(freqs[0])
    # input("\n")
    pp(get_word_freq_by_tuple(obj=freqs[0], top=20))
    log("Filtering using built-in STOPWORDS")
    freqs = list(map(filter_tuple_using_builtin_stopwords, freqs))
    pp(get_word_freq_by_tuple(obj=freqs[0], top=20))
    if True:  # hey this is just a switch so be quiet
        for index, t in enumerate(freqs):
            NTH = index + 18
            filename = f"{NTH}th_TupleOfTwoDicts_akaWordFreqComplete.pickle"
            if filename not in os.listdir():
                log(f"{filename} not found, now creating.")
                with open(filename, "wb") as o:
                    log(f"Writing to {filename}")
                    pickle.dump(t, o)
                    log(f"Done writing to {filename}")
    fire.Fire(Main)
