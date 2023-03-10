import os
import sys


if len(sys.argv) < 2:
    print("Need to specify PDF Path")
    os._exit(-1)

PDFPATH = sys.argv[1]

for pdf in os.listdir(PDFPATH):
    os.system(f"./app.py {PDFPATH}/{pdf}")
    ipt = input("\nContinue? ")
    if ipt.lower() not in ["n", "no"]:
        continue
    else:
        print("Bye")
        os._exit(0)
