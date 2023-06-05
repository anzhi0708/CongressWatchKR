from dearAJ import Assembly
import csv
import fire


FILENAME_PAT = "top20_{NTH}th_TupleOfTwoDicts_akaWordFreq_{GENDER}.csv"

def total_mps_count(nth: int) -> int:
    return Assembly(nth).total

def female_percentage_nth(nth: int) -> float:
    return Assembly(nth).female / total_mps_count(nth)

def top20_total_count_by_nth_and_gender(nth: int, gender: str) -> int:
    filename = FILENAME_PAT.replace("{NTH}", str(nth)).replace("{GENDER}", gender)
    with open(filename, 'r') as csvfile:
        total: int = 0
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            total += int(row[1])
    return total

def average_count_by_nth_and_gender(nth: int, gender: str) -> float:
    total = top20_total_count_by_nth_and_gender(nth, gender)
    n_mp: int = 0
    if gender == "female":
        n_mp += Assembly(nth).female
    elif gender == "male":
        n_mp += Assembly(nth).male
    else:
        raise RuntimeError("?")
    return total / n_mp

def main(nth: int, gender: str):
    print(f"{nth}th, {gender=} - {average_count_by_nth_and_gender(nth, gender)}")

if __name__ == "__main__":
    fire.Fire(main)
