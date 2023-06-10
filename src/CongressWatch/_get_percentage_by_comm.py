import dearAJ as aj
import fire
from pprint import pp
import re
from stage_3 import Main
from dataclasses import dataclass
from collections import defaultdict
from typing import Self
from os import get_terminal_size
from tqdm import tqdm


"""
This module is used to calculate the proportion of 
female speeches in the statements of various committees 
according to the NTH parameter, written on June 8th.

这个模块用于按照NTH参数
统计各委员会发言中的女性发言比例
写于6月8日
"""

DATA_FILES: list[str, str, str] = [
    "NthAsmDescription_18.pickle",
    "NthAsmDescription_19.pickle",
    "NthAsmDescription_20.pickle",
]


def get_conf_descriptions_nth(nth: int) -> list[aj.ConfDescription]:
    filename: str = re.sub(r"[0-9][0-9]", str(nth), DATA_FILES[0])
    return Main.load_pickle_binary(filename)


@dataclass
class _StatsDataSingleConf:
    __slots__ = ("nth", "conf_speech_total", "conf_speech_female")
    nth: int
    conf_speech_total: int
    conf_speech_female: int

    def __add__(self, o: Self) -> Self:
        _total: int = self.conf_speech_total + o.conf_speech_total
        _female: int = self.conf_speech_female + o.conf_speech_female
        return self.__class__(self.nth, _total, _female)

    def __get_female_speech_percentage(self) -> float:
        return self.conf_speech_female / self.conf_speech_total

    def __repr__(self):
        return f"""<
    Total:  {self.conf_speech_total} chars,
    Female: {self.conf_speech_female} chars
            ({self.__get_female_speech_percentage():.2%})
    >"""


def _deafult_stats_singleconf_factory():
    return _StatsDataSingleConf(0, 0, 0)


def get_stats(nth: int) -> dict:
    STATS: defaultdict = defaultdict(_deafult_stats_singleconf_factory)
    for conf_desc in tqdm(get_conf_descriptions_nth(nth)):
        _stats = _StatsDataSingleConf(
            nth,
            conf_desc.n_total_mp_speech_char_count,
            conf_desc.n_total_female_mp_speech_char_count,
        )
        STATS[conf_desc.comm_name] += _stats
    return dict(STATS)


class _Main:
    def get(self, nth: int) -> None:
        WIDTH, HEIGHT = get_terminal_size()
        print(f"{nth=}".center(WIDTH, "="))
        pp((result := get_stats(nth)))
        print(f"Total: {len(result)}")


if __name__ == "__main__":
    fire.Fire(_Main)
