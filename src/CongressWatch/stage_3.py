"""

"The concluding stage of the paper"

In some Linux distributions, such as Gentoo, there are explicit concepts of 'Stage1', 'Stage2', and 'Stage3'. These stages are used to describe the process from the basic boot environment (Stage 1) to a fully functional system environment (Stage 3).

Here, I borrow the term 'Stage 3' to denote that this script file was created during the concluding stage of my thesis.

This script file will serve as the 'script file' for refining the thesis, implementing some simple functions that serve this purpose.

"""


import dearAJ as aj
import os
import sys
from collections import defaultdict
import csv
import fire
import pickle
from pprint import pp


log = aj.ajconsole.Message(enabled=True).log
period_pickle_filename_pattern: str = "PeriodObj_{nth}thAssemb.pickle"
confdesc_by_year_filename_pat: str = '_test_abc_{YEAR}.pickle'


def dump_conf_obj_to_pickle_binary_by_nth(nth: int):
    print(aj.GEN_PERIOD_DICT[nth])
    log("Preparing data for dumping to pickle file...")
    asm_start, asm_end = aj.GEN_PERIOD_DICT[nth]
    conf_objs: aj.period = aj.period(asm_start, asm_end)
    output_filename: str = f"PeriodObj_{nth}thAssemb.pickle"
    log(f"Writing {nth}th asm to disk (pickle file)")
    with open(output_filename, "wb") as output:
        pickle.dump(conf_objs, output)
    log(f"Created {nth}th asm pickle file")


def sort_dict(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda t: t[1], reverse=True))


def dict_to_csv(
    d: dict, *, output_file_name: str = "", header_row: list[str] | None = None
) -> None:
    if output_file_name == "":
        raise RuntimeError("Invalid output file name")
    if header_row is None:
        raise RuntimeError("Header Row missing")
    with open(output_file_name, "w") as output:
        writer = csv.writer(output)
        writer.writerow(header_row)
        for key in d.keys():
            writer.writerow([key, d[key]])
    import inspect

    fn_name: str = inspect.currentframe().f_code.co_name
    print(f"{fn_name} Done")


def load_csv_data_files() -> list[str]:
    csv_files: list[str] = []

    for file in os.listdir("."):
        if (
            file.endswith(".csv")
            and file.startswith("wordfreq_output")
            and ("top20" in file)
        ):
            csv_files.append(file)
    return csv_files


def merge_analyze_print_statistics(
    csv_files: list[str] = load_csv_data_files(),
) -> tuple[defaultdict, defaultdict]:
    result_male: defaultdict = defaultdict(int)
    result_female: defaultdict = defaultdict(int)
    for csv_file in csv_files:
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                male_word, male_freq_str = row[1].split(" ")
                female_word, female_freq_str = row[2].split(" ")
                result_male[male_word] += int(male_freq_str)
                result_female[female_word] += int(female_freq_str)

    pp(result_male := sort_dict(result_male))
    print()
    pp(result_female := sort_dict(result_female))

    should_save: bool = False
    if input("Save to csv?").lower() in ("y", "yes", "ye"):
        should_save = True
    if should_save:
        output_name: str = input("Save to: ")
        if not output_name.endswith(".csv"):
            raise RuntimeError("Invalid suffix")
        header_row: list[str] = input("Header row: ").split(",")
        dict_to_csv(
            result_male,
            output_file_name=output_name.replace(".csv", "_male.csv"),
            header_row=header_row,
        )
        dict_to_csv(
            result_female,
            output_file_name=output_name.replace(".csv", "_female.csv"),
            header_row=header_row,
        )
    return result_male, result_female


