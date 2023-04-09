"""
This module provides functions and classes for performing
operations on local csv data files.
"""
from collections import defaultdict
import ajcore as core
from ajcore import _USB_PDF_PATH
from ajpdf import PDFText, pdf_to_dict
import datetime
import time
from ajcore import (
    FEMALE_MP_LIST,
    MP,
    FemaleMP,
    MPList,
    MPName,
    FemaleMPName,
    Assembly,
    Movie,
    Speak,
    get_conf_vod_link,
)
from tqdm import tqdm
from os import listdir
import re
import csv
import json
from typing import Union
from unicodedata import normalize
from konlpy.tag import Kkma

__all__ = [
    "core",
    "MP",
    "MPList",
    "Assembly",
    "Conference",
    "Conferences",
    "Movie",
    "Speak",
    "MPSpeechRecord",
    "PDFText",
    "ConfBuilder",
    "period",
    "get_mp_speech_record",
    "pdf_to_dict",
    "get_conf_from_keys",
    "ConfDescription",
]


DATE_PARSE_FORMAT = "%Y-%m-%d"
FULL_PARSE_FORMAT = DATE_PARSE_FORMAT + " " + "%H:%M"


class ConfDescription:
    """Conference.describe()"""

    def __init__(
        self,
        *,
        n_total_speakers: int,
        n_total_female_speakers: int,
        n_total_female_mp_speech_char_count: int,
        n_total_mp_speech_char_count: int,
        female_mp_speaker_names: list,
        conf_ct1: str,
        conf_ct2: str,
        conf_ct3: str,
        conf_mc: str,
        conf_date: str,
        conf_open_time: str,
        comm_name: str,
    ):
        self.n_total_speakers = n_total_speakers
        self.n_total_female_speakers = n_total_female_speakers
        self.n_total_female_mp_speech_char_count = n_total_female_mp_speech_char_count
        self.n_total_mp_speech_char_count = n_total_mp_speech_char_count
        self.female_mp_speaker_names = female_mp_speaker_names
        self.ct1 = conf_ct1
        self.ct2 = conf_ct2
        self.ct3 = conf_ct3
        self.mc = conf_mc
        self.date = conf_date
        self.open_time = conf_open_time
        self.comm_name = comm_name

    def __repr__(self):
        _females = (
            ""
            if not self.female_mp_speaker_names
            else ", ".join([str(name) for name in self.female_mp_speaker_names])
        )
        return f"{self.__class__.__qualname__}({self.comm_name}; Total: {self.n_total_speakers} MP speakers, with {self.n_total_mp_speech_char_count} total characters; {self.n_total_female_speakers} female MP spoke{': ' + _females if _females else _females}; Time: {self.date} {self.open_time})"

    @property
    def has_multiple_identities_female_mp(self) -> bool:
        """Sometimes, speaker has multiple identities in a conference, she can be the leader of a committe, and, a normal MP at the same time. Return true if this situation exists"""
        return not len(set(self.female_mp_speaker_names)) == len(
            self.female_mp_speaker_names
        )

    def get_number_of_duplicated_female_mp_names(self) -> int:
        return len(self.female_mp_speaker_names) - len(
            set(self.female_mp_speaker_names)
        )

    @property
    def date_time(self) -> datetime.datetime:
        return datetime.datetime.strptime(
            f"{self.date} {self.open_time}", "%Y-%m-%d %H:%M"
        )

    def __lt__(self, o):
        return self.date_time < o.date_time

    def __eq__(self, o):
        return (
            self.ct1 == o.ct1
            and self.ct2 == o.ct2
            and self.ct3 == o.ct3
            and self.mc == o.mc
        )

    def __gt__(self, o):
        return self.date_time > o.date_time

    def __ge__(self, o):
        return self.date_time >= o.date_time

    def __le__(self, o):
        return self.date_time <= o.date_time

    @property
    def conf(self):
        return ConfBuilder.from_conf_description_obj(self)

    @property
    def conference(self):
        return self.conf

    @property
    def percentage_female_mp_speech(self) -> float:
        return (
            self.n_total_female_mp_speech_char_count / self.n_total_mp_speech_char_count
        )

    @property
    def percentage_female_mp(self) -> float:
        return self.n_total_female_speakers / self.n_total_speakers

    pass


