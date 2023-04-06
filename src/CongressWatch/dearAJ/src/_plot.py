from dearaj import *
import sys
import os
from tqdm import tqdm
from collections import defaultdict, namedtuple
import pickle
from pprint import pp
import matplotlib.pyplot as plt


def get_confdesc_by_year(year: int):
    """Load data from disk"""
    full_file_path = f"Description_{year}.pickle"
    with open(full_file_path, "rb") as f:
        ls_confdesc: list = pickle.load(f)

    ls_confdesc.sort()
    return ls_confdesc


# Need to get stats info by `comm_name` and `year`


def get_speech_percentage_by_year(year: int) -> float:
    """
    Getting `speech percentage`
    """
    char_count_total = 0
    female_char_count = 0
    for desc in (ls_confdesc := get_confdesc_by_year(year)):
        char_count_total += desc.n_total_mp_speech_char_count
        female_char_count += desc.n_total_female_mp_speech_char_count
    return female_char_count / char_count_total


def get_speech_percentage_by_year_and_comm_name(year: int, comm_name: str) -> float:
    """
    Getting `speech percentage` by `year` and `comm_name`
    """
    char_count_total = 0
    female_char_count = 0
    all_possible_comm_names = []
    for desc in (ls_confdesc := get_confdesc_by_year(year)):
        if desc.comm_name not in all_possible_comm_names:
            all_possible_comm_names.append(desc.comm_name)
        if desc.comm_name == comm_name:
            char_count_total += desc.n_total_mp_speech_char_count
            female_char_count += desc.n_total_female_mp_speech_char_count
        if comm_name == '여가위':
            if desc.comm_name == '여성위':
                char_count_total += desc.n_total_mp_speech_char_count
                female_char_count += desc.n_total_female_mp_speech_char_count
    if not char_count_total:
        raise ValueError(f"Error when getting {comm_name}\nAll possible comm names: {all_possible_comm_names}")
    return female_char_count / char_count_total
    pass


def _plot_bar_percentage(x_dim, y_dim, title, block=True):
    plt.figure(figsize=(48, 8))
    plt.rcParams["font.family"] = ["NanumGothic"]
    plt.title(title)
    plt.xticks(x_dim)
    _bar = plt.bar(x_dim, y_dim)
    _y_as_ticklabel = [f"{y:.2%}" for y in y_dim]
    plt.bar_label(_bar, label_type="edge", labels=_y_as_ticklabel)
    for idx, xtick_label in enumerate((xtick_labels := plt.gca().get_xticklabels())):
        if len(get_gen_by_year(int(xtick_label._text))) > 1:
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


# Plotting graph from 2006 to 2021
def plot_by_comm_name(comm_name: str = "", mode="speech_percentage"):
    if comm_name == "":
        raise ValueError("`comm_name` is empty")
    if mode == "speech_percentage":
        y_dim = []
        for year in (x_dim := range(2006, 2022)):
            y_dim.append(get_speech_percentage_by_year_and_comm_name(year, comm_name))
    _title = f"{comm_name} 회의중 여성의원 발언 비율 변화"
    _plot_bar_percentage(x_dim, y_dim, _title)

def get_word_frequency_by_year(year: int):
    # Guard
    to_confirm: list[str] = []
    for file in os.listdir("."):
        if str(year) in file:
            to_confirm.append(file)

    if len(to_confirm) != 0:
        print(f"\nFor year `{year}`, these files were found in current directory:\n")
        for file in to_confirm:
            print(f"\t- {file}")

        print("\nContinue? [y/N] ")
        user_input: str = input()

        if user_input.lower() not in ("yes", "y"):
            print("Canceled.")
            sys.exit(0)
    else:
        print(f"{year.center(10, '-')}")



    result_male: dict = {}
    result_female: dict = {}
    for confdesc in tqdm(get_confdesc_by_year(year), desc="Getting conf description", leave=True):
        freq_male, freq_female = confdesc.conf.get_ordered_word_frequency_of_both_gender()
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
    with open(f"_test_abc_{year}.pickle", "wb") as target:
        pickle.dump((result_male, result_female), target)
    print(f"DONE FOR {year}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        plot_by_comm_name(sys.argv[-1])
    else:
        plot_by_comm_name("환노위")
