#!/usr/bin/env python3


import os
import sys
import time
import signal
import termios
import logging
import subprocess
import multiprocessing
from multiprocessing import Process

"""
Only tested on unix machines.

This module aims to iterate through all PDF files
to find missing data (job titles)
"""

logging.basicConfig(level=logging.WARNING)

OLD_SETTINGS = termios.tcgetattr(sys.stdin)


def kill_all_processes():
    """
    Terminate all child processes
    """
    os.killpg(os.getpgid(0), signal.SIGTERM)


def process_pdf(path_to_file: str):
    subprocess.run(["./app.py", f"{path_to_file}", "1>", "/dev/null"])


if len(sys.argv) < 2:
    print("Need to specify PDF Path")
    os._exit(-1)

PDF_PATH: str = sys.argv[1]
PDF_FILES: list[str] = [file for file in os.listdir(PDF_PATH) if file.endswith("pdf")]
TOTAL: int = len(PDF_FILES)
N_DONE: int = 0
BATCH_SIZE: int = 4


if __name__ == "__main__":
    signal.signal(signal.SIGINT, kill_all_processes)
    batches = [PDF_FILES[i : i + BATCH_SIZE] for i in range(0, TOTAL, BATCH_SIZE)]
    for a_batch in batches:
        once: list[Process] = []
        for a_file in a_batch:
            full_path_of_this_pdf_file: str = f"{PDF_PATH}/{a_file}"
            p = Process(target=process_pdf, args=(full_path_of_this_pdf_file,))
            once.append(p)

        for a_process in once:
            a_process.start()
            print(a_process, file=sys.stderr)  # Print to stderr cuz `1> /dev/null`

        print("", file=sys.stderr)

        time.sleep(3)
        for a_process in once:
            a_process.terminate()
            a_process.join()
            print(a_process, file=sys.stderr)

        print("", file=sys.stderr)
        once.clear()