class MPSpeechStats:
    """This class is used in `speech_records`'s `defaultdict` to handle KeyError; I probably should never use it this way but whatever"""

    def __init__(self):
        raise KeyError("MP speech not found")


# alias
SpeechNotFound = MPSpeechStats


class Conference:
    """Conference from local data."""

    __slots__ = (
        "angun_base",
        "sami",
        "minutes",
        "ct1",
        "ct2",
        "ct3",
        "menu",
        "type",
        "movie_list",
        "open_time",
        "week",
        "hand_lang",
        "date",
        "mc",
        "minutes_type",
        "audio_service",
        "title",
        "angun",
        "qvod",
    )

    def __init__(
        self,
        angun_base: str,
        sami: str,
        minutes: str,
        ct1: str,
        ct2: str,
        ct3: str,
        menu: str,
        type: str,
        movie_list: list[dict],
        open_time: str,
        week: str,
        hand_lang: str,
        date: str,
        mc: str,
        minutes_type: str,
        audio_service: int,
        title: str,
        angun: list[dict],
        qvod: int,
    ):
        self.angun_base: str = angun_base
        self.sami: str = sami
        self.minutes: str = minutes
        self.ct1: str = ct1
        self.ct2: str = ct2
        self.ct3: str = ct3
        self.menu: str = menu
        self.type: str = type
        self.movie_list: list = movie_list
        self.open_time: str = open_time.replace(" ", "0")
        self.week: str = week
        self.hand_lang: str = hand_lang
        self.date: str = date
        self.mc: str = mc
        self.minutes_type: str = minutes_type
        self.audio_service: int = audio_service
        self.title: str = title
        self.angun: list[dict] = angun
        self.qvod: int = qvod

    def __repr__(self) -> str:
        _type: str = "" if self.type in (None, "") else f" <{self.type}> "
        return f"Conference({self.date}, {self.open_time}, {self.week}, {self.title}{_type}, {len(self.movies)} movie(s))"

    def __eq__(self, o) -> bool:
        return (
            self.ct1 == o.ct1
            and self.ct2 == o.ct2
            and self.ct3 == o.ct3
            and self.mc == o.mc
            and self.date == o.date
            and self.open_time == o.open_time
        )

    @property
    def _anji_usb_pdf_file_name(self):
        return f"{self.date}_{self.ct1}.{self.ct2}.{self.ct3}.{self.mc}.pdf"

    @property
    def all_possible_female_mp_with_details(self) -> list:
        """Returns a list of class `FemaleMP`s, could contain duplicated person with slightly different details"""
        result = []
        for femaleMP in FEMALE_MP_LIST:
            for lady in self.all_possible_female_mp:
                if femaleMP.name.hangul == normalize(
                    "NFKC", lady.name
                ) or femaleMP.name.hanja == normalize("NFKC", lady.name):
                    result.append(femaleMP)
        return result

    @property
    def all_possible_female_mp(self):
        """Returns **ONLY** hangul names which means could be not correct because sometimes two MPs have the **SAME** hangul name (e.g. 권은희). Use `self.all_possible_female_mp_with_details()` then turn the value into a `set` instead"""
        return Assembly(self.ct1).females

    def _debug_describe(self) -> dict:
        """Internal use only, probably not the best algorithm => slow"""
        result = {}
        _n_total_speakers = len(self.get_all_mp_speakers())
        _n_total_female_speakers = self.nb_female_mp_speakers
        _n_total_char_count = self.get_all_mp_speech_total_character_count()
        _n_total_char_count_female = 0
        content_female: dict[
            str, list[str]
        ] = self.get_all_female_mp_speakers_and_speeches()
        for key in content_female:
            for line in content_female[key]:
                _n_total_char_count_female += len(line)

        result["Total MP speakers"] = _n_total_speakers
        result["Female MP speakers"] = _n_total_female_speakers
        result["Total MP speech characters (M + F)"] = _n_total_char_count
        result["Total female MP speech characters"] = _n_total_char_count_female
        return result

    def describe(self) -> ConfDescription:
        """Returns a ConfDescription object containing basic stats info about a conference"""
        _n_total_speakers = 0
        _n_female_speakers = 0
        _n_total_char_count = 0
        _n_total_char_count_female = 0
        _female_mp_names = []
        as_py_dict = self.as_python_dict()
        for key in tqdm(as_py_dict, leave=False, desc=f"conf.describe{self.comm_name}"):
            normalized_key_name_title = normalize("NFKC", key)
            for femaleMP in tqdm(
                set(self.all_possible_female_mp_with_details),
                desc=f"{normalized_key_name_title[1:4]}...",
                leave=False,
            ):
                if (
                    femaleMP.name.hangul in normalized_key_name_title
                    or femaleMP.name.hanja in normalized_key_name_title
                ):
                    _n_female_speakers += 1
                    _female_mp_names.append(femaleMP.name)
                    for line in as_py_dict[key]:
                        _n_total_char_count_female += len(line)
            else:
                _n_total_speakers += 1
                for line in as_py_dict[key]:
                    _n_total_char_count += len(line)
        return ConfDescription(
            n_total_speakers=_n_total_speakers,
            n_total_female_speakers=_n_female_speakers,
            n_total_mp_speech_char_count=_n_total_char_count,
            n_total_female_mp_speech_char_count=_n_total_char_count_female,
            female_mp_speaker_names=_female_mp_names,
            conf_ct1=self.ct1,
            conf_ct2=self.ct2,
            conf_ct3=self.ct3,
            conf_mc=self.mc,
            conf_date=self.date,
            conf_open_time=self.open_time,
            comm_name=self.comm_name,
        )
        pass

    def describe_as_dict(self) -> dict:
        """Returns a dict containing basic stats info about a conference"""
        result = {}
        _n_total_speakers = 0
        _n_female_speakers = 0
        _n_total_char_count = 0
        _n_total_char_count_female = 0
        _female_mp_names = []
        as_py_dict = self.as_python_dict()
        for key in as_py_dict:
            normalized_key_name_title = normalize("NFKC", key)
            for femaleMP in tqdm(
                set(self.all_possible_female_mp_with_details),
                desc=f"{normalized_key_name_title[1:4]}...",
                leave=False,
            ):
                if (
                    femaleMP.name.hangul in normalized_key_name_title
                    or femaleMP.name.hanja in normalized_key_name_title
                ):
                    _n_female_speakers += 1
                    _female_mp_names.append(femaleMP.name)
                    for line in as_py_dict[key]:
                        _n_total_char_count_female += len(line)
            else:
                _n_total_speakers += 1
                for line in as_py_dict[key]:
                    _n_total_char_count += len(line)
        result["Total Speakers"] = _n_total_speakers
        result["Total Male MP Speakers"] = _n_total_speakers - _n_female_speakers
        result["Total Female MP Speakers"] = _n_female_speakers
        result["Total Male MP Speech Char Count"] = (
            _n_total_char_count - _n_total_char_count_female
        )
        result["Total Female MP Speech Char Count"] = _n_total_char_count_female
        result["Total MP Speech Char Count"] = _n_total_char_count
        result["Female MP speaker names"] = _female_mp_names
        result["ct1"] = self.ct1
        result["ct2"] = self.ct2
        result["ct3"] = self.ct3
        result["mc"] = self.mc
        return result
        pass

    def get_all_mp_speakers(self) -> list[str]:
        """Returns speakers' names and job titles, with `LARGE_CIRCLE` removed; **NOT** normalized"""
        result = []
        for key in self.as_python_dict():
            result.append(key[1:])
        return result

    def split_by_gender(self) -> tuple[dict, dict]:
        """
        Returns a tuple containing 2 dictionaries
        """
        result_male = {}
        result_female = {}
        _all_mp_speakers = self.as_python_dict()

        # Looping through all names
        for key_name_title in tqdm(_all_mp_speakers, desc="SplitByGender", leave=False):
            _flag_found_a_female = False
            normalized_key_name_title = normalize("NFKC", key_name_title)

            # Matching female names
            for femaleMP in tqdm(
                set(self.all_possible_female_mp_with_details),
                desc=f"{normalized_key_name_title[:5]} - SplitByGender",
                leave=False,
            ):
                if (
                    femaleMP.name.hangul in normalized_key_name_title
                    or femaleMP.name.hanja in normalized_key_name_title
                ):
                    result_female[key_name_title] = _all_mp_speakers[key_name_title]
                    _flag_found_a_female = True

            # If current name does not match any female name, then it's a male MP
            if not _flag_found_a_female:
                result_male[key_name_title] = _all_mp_speakers[key_name_title]

        return (result_male, result_female)

    def get_all_nouns_of_all_speech_of_both_male_and_female(
        self,
    ) -> tuple[list[str], list[str]]:
        kkma = Kkma()
        words_male: list[str] = []
        words_female: list[str] = []
        splitted_dict_of_male, splitted_dict_of_female = self.split_by_gender()

        for key_male in tqdm(
            splitted_dict_of_male, desc="Joining lines(M)", leave=False
        ):
            speech_of_this_guy = ""

            for line in tqdm(
                splitted_dict_of_male[key_male], desc=f"{key_male[1:7]}", leave=False
            ):
                speech_of_this_guy += line

            words_male.extend(kkma.nouns(speech_of_this_guy))

        for key_female in tqdm(
            splitted_dict_of_female, desc="Joining lines(F)", leave=False
        ):
            speech_of_this_lady = ""

            for line in tqdm(
                splitted_dict_of_female[key_female],
                desc=f"{key_female[1:7]}",
                leave=False,
            ):
                speech_of_this_lady += line

            words_female.extend(kkma.nouns(speech_of_this_lady))

        return (words_male, words_female)

    def get_word_frequency_of_both_gender(self) -> tuple[dict, dict]:
        result_male = defaultdict(int)
        result_female = defaultdict(int)
        (
            words_spoke_by_male,
            words_spoke_by_female,
        ) = self.get_all_nouns_of_all_speech_of_both_male_and_female()
        for word_m in tqdm(words_spoke_by_male, desc="Freq(M)", leave=False):
            result_male[word_m] += 1
        for word_f in tqdm(words_spoke_by_female, desc="Freq(F)", leave=False):
            result_female[word_f] += 1

        return (result_male, result_female)

    def get_ordered_word_frequency_of_both_gender(self) -> tuple[dict, dict]:
        freq_male, freq_female = self.get_word_frequency_of_both_gender()
        sorted_freq_male = dict(sorted(freq_male.items(), key=lambda item: item[1]))
        sorted_freq_female = dict(sorted(freq_female.items(), key=lambda item: item[1]))
        return (sorted_freq_male, sorted_freq_female)

    def get_all_female_mp_speakers_and_speeches(self) -> dict:
        """Slice of `conf.as_python_dict()`"""
        result = {}
        _all_mp_speakers = self.as_python_dict()
        for key_name_title in tqdm(_all_mp_speakers, desc="Speech(F)", leave=False):
            normalized_key_name_title = normalize("NFKC", key_name_title)
            for femaleMP in tqdm(
                set(self.all_possible_female_mp_with_details),
                desc=f"{normalized_key_name_title[:7]}...",
                leave=False,
            ):
                if (
                    femaleMP.name.hangul in normalized_key_name_title
                    or femaleMP.name.hanja in normalized_key_name_title
                ):
                    result[key_name_title] = _all_mp_speakers[key_name_title]
        return result

    @property
    def nb_female_mp_speakers(self) -> int:
        """Returns number of female MPs those who had a speech"""
        return len(self.get_all_female_mp_speakers_and_speeches())

    def get_all_mp_speakers_unicode_normalized(self) -> list:
        """Returns list of unicode normalized MP speaker names"""
        result = []
        for key in tqdm(self.as_python_dict(), desc="NameNormalized(F)", leave=False):
            result.append(normalize("NFKC", key[1:]))
        return result

    def get_all_mp_speech_total_character_count(self) -> int:
        """Total speech character count (male + female)"""
        result = 0
        for list_of_lines in tqdm(
            self.as_python_dict().values(), desc="CharCount", leave=False
        ):
            for line in list_of_lines:
                result += len(line)
        return result

    def get_female_mp_speeches(self) -> dict:
        """Returns female MP speech content (list of strings) as a Python dict"""
        result = {}
        full_dict = self.as_python_dict()
        for name_with_job_title in tqdm(
            full_dict, desc=f"Looking for lady of gen{self.ct1}", leave=False
        ):
            key_name = normalize("NFKC", name_with_job_title)
            for femaleMP in tqdm(
                self.all_possible_female_mp_with_details, desc="MatchingName(n,F)"
            ):
                if femaleMP.name.hangul in key_name or femaleMP.name.hanja in key_name:
                    result[name_with_job_title] = full_dict[name_with_job_title]
        return result

    def as_python_dict(self, pdf_file_path=None) -> dict:
        """alias of `self.from_pdf_to_python_dict`"""
        if pdf_file_path == None:
            pdf_file_path = _USB_PDF_PATH
        return self.from_pdf_to_python_dict(pdf_file_path)

    def from_pdf_to_python_dict(self, path=_USB_PDF_PATH) -> dict:
        """Turns a PDF file into an object then into a dictionary, `path` defaults to Anji's USB stick. Parent directory name has to be the `year`"""
        if path == _USB_PDF_PATH:
            _full_path = (
                _USB_PDF_PATH
                / f"{self.date[:4]}/{self.date}_{self.ct1}.{self.ct2}.{self.ct3}.{self.mc}.pdf"
            )
        return pdf_to_dict(_full_path)

    @property
    def _anji_usb_pdf_file_path(self):
        """File path, on Anji's USB"""
        return (
            _USB_PDF_PATH
            / f"{self.date[:4]}/{self.date}_{self.ct1}.{self.ct2}.{self.ct3}.{self.mc}.pdf"
        )

    @property
    def full_time_string(self) -> str:
        """Returns a string represents date and time"""
        full_time_string = self.date + " " + self.open_time
        return full_time_string

    def __lt__(self, o) -> bool:
        return time.strptime(self.full_time_string, FULL_PARSE_FORMAT) < time.strptime(
            o.full_time_string, FULL_PARSE_FORMAT
        )

    def __gt__(self, o) -> bool:
        return time.strptime(self.full_time_string, FULL_PARSE_FORMAT) > time.strptime(
            o.full_time_string, FULL_PARSE_FORMAT
        )

    def __le__(self, o) -> bool:
        return time.strptime(self.full_time_string, FULL_PARSE_FORMAT) <= time.strptime(
            o.full_time_string, FULL_PARSE_FORMAT
        )

    def __ge__(self, o) -> bool:
        return time.strptime(self.full_time_string, FULL_PARSE_FORMAT) >= time.strptime(
            o.full_time_string, FULL_PARSE_FORMAT
        )

    @property
    def vod_link(self) -> str:
        return get_conf_vod_link(self)

    @property
    def local_csv_file_name(self) -> str:
        return f"{self.date}_gen{self.ct1}.{self.ct2}.{self.ct3}.{self.mc}_{self.open_time}({len(self.movies)}movies).csv"

    @property
    def default_file_name(self) -> str:
        return self.local_csv_file_name.replace(".csv", "")

    @property
    def confer_num_and_pdf_file_id(self) -> tuple[str, str]:
        pdf_link = self.minutes
        if pdf_link in ("", None):
            from sys import stderr

            print(
                f"This conference:\n{self.title!r}\nhas no valid PDF link, check\n{self.vod_link}\nfor details.",
                file=stderr,
            )
            return ("", "")

        try:
            confer_num: str = (
                re.search(r"conferNum=[^&]*", pdf_link)
                .group(0)
                .replace("conferNum=", "")
            )
        except:
            confer_num: str = ""
            from sys import stderr

            print(
                f"confer number not found\n{self.title!r}\n{pdf_link!r}\nhas no valid confer number, check\n{self.vod_link}\nfor details.",
                file=stderr,
            )
        try:
            pdf_file_id: str = (
                re.search(r"pdfFileId=[^&]*", pdf_link)
                .group(0)
                .replace("pdfFileId=", "")
            )
        except:
            pdf_file_id: str = ""
            from sys import stderr

            print(
                f"pdf id not found\n{self.conf_title!r}\n{pdf_link!r}\nhas no valid pdf ID, check\n{self.vod_link}\nfor details.",
                file=stderr,
            )
        return (confer_num, pdf_file_id)

    @property
    def confer_num(self) -> str:
        return self.confer_num_and_pdf_file_id[0]

    @property
    def pdf_file_id(self) -> str:
        return self.confer_num_and_pdf_file_id[1]

    def download_pdf(self, to: str = ".") -> bool:
        """
        Downloads pdf file to some path, defaults to '.'
        returns True if succeed, else False
        """
        with open(f"{to}/{self.default_file_name}.pdf", "wb") as output_pdf:
            output_pdf.write(self.pdf)
            return True
        return False

    @property
    def pdf(self) -> bytes:
        """Returns PDF raw bytes data"""
        action: str = "http://likms.assembly.go.kr/record/mhs-10-040-0040.do"
        import requests
        from faker import Faker

        # # # # # # # # # # #
        # HTTP POST method  #
        # # # # # # # # # # #
        respond = requests.post(
            action,
            data={
                "target": "I_TARGET",
                "enctype": "multipart/form-data",
                "conferNum": self.confer_num,
                "fileId": self.pdf_file_id,
            },
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": Faker().user_agent(),
            },
        )
        # # # # # # # # # # # #
        # returns binary data #
        # # # # # # # # # # # #
        return respond.content

    @property
    def movies(self) -> list:
        return self.movie_list

    @property
    def speaks(self) -> list:
        return [speak for movie in self for speak in movie]

    def has(self, o) -> bool:
        if isinstance(o, MP):
            return any([o.name in speak.title for speak in self.speaks])
        elif isinstance(o, FemaleMP):
            if any([o.hg_nm in speak.title for speak in self.speaks]):
                return True
            elif any([o.hj_nm in speak.title for speak in self.speaks]):
                return True
            else:
                return False
        elif isinstance(o, str):
            return any([o in speak.title for speak in self.speaks])
        elif isinstance(o, MPName):
            return any([o.hangul in speak.title for speak in self.speaks]) or any(
                [o.hanja in speak.title for speak in self.speaks]
            )
        elif isinstance(o, type):
            if o.__qualname__ == "FemaleMP":
                _flag_found = False
                _name_found = ""
                for female_mp in tqdm(FEMALE_MP_LIST, desc="SearchingF"):
                    for speak in self.speaks:
                        if (name := female_mp.hg_nm) in speak.title:
                            _flag_found = True
                            _name_found = name
                        elif (name := female_mp.hj_nm) in speak.title:
                            _flag_found = True
                            _name_found = name
                        else:
                            continue
                    continue
                if _flag_found:
                    import inspect

                    print(
                        f"{inspect.currentframe().f_code.co_name}: found name {_name_found} ({self.title}, {self.date}_{self.ct1}.{self.ct2}.{self.ct3}.{self.mc})"
                    )
                return _flag_found
            else:
                raise TypeError(f"Unexpected type {o.__class__}")

        else:
            raise TypeError(
                f"expected type 'MP', 'FemaleMP' or 'str', instead got: {o.__class__}"
            )
            return False

    @staticmethod
    def from_local_file(path: str) -> "Conference":
        """Opens local file and turns it into a Conference class"""
        with open(path, "r") as local_file_fp:
            reader = csv.reader(local_file_fp)
            for line in reader:
                current_raw_data: dict = json.loads(line[0])
                current_conf_movies_dict_data_list: list = current_raw_data["movieList"]
                current_conf_movies_list: list = []
                for current_movie in current_conf_movies_dict_data_list:
                    current_movie_speak_list: list = current_movie.get("subList")
                    current_conf_movies_list.append(
                        Movie(
                            current_movie.get("realTime"),
                            current_movie["playTime"],
                            current_movie["speakType"],
                            current_movie["no"],
                            [
                                Speak(
                                    d.get("realTime"),
                                    d.get("playTime"),
                                    d.get("speakType"),
                                    d.get("no"),
                                    d.get("movieTitle"),
                                    d.get("wv"),
                                )
                                for d in current_movie_speak_list
                            ]
                            if current_movie_speak_list is not None
                            else [],
                        )
                    )
                current_conf = Conference(
                    current_raw_data["angunBase"],
                    current_raw_data["sami"],
                    current_raw_data["minutes"],
                    current_raw_data["ct1"],
                    current_raw_data["ct2"],
                    current_raw_data["ct3"],
                    current_raw_data["menu"],
                    current_raw_data["type"],
                    # current_raw_data['movieList'],
                    current_conf_movies_list,
                    current_raw_data["confOpenTime"],
                    current_raw_data["confWeek"],
                    current_raw_data["handlang"],
                    current_raw_data["confDate"],
                    current_raw_data["mc"],
                    current_raw_data["munitesType"],
                    current_raw_data["audioService"],
                    current_raw_data["confTitle"],
                    current_raw_data["angun"],
                    current_raw_data["qvod"],
                )
                return current_conf

    def __iter__(self):
        return iter(self.movies)

    @property
    def comm_name(self):
        target_file = None
        for single_file in listdir(core.DATA_FILES_PATH):
            if single_file.startswith(str(self.ct1)) and single_file.endswith("csv"):
                target_file = single_file
        if target_file is None:
            print(
                f"Error: Details(self.comm_name) unavailable for {repr(self)} ({self.ct1}.{self.ct2}.{self.ct3})"
            )
        else:
            with open(core.DATA_FILES_PATH / target_file, "r") as _data:
                reader = csv.reader(_data)
                lines: list[str] = [line[0] for line in reader]
                for line in lines:
                    # `line` is a JSON string.
                    line = json.loads(line)
                    if (
                        line["ct1"] == self.ct1
                        and line["ct2"] == self.ct2
                        and line["ct3"] == self.ct3
                    ) and line["confOpenTime"] == self.open_time:
                        return line["commName"]
                else:
                    print("No record found!")


