#!/usr/bin/env python3

from ajconsole import Message
from collections import defaultdict
import json
from dearaj import *
import fire
from pprint import pp

LOGGING = False
console = Message(LOGGING)


class StatInfo:
    def __init__(self, file):
        self.DATABASE = core.FEMALE_MP_JSON_DATABASE
        self.FEMALE_MP_LIST = core.get_all_female_mp()
        self.FEMALE_MP_HANGUL_NAMES = []
        self.FEMALE_MP_HANJA_NAMES = []

        for lady in self.FEMALE_MP_LIST:
            if lady.hg_nm not in self.FEMALE_MP_HANGUL_NAMES:
                self.FEMALE_MP_HANGUL_NAMES.append(lady.hg_nm)
            if lady.hj_nm not in self.FEMALE_MP_HANJA_NAMES and lady.hj_nm is not None:
                self.FEMALE_MP_HANJA_NAMES.append(lady.hj_nm)

        with open(file, "r") as file:
            data = json.loads(file.read())
            self.data = data

    def describe(self) -> dict[str, int]:
        result = defaultdict(int)
        for hangul_name in self.FEMALE_MP_HANGUL_NAMES:
            for key in self.data:
                if hangul_name in key:
                    for line in self.data[key]:
                        result[hangul_name] += len(line)
        for hanja_name in self.FEMALE_MP_HANJA_NAMES:
            for key in self.data:
                if hanja_name in key:
                    for line in self.data[key]:
                        result[hanja_name] += len(line)
        return result

    def query(self, names: tuple[str]):
        result = defaultdict(int)
        # `names` can hold hangul name(s) / hanja name(s).
        # Have to get mapping
        names_to_query = []
        for name in names:
            for lady in self.FEMALE_MP_LIST:
                if lady.hg_nm == name and name not in names_to_query:
                    names_to_query.append(lady.hg_nm)
                    if lady.hj_nm not in names_to_query:
                        names_to_query.append(lady.hj_nm)
                if lady.hj_nm == name and name not in names_to_query:
                    names_to_query.append(lady.hj_nm)
                    if lady.hg_nm not in names_to_query:
                        names_to_query.append(lady.hg_nm)

        for key in self.data:
            for name in names_to_query:
                if name in key:
                    for line in self.data[key]:
                        result[name] += len(line)

        return result


if __name__ == "__main__":
    fire.Fire(StatInfo)
