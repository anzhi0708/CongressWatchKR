#!/usr/bin/env python3

import fire
import os
from ajconsole import Message
from sys import argv


class Test:
    def __init__(self):
        self.__console = Message(enabled=True)

    def iter(self, dir=f"/Volumes/AJ/yeongnok-pdfs/{argv[2]}"):
        for file in os.listdir(dir):
            os.system(f"./ajpdf.py {dir}/{file}")
            input("Continue? ")

    def serialize_all(self, dir="/Volumes/AJ/yeongnok-pdfs", start=2006, end=2022):
        for year in range(start, end):
            full_dir = f"{dir}/{year}"
            for file in os.listdir(full_dir):
                os.system(f"./ajpdf.py {full_dir}/{file}")
            self.__console.log(f"{year} Done")
            with os.popen(f"du -ah ./serialized/{year}", "w") as output:
                self.__console.log(f"{output.read()=}")


if __name__ == "__main__":
    fire.Fire(Test)