class ConfBuilder:
    """Build Conference object with keys: `ct1`, `ct2`, `ct3` and `mc`"""

    @classmethod
    def from_conf_description_obj(cls, o: ConfDescription) -> Conference:
        return cls.from_keys(ct1=o.ct1, ct2=o.ct2, ct3=o.ct3, mc=o.mc)

    @classmethod
    def from_keys(cls, *, ct1, ct2, ct3, mc) -> Conference:
        _file = None
        for file in listdir(core.LOCAL_DATA_PATH):
            if file[14:16] == ct1:
                if file.split("_")[1] == f"gen{ct1}.{ct2}.{ct3}.{mc}":
                    _file = file
                    break
        else:
            raise FileNotFoundError(
                f"Local CSV file not found for {ct1}.{ct2}.{ct3}.{mc} (local data path: {core.LOCAL_DATA_PATH})"
            )
        target_path = core.LOCAL_DATA_PATH / _file
        return Conference.from_local_file(target_path)

    pass


# alias
get_conf_from_keys = ConfBuilder.from_keys


class Conferences:
    """Load data from local disk"""

    __slots__ = "generation", "files", "conferences"

    def __init__(self, nth: int):
        self.generation: int = nth
        suffix: str = "" if self.generation > 9 else "0"
        # print(len(core.Local.files))
        self.files = []
        for file in core.Local.files:
            if f"gen{suffix}{nth}" in str(file):
                self.files.append(file)
        self.conferences = []
        progress = tqdm(self.files, unit="conf", leave=False)
        for file in progress:
            current_conf = Conference.from_local_file(file)
            desc = (
                f"{current_conf.title[:9] + '...'}"
                if len(current_conf.title) >= 9
                else f"{current_conf.date}.."
            )
            progress.set_description(f"{desc}")
            self.conferences.append(current_conf)

    @property
    def movies(self) -> list[Movie]:
        return [movie for conf in self for movie in conf]

    @property
    def speaks(self) -> list[Speak]:
        return [speak for movie in self.movies for speak in movie]

    def __iter__(self):
        return iter(self.conferences)

    def __repr__(self) -> str:
        return f"<class '{self.generation}{core.suffix_of(self.generation)} Assembly conferences' ({len(self.conferences)} local records in {str(core.LOCAL_DATA_PATH)!r})>"


