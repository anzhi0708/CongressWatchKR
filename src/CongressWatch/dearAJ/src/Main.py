#!/usr/bin/env python3
# coding: utf-8


from os import popen, listdir
from queue import Empty
from collections import defaultdict
from tqdm import tqdm
from pprint import pp
from multiprocessing import Queue, Process
from unicodedata import normalize
import matplotlib.pyplot as plt
from dearaj import *
import time  # For debugging.
from ajconsole import Message  # For debugging.


console = Message(True)

ALL_FEMALE_MP_EVER: list["FemaleMP"] = core.get_all_female_mp()

Q: Queue = Queue()

ANALYZER = "/Users/aj/Public/py/dearAJ/src/ajFemaleMPAnalyzer.py"


def analyze(year: int, queue: Queue):
    DIRECTORY = f"{year}_json"
    result = defaultdict(
        int
    )  # Initializing dictionary, return it at the end of function.

    for json_record in tqdm(listdir(DIRECTORY), desc=str(year)):
        target = f"{DIRECTORY}/{json_record}"
        with popen(f"python3 {ANALYZER} --file={target} describe", "r") as output:
            lines = output.read().strip().splitlines()
            for line in lines:
                try:
                    line = line.split(":")
                    name = normalize("NFKC", line[0].strip())
                    count = int(line[1].strip())
                    result[name] += count
                except IndexError as e:
                    console.warn(
                        f'Seems like no female MP spoke (file: {target}, cause "{e}")',
                        prefix=str(year),
                    )
                    continue

    console.log(f"Putting result to Q", prefix=str(year))
    queue.put({year: result})
    console.log(f"Completed", prefix=str(year))


def main(queue: Queue, n: int):
    """Analyze each result from the queue."""
    for i in range(n):
        console.log(f"Looping {i+1} / {n}, getting result from queue", prefix="Main")
        try:
            result: dict[int, dict[str, int]] = queue.get(timeout=7)
        except Empty:
            print("Queue is now empty")
            exit(0)
        assert len(result.keys()) == 1

        YEAR: int = list(result.keys())[0]
        console.log(f"Got year {YEAR} from queue.")

        plt.rcParams["font.family"] = ["NanumGothic"]
        plt.figure(figsize=(48, 8))

        GENERATIONS: list[int] = core.get_gen_by_year(YEAR)
        names = []
        for gen in GENERATIONS:
            ladies: list[MP] = Assembly(gen).females
            for lady in ladies:
                hangul_name = normalize("NFKC", lady.name)
                if hangul_name not in names:
                    names.append(hangul_name)
                    console.log(
                        f'Name "{hangul_name}" added', prefix=str(YEAR) + f" hg"
                    )
                for lady in ALL_FEMALE_MP_EVER:
                    if normalize("NFKC", lady.hg_nm) == hangul_name:
                        hanja_name = normalize("NFKC", lady.hj_nm)
                        if hanja_name not in names:
                            names.append(hanja_name)
                            console.log(
                                f'Name "{hanja_name}" added', prefix=str(YEAR) + f" HJ"
                            )


if __name__ == "__main__":
    worker2016 = Process(target=analyze, args=(2016, Q))
    worker2017 = Process(target=analyze, args=(2017, Q))
    worker2018 = Process(target=analyze, args=(2018, Q))
    worker2019 = Process(target=analyze, args=(2019, Q))
    worker2020 = Process(target=analyze, args=(2020, Q))
    worker2021 = Process(target=analyze, args=(2021, Q))

    worker2016.start()
    console.log("Starting year 2016", prefix="Process")
    worker2017.start()
    console.log("Starting year 2017", prefix="Process")
    worker2018.start()
    console.log("Starting year 2018", prefix="Process")
    worker2019.start()
    console.log("Starting year 2019", prefix="Process")
    worker2020.start()
    console.log("Starting year 2020", prefix="Process")
    worker2021.start()
    console.log("Starting year 2021", prefix="Process")

    worker2016.join()
    worker2017.join()
    worker2018.join()
    worker2019.join()
    worker2020.join()
    worker2021.join()

    main(Q, 6)
