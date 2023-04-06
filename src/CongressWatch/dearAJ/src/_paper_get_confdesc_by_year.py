#!/usr/bin/env python3

from dearaj import *
from tqdm import tqdm
import pickle
from os import get_terminal_size
import re
import time
import datetime


def get_conf_desc_of_year(year: int, log_file_path: str = ""):
    if log_file_path == "":
        log_file_path = f"./DEBUG_{year}_{__file__.split('/')[-1]}.log"

    console.log(f"Log file: {log_file_path}", prefix="log")
    t_start = time.time()

    width = get_terminal_size()[0]
    if year < 1996 or year > 2021:
        raise IndexError(f"invalid argument `year`: {year}")

    p_start = f"{year}-01-01"
    p_end = f"{year}-12-31"

    result: list[ConfDescription] = []

    for index, conf in enumerate((p := period(p_start, p_end))):
        if conf.has(FemaleMP):
            description = conf.describe()
            _simple_debug = re.compile(r"[0-9]+(?= female MP spoke)").search(
                repr(description)
            )
            if not _simple_debug:
                raise RuntimeError("Debug failed")
            else:
                number = int(_simple_debug.group())
                console.faded(f"simple_debug: {number}")
                if number == 0:
                    _now = datetime.datetime.now()
                    console.warn(repr(conf))
                    console.warn(
                        f"ajPDF algorithm says it has ZERO female MP:\n\t{repr(conf)}\n\t{repr(description)}\n\t{conf._anji_usb_pdf_file_name}",
                        prefix="...",
                    )
                    # Writing info to log file
                    with open(log_file_path, "a+") as log_file:
                        console.log(
                            "Writing debug informations to log file...", prefix="dbg"
                        )
                        log_file.write("---\n")
                        log_file.write(_now.strftime("%Y-%m-%d %H:%M:%S") + "\n")
                        from io import StringIO
                        from contextlib import redirect_stdout

                        f = StringIO()
                        with redirect_stdout(f):
                            exec("conf.has(FemaleMP)")
                        method_confhas_output = f.getvalue()
                        aft = method_confhas_output.index(" (")
                        that_possible_female_name = method_confhas_output[
                            0:aft
                        ].replace("has: found name ", "")
                        console.log(f"{that_possible_female_name} has been recorded")

                        log_file.write(
                            f"[Skipped] Simple string check found a possible female MP name '{that_possible_female_name}', but `conf.describe` confirms no female MP speaker was there:\n\n"
                        )
                        log_file.write(f"{conf._anji_usb_pdf_file_name}\n\n\n")
                else:
                    result.append(description)
                    console.log(f"{len(result) = }", prefix="res")

            console.log(f"[{index}/{len(p)}] conferences, {year}", prefix="idx")
            console.faded(repr(description))
            t_end = time.time()
            t_spent = str(t_end - t_start)
            console.faded(f"{t_spent.center(width, '-')}")
        else:
            print(f"index {index} of {len(p)} conferences", end="\r")

    with open(f"./Description_{year}.pickle", "wb") as out_put:
        pickle.dump(result, out_put)


if __name__ == "__main__":
    console = ajconsole.Message(True)
    from sys import argv

    if len(argv) != 2:
        raise ValueError("Should be exactlly 1 arg")
    year: int = int(argv[1])
    console.log(f"Now getting year {year}'s conf descriptions...\n", prefix="get")
    get_conf_desc_of_year(year)