class period:
    __slots__ = "files", "start", "end", "conferences"

    def __init__(self, start: str, end: str):
        self.files: list = []
        self.conferences: list[Conference] = []
        self.start: datetime.datetime = datetime.datetime.strptime(start, "%Y-%m-%d")
        self.end: datetime.datetime = datetime.datetime.strptime(end, "%Y-%m-%d")
        for file in tqdm(
            core.Local.files, unit="file", desc=f"{start}to{end}", leave=False
        ):
            filename = str(file.name)
            filedate = filename[:10]
            filedate = datetime.datetime.strptime(filedate, "%Y-%m-%d")
            if self.start <= filedate <= self.end:
                self.files.append(file)
        for file in tqdm(
            self.files,
            unit="conf",
            desc=f"{(self.end - self.start).days} days",
            leave=False,
        ):
            conf: Conference = Conference.from_local_file(file)
            self.conferences.append(conf)

    def __iter__(self):
        return iter(self.conferences)

    def __len__(self):
        return len(self.conferences)

    def __repr__(self) -> str:
        start: str = self.start.strftime("%Y-%m-%d")
        end: str = self.end.strftime("%Y-%m-%d")
        return f"<'period' object, with {len(self.conferences)} conferences from {start} to {end}, at {hex(id(self))}>"

    @property
    def movies(self) -> list[Movie]:
        return [movie for conf in self.conferences for movie in conf]

    @property
    def speaks(self) -> list[Speak]:
        return [speak for conf in self.conferences for movie in conf for speak in movie]


