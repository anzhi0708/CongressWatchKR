from dearAJ import *
import sys
import os
from tqdm import tqdm
from collections import defaultdict, namedtuple
import pickle
from pprint import pp
import matplotlib.pyplot as plt


def get_confdesc_by_nth(nth: int):
    """Load data from disk"""
    full_file_path = f"NthAsmDescription_{nth}.pickle"
    with open(full_file_path, "rb") as f:
        ls_confdesc: list = pickle.load(f)

    ls_confdesc.sort()
    return ls_confdesc


# Need to get stats info by `comm_name` and `nth`


def get_speech_percentage_by_nth(nth: int) -> float:
    """
    Getting `speech percentage`
    """
    char_count_total = 0
    female_char_count = 0
    for desc in (ls_confdesc := get_confdesc_by_nth(nth)):
        char_count_total += desc.n_total_mp_speech_char_count
        female_char_count += desc.n_total_female_mp_speech_char_count
    return female_char_count / char_count_total


def get_speech_percentage_by_nth_and_comm_name(nth: int, comm_name: str) -> float:
    """
    Getting `speech percentage` by `nth` and `comm_name`
    """
    char_count_total = 0
    female_char_count = 0
    for desc in (ls_confdesc := get_confdesc_by_nth(nth)):
        if desc.comm_name == comm_name:
            char_count_total += desc.n_total_mp_speech_char_count
            female_char_count += desc.n_total_female_mp_speech_char_count
    return female_char_count / char_count_total


def _plot_bar_percentage(x_dim, y_dim, title, block=True):
    plt.figure(figsize=(48, 8))
    plt.rcParams["font.family"] = ["NanumGothic"]
    plt.title(title)
    plt.xticks(x_dim)
    _bar = plt.bar(x_dim, y_dim)
    _y_as_ticklabel = [f"{y:.2%}" for y in y_dim]
    plt.bar_label(_bar, label_type="edge", labels=_y_as_ticklabel)
    for idx, xtick_label in enumerate((xtick_labels := plt.gca().get_xticklabels())):
        #if len(get_gen_by_year(int(xtick_label._text))) > 1:
        target = xtick_labels[idx]
        plt.text(
            target.get_position()[0] + 0.3,
            target.get_position()[1] - 0.002,
            "*",
            va="center",
            ha="center",
        )
        # target.set_color("red")

    plt.show(block=block)


# Plotting graph from 17th to 21st
def plot_by_comm_name(comm_name: str = "", mode="speech_percentage"):
    if comm_name == "":
        raise ValueError("`comm_name` is empty")
    if mode == "speech_percentage":
        y_dim = []
        for nth in (x_dim := range(17, 21)):
            y_dim.append(get_speech_percentage_by_nth_and_comm_name(nth, comm_name))
    _title = f"{comm_name} 회의중 여성의원 발언 비율 변화 ({nth})"
    _plot_bar_percentage(x_dim, y_dim, _title)


def get_word_frequency_by_nth(nth: int):
    # Guard
    to_confirm: list[str] = []
    for file in os.listdir("."):
        if str(nth) in file:
            to_confirm.append(file)

    if len(to_confirm) != 0:
        print(f"\nFor NTH `{nth}`, these files were found in current directory:\n")
        for file in to_confirm:
            print(f"\t- {file}")

        print("\nContinue? [y/N] ")
        user_input: str = input()

        if user_input.lower() not in ("yes", "y"):
            print("Canceled.")
            sys.exit(0)
    else:
        print(f"{nth.center(10, '-')}")

    result_male: dict = {}
    result_female: dict = {}
    for confdesc in tqdm(
        get_confdesc_by_nth(nth), desc="nthAsmConfDesc", leave=True
    ):
        (
            freq_male,
            freq_female,
        ) = confdesc.conf.get_ordered_word_frequency_of_both_gender()
        for word in freq_male:
            if word in result_male.keys():
                result_male[word] += freq_male[word]
            else:
                result_male[word] = freq_male[word]
        for word in freq_female:
            if word in result_female.keys():
                result_female[word] += freq_female[word]
            else:
                result_female[word] = freq_female[word]
    with open(f"WordFreqByNth{nth}.pickle", "wb") as target:
        pickle.dump((result_male, result_female), target)
    print(f"DONE FOR {nth}")


if __name__ == "__main__":
    # plot_by_comm_name("국방위")
    from sys import argv

    nth = int(argv[1])
    get_word_frequency_by_nth(nth)
