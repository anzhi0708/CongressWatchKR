#!/usr/bin/env python3

from dearaj import *
from tqdm import tqdm
import time
import click


SAVE_TO = "/Volumes/AJ/yeongnok-pdfs/"


@click.command()
@click.option("--delta", default=0.7, help="Time sep (seconds), default==0.7")
@click.argument("year")
def crawl(year: int, delta: float):
    time_start = time.time()
    save_to_path = f"{SAVE_TO}{year}/"
    for conf in period(f"{year}-01-01", f"{year}-12-31"):
        filename = f"{conf.date}_{conf.ct1}.{conf.ct2}.{conf.ct3}.{conf.mc}.pdf"
        fullpath = save_to_path + filename
        click.echo(f"\t\033[1;36msaving:\033[0m\t{fullpath}\r", nl=False)
        with open(fullpath, "wb") as output:
            output.write(conf.pdf)
            click.echo(f"\t\033[1;32msaved: \033[0;2m\t{fullpath}\033[0m")
            time.sleep(delta)
    time_end = time.time()
    click.echo(f"\nTime spent: {(time_end - time_start) / 60} minutes")


if __name__ == "__main__":
    crawl()