class MPSpeechContent:
    def __init__(self, mp_name: str):
        self.name = mp_name
        self.lines = []
        self.ct1 = -1
        self.ct2 = -1
        self.ct3 = -1
        self.mc = -1

    @property
    def as_lines(self):
        return self.lines

    @property
    def char_count(self) -> int:
        count = 0
        for line in self.lines:
            count += len(line.strip())
        return count

    def __iter__(self):
        return self.lines.__iter__()

    def __repr__(self):
        return f"{self.__class__.__qualname__}({len(self.lines)} lines; Total Characters: {self.char_count})"


class MPSpeechRecord:
    def __init__(self, mp_name: str):
        self.name = mp_name
        self.records: list[Conference] = []

    @property
    def size(self):
        return len(self.records)

    def __iter__(self):
        return self.records.__iter__()

    def __repr__(self):
        return f"<{self.__class__.__qualname__}(name: {self.name}, name found in {len(self.records)} confs)>"

    @property
    def speeches(self):
        return dict(self.speech_records)

    @property
    def speech_records(self, PDF_FILES_PATH="/Volumes/AJ/yeongnok-pdfs/"):
        if PDF_FILES_PATH == "/Volumes/AJ/yeongnok-pdfs":
            print(
                "Using Anji(anzhi0708@gmail.com)'s PERSONAL configuration; you might want to change it"
            )

        # Return this dict at the end of method.
        speech_record = defaultdict(SpeechNotFound)
        for conf in tqdm(self.records, desc=f"{self.name}", leave=False):
            pdf_filename_string = (
                f"{conf.date}_{conf.ct1}.{conf.ct2}.{conf.ct3}.{conf.mc}.pdf"
            )
            pdf_file_full_path = (
                PDF_FILES_PATH + f"{conf.date[:4]}/" + pdf_filename_string
            )
            everyones_speech_record = pdf_to_dict(pdf_file_full_path)
            for name in everyones_speech_record:
                if self.name in normalize("NFKC", name):
                    speech_content = MPSpeechContent(self.name)
                    speech_content.lines = everyones_speech_record[name]
                    speech_content.ct1 = conf.ct1
                    speech_content.ct2 = conf.ct2
                    speech_content.ct3 = conf.ct3
                    speech_content.mc = conf.mc
                    speech_content.comm_name = conf.comm_name
                    speech_record[conf] = speech_content
        return speech_record

    @property
    def confs(self) -> list[Conference]:
        """alias to `self.records`"""
        return self.records

    @property
    def conferences(self) -> list[Conference]:
        """alias to `self.records`"""
        return self.records

    @staticmethod
    def get_by_period_and_name(
        *, name: Union[str, MPName] = "", start: str = "", end: str = ""
    ):
        """
        Takes 3 keyword-only arguments: `start`, `end`, `name`, and returns a `MPSpeechRecord` object.

        This function turns `start` and `end` into a `period` object which contains multuple `Conference`s,
        then loop through the `period` object to check if `name` appeared in that conference.
        """
        if start == "" or end == "" or name == "":
            raise ValueError(
                "`start`, `end` and `name` are required, e.g. `start='2020-01-01', end='2020-02-01', name='안지'`"
            )

        record = MPSpeechRecord(name)
        for conf in period(start, end):
            if conf.has(name):
                if conf not in record.records:
                    record.records.append(conf)
        record.records.sort()
        return record


# alias
get_mp_speech_record = MPSpeechRecord.get_by_period_and_name