def _write_csv_for_getting_freq_by_nth_asm(nth: int):
    """
    Internal Use Only

    Following the professor's suggested revision that 'it might be more beneficial to analyze based on the terms of the parliament rather than by year,' I incorporated the corresponding functionality into CongressWatch via this script file.
    """
    log("Reading data...")
    start_18th: str = aj.GEN_PERIOD_DICT[18][0]
    end_18th: str = aj.GEN_PERIOD_DICT[18][1]

    start_19th: str = aj.GEN_PERIOD_DICT[19][0]
    end_19th: str = aj.GEN_PERIOD_DICT[19][1]

    start_20th: str = aj.GEN_PERIOD_DICT[20][0]
    end_20th: str = aj.GEN_PERIOD_DICT[20][1]

    all_confs_18th: aj.period = aj.period(start_18th, end_18th)
    all_confs_19th: aj.period = aj.period(start_19th, end_19th)
    all_confs_20th: aj.period = aj.period(start_20th, end_20th)

    log("Done reading data.")
    import pickle

    for obj_index, conf_obj in enumerate(
        (all_confs_18th, all_confs_19th, all_confs_20th)
    ):
        conf_nth: int = obj_index + 18
        filename_for_output: str = f"all_confs_{conf_nth}th.pickle"
        with open(filename_for_output, "wb") as output:
            log("Dumping Conf Object to pickle binary")
            pickle.dump(conf_obj, output)
            log(f"Done dumping {conf_nth}th")

    pass


