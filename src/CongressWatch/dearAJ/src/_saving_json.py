#!/usr/bin/env python3

from dearaj import *
from multiprocessing import Process, Queue
import os
import time
from queue import Empty


queue = Queue(1000)


ANALYZER = "/Users/aj/Public/py/dearAJ/src/_to_json_string.py"

PDF_PATH = "/Volumes/AJ/yeongnok-pdfs/"
JSON_PATH = "/Users/aj/Public/py/dearAJ/src/"


def get_by_year(q, year: int):
    for conf in period(f"{year}-01-01", f"{year}-12-31"):
        gen_ls: list = get_gen_by_year(year)
        for gen in gen_ls:
            for lady in Assembly(gen).females:
                if conf.has(lady):
                    q.put(conf)


def save_json(q, year: int):
    pdfpath = f"{PDF_PATH}{year}/"
    json_path = f"{JSON_PATH}{year}_json/"
    files = []
    while True:
        try:
            conf = q.get(timeout=3)
        except Empty:
            print("\tQueue is now empty.\n")
            break
        filename = (
            pdfpath + f"{conf.date}_{conf.ct1}.{conf.ct2}.{conf.ct3}.{conf.mc}.pdf"
        )
        if filename not in files:
            print(f"\t\033[1;36mSaving\033[0m {filename}\r", end="")
            files.append(filename)
            os.system(
                f"python3 {ANALYZER} {filename} >> {json_path}{(conf.local_csv_file_name).replace('(', '__').replace(')', '')}.json"
            )
            print(f"\t \033[1;32mSaved\033[0m {filename}")
        else:
            pass


if __name__ == "__main__":
    from sys import argv

    YEAR = int(argv[1])
    job = Process(target=get_by_year, args=(queue, YEAR))
    job.start()
    save_json(queue, YEAR)
    job.join()
