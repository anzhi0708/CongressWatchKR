#!/usr/bin/env python3

import fitz
import re
import sys
from os import _exit
from ajconsole import Message
from dearaj import *

LOGGING = False
console = Message(enabled=LOGGING)


def main():
    console.log(fitz.__doc__)
    console.log("")
    if len(sys.argv) < 2:
        console.error("Please specify path to PDF file correctly")
        raise RuntimeError("Please specify path to PDF file correctly")
    FILE = sys.argv[1]

    try:
        DOC = fitz.open(FILE)  # type: fitz.Document
        console.log("Found: " + FILE)
        INDEX_MAX = len(DOC) - 1
    except Exception as e:
        console.error("File not found!")
        raise e
        _exit(233)

    pdf_text = PDFText(DOC)
    pdf_text.get_stats()
    pdf_text.write_json_to_stdout()
    return pdf_text.result


if __name__ == "__main__":
    main()