class Main:
    def merge_analyze_print_statistics(
        self,
        csv_files: list[str] = load_csv_data_files(),
    ) -> tuple[defaultdict, defaultdict]:
        merge_analyze_print_statistics(csv_files)

    def freq_by_nth_asm(self, nth: int):
        import STOPWORDS  # STOPWORDS.SKIP

        conferences = self.load_pickle_by_nth(nth)

        """
        for conf in conferences:
            print(dir(conf))
            pp(conf.get_ordered_word_frequency_of_both_gender())
            break
        """

        """Filtering"""
        male_dict: defaultdict = defaultdict(int)
        female_dict: defaultdict = defaultdict(int)

        i = 0

        for conf in conferences:
            i += 1
            male_this_conf, female_this_conf = conf.get_word_frequency_of_both_gender()
            for k, v in male_this_conf.items():
                male_dict[k] += v
            for k, v in female_this_conf.items():
                female_this_conf[k] += v

            if i == 5:
                pp(male_this_conf)
                sys.exit(0)

    def load_pickle_by_nth(self, nth: int):
        filename: str = period_pickle_filename_pattern.replace("{nth}", str(nth))
        file_size = os.path.getsize(filename)
        log(f"Reading {filename} (size: {file_size})")
        with open(filename, "rb") as pickle_binary:
            result = pickle.load(pickle_binary)
            print(type(result))
        log(f"Done reading {filename}")
        return result

    def load_pickle_by_year(self, year: int):
        filename: str = confdesc_by_year_filename_pat.replace("{YEAR}", str(year))
        file_size = os.path.getsize(filename)
        log(f"Reading {filename} (size: {file_size})")
        with open(filename, "rb") as pickle_binary:
            result = pickle.load(pickle_binary)
            print(type(result))
        log(f"Done reading {filename}")
        return result

    def stage_3(self, year: int = -1):
        """
        教授说需要‘届数别’的数据分析。之前得到的数据都是
        以“年”为单位，因此在某些时间跨度上，某一年的数据
        是同时包含了两届国会发言的数据的。
        - 找出这些重叠的时间段。
        - 将重叠的时间段（年份）按照：1月1日～当时的某届
        的结束日期
        - 以及：结束日期-12月31日。
          如此一来，一个重叠了两届议会的年份就被分成了两
          个部分。将这两个部分合并到它们归属的议会数据中
          即可。
        那么，
        要如何做呢？
        已知ConfDesc的pickle数据（已有的_test_abc*文件）
        是以年份为单位划分的。
        那么：
            - 找出重叠的年份
            - 。。。
        Anyway 先做第一步。

        这个method显然是会被包装为CLI命令的。
        那么它需要达成什么功能？- 必然是：根据届数输出
        词频统计信息、单独的委员会发言情况统计。
        首先先做词频的功能。
        """

        DATA_FILES: list[str] = []
        for file in os.listdir("./dearAJ/src"):
            if file.startswith("_test_abc_") and \
            file.endswith("pickle"):
                DATA_FILES.append(f"./dearAJ/src/{file}")
        ALL_DUP_YEARS: list[str] = []
        for gen in (d:=aj.GEN_PERIOD_DICT):
            year_start = d[gen][0]
            year_end = d[gen][1]
            if year_start not in ALL_DUP_YEARS:
                ALL_DUP_YEARS.append(year_start)
            if year_end not in ALL_DUP_YEARS:
                ALL_DUP_YEARS.append(year_end)
        log(f"{ALL_DUP_YEARS=}")
        YEARS: list[str] = list(filter(lambda n: 2004 <= int(n[:4]) <= 2021,
                                       ALL_DUP_YEARS))
        YEARS.sort()
        log(f"{YEARS=}")
        # YEARS=['2004-05-29', '2004-05-30', '2008-05-29', '2008-05-30', '2012-05-29', '2012-05-30', '2016-05-29', '2016-05-30', '2020-05-29', '2020-05-30']

        """
        现在我需要把这些年的pickle文件单独分析。
        这些年份里，每个年份都是包含了前一届国会的结束日期
        和下一届国会的就任日期。
        """
        if year == -1:
            for index, x in enumerate(YEARS):
                THE_YEAR = x[:4]
                if index % 2 == 1:
                    period_obj = aj.period(x, f"{THE_YEAR}-12-31")
                    output_filename = f"ConfDesc{THE_YEAR}_aft_{x}toLastDay.pickle"
                else:
                    period_obj = aj.period(f"{THE_YEAR}-01-01", x)
                    output_filename = f"ConfDesc{THE_YEAR}_pre_Jan1To{x}.pickle"
                list_of_confdesc_objs = []
                log(f"Output file name will be:\n\t{output_filename}")
                for conf in period_obj:
                    confdesc_obj = conf.describe()
                    list_of_confdesc_objs.append(confdesc_obj)
                with open(output_filename, 'wb') as output:
                    log("Dumping")
                    pickle.dump(list_of_confdesc_objs, output)
                    log("Done dumping")
        
        else:
            # Check if year is valid
            # Im gonna hard code this stuff
            if not year in (2008, 2012, 2016, 2020):
                raise RuntimeError("Invalid year")
            log(f"{year=}")
            match year:
                case 2008:
                    P_Pre = aj.period("2008-01-01", YEARS[2])
                    P_Aft = aj.period(YEARS[3], "2008-12-31")
                case 2012:
                    P_Pre = aj.period("2012-01-01", YEARS[4])
                    P_Aft = aj.period(YEARS[5], "2012-12-31")
                case 2016:
                    P_Pre = aj.period("2016-01-01", YEARS[6])
                    P_Aft = aj.period(YEARS[7], "2016-12-31")
                case 2020:
                    P_Pre = aj.period("2020-01-01", YEARS[8])
                    P_Aft = aj.period(YEARS[9], "2020-12-31")
            output_filename_pre = f"ConfDesc{year}_pre_Jan1ToMiddle.pickle"

            output_filename_aft = f"ConfDesc{year}_aft_MiddleToLastDayOfYear.pickle"
            ls_pre = []
            ls_aft = []
            for conf in P_Pre:
                ls_pre.append(conf.describe())
            with open(output_filename_pre, 'wb') as output:
                log(f"[pre] Writing for year {year}")
                pickle.dump(ls_pre, output)
            log(f"{year=} [pre] Now cleaning up")
            ls_pre = []

            for conf in P_Aft:
                ls_aft.append(conf.describe())
            with open(output_filename_aft, 'wb') as output:
                log(f"[aft] Writing for year {year}")
                pickle.dump(ls_aft, output)
            log(f"{year=} [aft] Now cleaning up")
            ls_aft = []


        

    def dump_pickle_file_by_nth(self, nth: int) -> None:
        """
        Internal use only
        ** 17th - 21st asm data is already here! **
        """
        dump_conf_obj_to_pickle_binary_by_nth(nth)


if __name__ == "__main__":
    fire.Fire(Main)
