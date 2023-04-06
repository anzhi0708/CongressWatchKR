"""
This core module provides basic wrapping / crawling functions and classes.
It also defines important global variables, such as paths, mappings.
"""
import pathlib
from typing import List, Union, Optional, Tuple
from dataclasses import dataclass
import time
from faker import Faker
from unicodedata import normalize

__all__ = [
    "CONFIG_FILE_DIR",
    "CONGRESSMAN_DIR",
    "DATA_FILES_PATH",
    "FEMALE_MP_JSON_DATABASE",
    "PACKAGE_ABS_DIR",
    "LOCAL_DATA_PATH",
    "GEN_PERIOD_DICT",
    "TOOLS_DIR",
    "FEMALE_MP_LIST",
    "ConfLoadError",
    "ConfMovieInfoIsEmptyString",
    "ConfMovieInfoIsNone",
    "ConferNumError",
    "Conference",
    "Conferences",
    "EmptyCSVFile",
    "GetConfMovieInfoError",
    "PdfFileIdError",
    "Local",
    "MP",
    "FemaleMP",
    "MPList",
    "Assembly",
    "Movie",
    "Speak",
    "get_conf_file_info",
    "get_conf_movie_info",
    "get_conf_movies",
    "get_conf_pdf",
    "get_conf_pdf_link",
    "get_conf_vod_link",
    "get_conferences_of",
    "get_end_of",
    "get_end_year_of",
    "get_normal_page_of",
    "get_start_of",
    "get_start_year_of",
    "get_gen_by_year",
    "get_year_by_gen",
    "get_all_female_mp",
    "suffix_of",
]

CONFIG_FILE_DIR: pathlib.Path = pathlib.Path(__file__)
PACKAGE_ABS_DIR: pathlib.Path = CONFIG_FILE_DIR.parent
DATA_FILES_PATH: pathlib.Path = PACKAGE_ABS_DIR / "data"
LOCAL_DATA_PATH: pathlib.Path = PACKAGE_ABS_DIR / "local"
CONGRESSMAN_DIR: pathlib.Path = DATA_FILES_PATH / "congressman_list"

_USB_PDF_PATH = pathlib.Path("/Volumes/AJ/yeongnok-pdfs")

FEMALE_MP_JSON_DATABASE = DATA_FILES_PATH / "ALL_FEMALE_MP.json"

TOOLS_DIR = PACKAGE_ABS_DIR


GEN_PERIOD_DICT: dict = {
    21: ("2020-05-30", "2024-05-29"),
    20: ("2016-05-30", "2020-05-29"),
    19: ("2012-05-30", "2016-05-29"),
    18: ("2008-05-30", "2012-05-29"),
    17: ("2004-05-30", "2008-05-29"),
    16: ("2000-05-30", "2004-05-29"),
    15: ("1996-05-30", "2000-05-29"),
    14: ("1992-05-30", "1996-05-29"),
    13: ("1988-05-30", "1992-05-29"),
    12: ("1985-04-11", "1988-05-29"),
    11: ("1981-04-11", "1985-04-10"),
    10: ("1979-03-12", "1980-10-27"),
    9: ("1973-03-12", "1979-03-11"),
    8: ("1971-07-01", "1972-10-17"),
    7: ("1967-07-01", "1971-06-30"),
    6: ("1963-12-17", "1967-06-30"),
}


class MPName:
    """Unicode normalized Hangul name & Hanja name"""

    def __init__(self, hangul_name, hanja_name):
        self.hangul_name = normalize("NFKC", hangul_name)
        self.hanja_name = normalize("NFKC", hanja_name)

    def __repr__(self):
        return f"<{self.__class__.__qualname__}(Hangul: {self.hangul_name}; Hanja: {self.hanja_name}; unicode normalized) at {hex(id(self))}>"

    def __getitem__(self, index):
        if index > 1:
            raise IndexError
        return self.hangul_name if index == 0 else self.hanja_name

    def __eq__(self, o):
        return self.hangul == o.hangul and self.hanja == o.hanja

    def __hash__(self):
        return hash((self.hangul, self.hanja))

    @property
    def Hangul(self):
        return self.hangul_name

    @property
    def hangul(self):
        return self.hangul_name

    @property
    def Hanja(self):
        return self.hanja_name

    @property
    def hanja(self):
        return self.hanja_name

    def __str__(self):
        return f"{self.hangul}({self.hanja})"


class FemaleMPName(MPName):
    pass


class GetConfMovieInfoError(Exception):
    pass


class ConfMovieInfoIsNone(GetConfMovieInfoError):
    pass


class ConfMovieInfoIsEmptyString(GetConfMovieInfoError):
    pass


class ConferNumError(Exception):
    pass


class PdfFileIdError(Exception):
    pass


class EmptyCSVFile(Exception):
    pass


class ConfLoadError(Exception):
    pass


@dataclass
class FemaleMP:
    emp_no: str
    mona_cd: str
    hg_nm: str
    hj_nm: str
    eng_nm: str
    age: int
    sex_gbn_nm: str
    dept_img_url: str
    poly_cd: str
    poly_nm: str
    orig_nm: str
    ele_gbn_nm: str
    reele_gbn_nm: str
    unit_cd: str
    units: str
    cmit_nm: str
    cmits: str
    tel_no: str
    e_mail: str
    homepage: str
    staff: str
    secretary: str
    secretary2: str
    bth_date: str
    unit_nm: str
    link_url: str
    open_na_id: str

    @property
    def name(self):
        return FemaleMPName(self.hg_nm, self.hj_nm)

    @property
    def hanja_name(self):
        """Unicode normalized hanja name"""
        return normalize("NFKC", self.hj_nm)

    @property
    def hangul_name(self):
        """Unicode normalized hangul name"""
        return normalize("NFKC", self.hg_nm)

    def __eq__(self, o):
        return self.hanja_name == o.hanja_name and self.hangul_name == o.hangul_name

    def __hash__(self):
        return (self.hanja_name, self.hangul_name, self.bth_date).__hash__()


def get_all_female_mp(FEMALE_MP_JSON: str = FEMALE_MP_JSON_DATABASE) -> list[FemaleMP]:
    import json

    FEMALE_MP_LIST: list[dict] = []

    with open(FEMALE_MP_JSON, "r") as json_data:
        FEMALE_MP_LIST = json.loads(json_data.read())["data"]
    result = list(
        map(
            lambda data: FemaleMP(
                data["empNo"],
                data["monaCd"],
                data["hgNm"],
                data["hjNm"] if data["hjNm"] else "None",
                data["engNm"],
                data["age"],
                data["sexGbnNm"],
                data["deptImgUrl"],
                data["polyCd"],
                data["polyNm"],
                data["origNm"],
                data["eleGbnNm"],
                data["reeleGbnNm"],
                data["unitCd"],
                data["units"],
                data["cmitNm"],
                data["cmits"],
                data["telNo"],
                data["eMail"],
                data["homepage"],
                data["staff"],
                data["secretary"],
                data["secretary2"],
                data["bthDate"],
                data["unitNm"],
                data["linkUrl"],
                data["openNaId"],
            ),
            FEMALE_MP_LIST,
        )
    )
    return result


FEMALE_MP_LIST = get_all_female_mp()


def get_start_of(nth: int) -> str:
    return GEN_PERIOD_DICT[nth][0]


def get_end_of(nth: int) -> str:
    return GEN_PERIOD_DICT[nth][1]


def get_start_year_of(nth: int) -> int:
    return int(GEN_PERIOD_DICT[nth][0][:4])


def get_end_year_of(nth: int) -> int:
    return int(GEN_PERIOD_DICT[nth][1][:4])


def get_year_by_gen(gen: int) -> tuple[str, str]:
    return GEN_PERIOD_DICT[gen]


def get_gen_by_year(year: int) -> list[int]:
    """Getting gen"""
    if year <= 2000:
        return []

    gen: list = []
    for nb_gen in GEN_PERIOD_DICT:
        if int(GEN_PERIOD_DICT[nb_gen][0][:4]) == year:
            gen.append(nb_gen - 1)
            gen.append(nb_gen)
            break
        if (
            int(GEN_PERIOD_DICT[nb_gen][0][:4])
            < year
            < int(GEN_PERIOD_DICT[nb_gen][1][:4])
        ):
            gen.append(nb_gen)
            break
    return gen


def suffix_of(nth: int):
    return (
        "st"
        if nth % 10 == 1
        else "nd"
        if nth % 10 == 2
        else "rd"
        if nth % 10 == 3
        else "th"
    )


def get_normal_page_of(nth: int, page: int = 1) -> dict:
    prefix: str = ""
    start_year: int = get_start_year_of(nth)
    end_year: int = get_end_year_of(nth)
    # Turning '9' to '09', 6 to '06' for the URL
    if nth < 10:
        prefix = "0"
    import time

    url: str = f"https://w3.assembly.go.kr/vod/main/service/list.do?cmd=subList&menu=1&ct1={prefix}{nth}&mc=&searchUpdateDate={start_year}&searchUpdateDate2={end_year}&searchCt2=&searchType_id=&mc_param2=&searchSelect=1&searchString=&curPages={page}&vv={int(time.time())}&"
    import requests
    import json

    response = requests.get(
        url,
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": Faker().user_agent(),
        },
    )

    while response.ok is False:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": Faker().user_agent(),
            },
        )
    return json.loads(response.text)


@dataclass
class Speak:
    """Dictionaries in 'subList'"""

    real_time: Optional[str]
    play_time: str
    speak_type: str
    no: int
    speak_title: str
    wv: int

    @property
    def as_json(self) -> str:
        import json

        return json.dumps(
            {
                "real_time": self.real_time,
                "play_time": self.play_time,
                "speak_type": self.speak_type,
                "no": self.no,
                "speak_title": self.speak_title,
                "wv": self.wv,
            }
        )

    @property
    def title(self) -> str:
        """Unicode normalized Speech Title"""
        return normalize("NFKC", self.speak_title)

    @property
    def speech_title(self) -> str:
        """Unicode normalized Speech Title"""
        return normalize("NFKC", self.speak_title)

    @property
    def type(self) -> str:
        return self.speak_type

    def has(self, string: str) -> bool:
        return normalize("NFKC", string) in self.title

    def __repr__(self) -> str:
        return f"Speak(<{self.type}> {self.title})"

    def __str__(self) -> str:
        return self.title


@dataclass
class Movie:
    """It was in 'movieList'"""

    real_time: Optional[str]
    play_time: str
    speak_type: str
    no: int
    sublist: List[Union[dict, Speak]]

    @property
    def as_json(self) -> str:
        import json

        return json.dumps(
            {
                "real_time": self.real_time,
                "play_time": self.play_time,
                "speak_type": self.speak_type,
                "no": self.no,
                "sublist": self.sublist,
            }
        )

    @property
    def type(self) -> str:
        return self.speak_type

    @property
    def speaks(self) -> list:
        return self.sublist

    def has(self, string: str) -> bool:
        string = normalize("NFKC", string)
        return any([speak.has(string) for speak in self.speaks])

    def __iter__(self):
        return iter(self.sublist)

    def __repr__(self) -> str:
        return f"Movie({len(self.sublist)} speak(s))"


class Local:
    def __init__(self):
        self._files = list(LOCAL_DATA_PATH.glob("*_gen*.*.*.*(*movies).csv"))
        self._number = len(self._files)

    @property
    def files(self) -> list:
        return self._files

    @property
    def number(self) -> int:
        return self._number

    @property
    def path(self) -> str:
        return str(LOCAL_DATA_PATH)


Local = Local()


@dataclass
class Conference:
    """ """

    __slots__ = (
        "sami",
        "angun_type",
        "minutes",
        "ct1",
        "ct2",
        "ct3",
        "open_time",
        "date",
        "hand_lang",
        "mc",
        "conf_title",
        "comm_name",
        "qvod",
    )
    sami: str
    angun_type: list
    minutes: str
    ct1: str
    ct2: str
    ct3: str
    open_time: str
    date: str
    hand_lang: str
    mc: str
    conf_title: str
    comm_name: str
    qvod: int

    @property
    def title(self):
        return self.conf_title

    def get_local_csv_file_name(self):
        return f"{self.date}_gen{self.ct1}.{self.ct2}.{self.ct3}.{self.mc}_{self.open_time}({len(self.get_movies())}movies).csv"

    @property
    def vod_link(self) -> str:
        """It's actually a method"""
        return get_conf_vod_link(self)

    def get_movie_info(self) -> dict:
        return get_conf_movie_info(self)

    def get_confer_num_and_pdf_file_id(self) -> Tuple[str, str]:
        pdf_link: Optional[str] = get_conf_pdf_link(self)
        if pdf_link in ("", None):
            from sys import stderr

            print(
                f"This conference:\n{self.conf_title!r}\nhas no valid PDF link, check its link:\n{self.vod_link!r}\nfor more information.\n",
                file=stderr,
            )
            return ("", "")
        import re

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
                f"confer number not found\n{self.conf_title!r}\n{pdf_link!r}\nhas no valid confer number, check its link\n{self.vod_link!r}\nfor details.\n",
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
                f"pdf id not found\n{self.conf_title!r}\n{pdf_link!r}\nhas no valid pdf ID, check its link\n{self.vod_link!r}\nfor details.\n",
                file=stderr,
            )
        return (confer_num, pdf_file_id)

    @property
    def confer_num(self) -> str:
        """It's actually a method"""
        return self.get_confer_num_and_pdf_file_id()[0]

    @property
    def pdf_file_id(self) -> str:
        """It's actually a method"""
        return self.get_confer_num_and_pdf_file_id()[1]

    def get_movie_list(self) -> List[Movie]:
        return get_conf_movies(self)

    def get_movies(self) -> List[Movie]:
        """This is actually a sweet function"""
        return self.get_movie_list()

    def get_movie_sublist(self) -> List[Speak]:
        result: List[Speak] = []
        for movie in self.get_movie_list():
            if movie.sublist in ([], "", None):
                return []
            for speak in movie.sublist:
                result.append(
                    Speak(
                        speak["realTime"],
                        speak["playTime"],
                        speak["speakType"],
                        speak["no"],
                        speak["movieTitle"],
                        speak["wv"],
                    )
                )
        return result

    @property
    def speaks(self) -> List[Speak]:
        return self.get_movie_sublist()

    def has(self, mp_name: str) -> bool:
        for speak in self.speaks:
            #           if mp_name in speak:  # Is `Speak` iterable?
            if speak.has(mp_name):
                return True
        return False

    @property
    def pdf(self) -> Optional[bytes]:
        """It's actually a method"""
        return get_conf_pdf(self)

    def save_pdf_to(self, path: str) -> None:
        with open(f"{path}", "wb") as output:
            output.write(self.pdf)

    @property
    def as_json(self) -> str:
        import json

        return json.dumps(
            {
                "sami": self.sami,
                "angunType": self.angun_type,
                "minutes": self.minutes,
                "ct1": self.ct1,
                "ct2": self.ct2,
                "ct3": self.ct3,
                "confOpenTime": self.open_time,
                "confDate": self.date,
                "handlang": self.hand_lang,
                "mc": self.mc,
                "confTitle": self.conf_title,
                "commName": self.comm_name,
                "qvod": self.qvod,
            }
        )

    @property
    def as_original_raw_json_data(self) -> str:
        import json

        return json.dumps(get_conf_movie_info(self))

    def to_csv_from_original_raw_json_data(self) -> None:
        import csv

        with open(
            LOCAL_DATA_PATH / self.get_local_csv_file_name(),
            "w",
        ) as output:
            writer = csv.writer(output)
            writer.writerow([self.as_original_raw_json_data])


def get_conf_vod_link(conf: Conference) -> str:
    return f"https://w3.assembly.go.kr/vod/main/player.do?menu=1&mc={conf.mc}&ct1={conf.ct1}&ct2={conf.ct2}&ct3={conf.ct3}&wv=1&"


class get_conferences_of:
    """The crawler, craws by 'nth'"""

    __slots__ = "total_count", "last_page", "conferences"

    def __init__(
        self,
        *,
        nth: int,
        save: bool,
        to: str = "",
        sleep: Union[float, int] = 0.3,
    ):
        save_to_csv: bool = save
        save_to_csv_path: Union[str, pathlib.Path] = to
        if save_to_csv_path == "":
            save_to_csv_path = (
                PACKAGE_ABS_DIR
                / "data"
                / (str(nth) + f"_conferences_{time.strftime('%Y-%m-%d-%H-%M-%S')}.csv")
            )
        if save_to_csv:
            print(f"{save_to_csv_path = }")

        self.total_count: int = 0
        self.last_page: int = 0
        self.conferences: List[Conference] = []
        # # # # # # # # # # # # #
        # Getting the 1st page  #
        # # # # # # # # # # # # #
        first_page: dict = get_normal_page_of(nth)
        self.total_count = first_page["totCnt"]
        try:
            self.last_page = int(first_page["paging"]["moveLast"])
        except ValueError:
            self.last_page = 1
        except Exception as e:
            import pprint

            pprint.pp(first_page)
            print(e)
        for d in first_page["confList"]:
            current_conference: Conference = Conference(
                d["sami"],
                d["angunType"],
                d["minutes"],
                d["ct1"],
                d["ct2"],
                d["ct3"],
                d["confOpenTime"],
                d["confDate"],
                d["handlang"],
                d["mc"],
                d["confTitle"],
                d["commName"],
                d["qvod"],
            )
            self.conferences.append(current_conference)
            if save_to_csv:
                write_dir: Union[str, pathlib.Path] = save_to_csv_path
                import csv

                with open(write_dir, "a+", encoding="UTF-8") as output_fp:
                    writer = csv.writer(output_fp)
                    writer.writerow([current_conference.as_json])
        time.sleep(sleep)
        for page_index in range(2, self.last_page + 1):
            current_page: dict = get_normal_page_of(nth, page_index)
            nb_items: int = len(current_page["confList"])
            if nb_items != 10 and page_index != self.last_page:
                raise RuntimeError("This is not the last page, yet items < 10")
            for d in current_page["confList"]:
                current_conference = Conference(
                    d["sami"],
                    d["angunType"],
                    d["minutes"],
                    d["ct1"],
                    d["ct2"],
                    d["ct3"],
                    d["confOpenTime"],
                    d["confDate"],
                    d["handlang"],
                    d["mc"],
                    d["confTitle"],
                    d["commName"],
                    d["qvod"],
                )
                self.conferences.append(current_conference)
                if save_to_csv:
                    import csv

                    with open(write_dir, "a+", encoding="UTF-8") as output_fp:
                        writer = csv.writer(output_fp)
                        writer.writerow([current_conference.as_json])
            time.sleep(sleep)


class Conferences:
    """Reads csv files on the disk - has to work with local files."""

    __slots__ = "conferences", "generation"

    def __init__(self, nth: int):
        self.generation: int = nth
        self.conferences: List[Conference] = []
        data_csv_files: List[pathlib.Path] = list(
            DATA_FILES_PATH.glob(f"{nth}_conferences*.csv")
        )
        if len(data_csv_files) != 1:
            print(f"{data_csv_files = }, {len(data_csv_files) = }")
        else:
            data_csv_file: pathlib.Path = data_csv_files[0]
            import csv
            import json

            with open(data_csv_file, "r") as json_data_file:
                reader = csv.reader(json_data_file)
                for line in reader:
                    d: dict = json.loads(line[0])
                    current_conference = Conference(
                        d["sami"],
                        d["angunType"],
                        d["minutes"],
                        d["ct1"],
                        d["ct2"],
                        d["ct3"],
                        d["confOpenTime"],
                        d["confDate"],
                        d["handlang"],
                        d["mc"],
                        d["confTitle"],
                        d["commName"],
                        d["qvod"],
                    )
                    self.conferences.append(current_conference)

    def __iter__(self):
        return iter(self.conferences)

    def __getitem__(self, val):
        return self.conferences.__getitem__(val)

    def __repr__(self):
        return f"<{'Empty ' + self.__class__.__name__ + ' of ' + str(self.generation) + suffix_of(self.generation) if self.conferences == [] else self.__class__.__name__ + ' of ' + str(self.generation) + suffix_of(self.generation) + ', total: ' + str(len(self.conferences))}>"


def get_conf_movie_info(conf: Conference) -> dict:
    movie_info_link: str = f"https://w3.assembly.go.kr/vod/main/service/movie.do?cmd=movieInfo&mc={conf.mc}&ct1={conf.ct1}&ct2={conf.ct2}&ct3={conf.ct3}&no=&wv=1&vv={int(time.time())}&"
    import json
    import requests

    response = requests.get(
        movie_info_link,
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": Faker().user_agent(),
        },
    )
    while response.ok is False:
        response = requests.get(
            movie_info_link,
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": Faker().user_agent(),
            },
        )
    received_json_string: str = response.text

    if received_json_string is None:
        raise ConfMovieInfoIsNone
    if received_json_string == "":
        raise ConfMovieInfoIsEmptyString

    return json.loads(received_json_string)


def get_conf_file_info(conf: Conference) -> dict:
    conf_movie_info: dict = get_conf_movie_info(conf)
    parent_movie: dict = conf_movie_info["movieList"][0]
    file_info_link: str = f"https://w3.assembly.go.kr/main/service/movie.do?cmd=fileInfo&mc={conf_movie_info['mc']}&ct1={conf_movie_info['ct1']}&ct2={conf_movie_info['ct2']}&ct3={conf_movie_info['ct3']}&no={parent_movie['no']}&wv=1&xreferer=&vv={int(time.time())}&"
    import json
    import requests

    respond = requests.get(
        file_info_link,
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": Faker().user_agent(),
        },
    )
    received_json_string: str = respond.txt
    return json.loads(received_json_string)


def get_conf_movies(conf: Conference) -> List[Movie]:
    movie_list: list = get_conf_movie_info(conf)["movieList"]
    result: List[Movie] = []
    for movie in movie_list:
        real_time: Optional[str] = movie.get("realTime")
        play_time: str = movie.get("playTime")
        speak_type: str = movie.get("speakType")
        no: int = movie.get("no")
        sublist: Optional[List[dict]] = movie.get("subList")
        result.append(
            Movie(
                real_time,
                play_time,
                speak_type,
                no,
                sublist,
            )
        )
    return result


def get_conf_pdf_link(conf: Conference) -> Optional[str]:
    movie_info: dict = get_conf_movie_info(conf)
    pdf_link: str = movie_info["minutes"]
    return pdf_link


def get_conf_pdf(conf: Conference) -> Optional[bytes]:
    """
    Gets PDF bytes.
    Returns None if PDF file not available.
    """
    action: str = "http://likms.assembly.go.kr/record/mhs-10-040-0040.do"
    pdf_link: str = get_conf_pdf_link(conf)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # unlike 'ct1' to 'ct3', 'minutes' have different types under different #
    # situations(pages), sometimes 'minutes' is a link, sometimes it's a    #
    # number. for this kind of requested page, 'minutes' are links          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    if pdf_link == "":
        # # # # # # # # # # # # # # # # # # #
        # if no PDF available, return None  #
        # # # # # # # # # # # # # # # # # # #
        from sys import stderr

        print(f"valid pdf link not found in\n{conf.conf_title}\n", file=stderr)
        return None
    import re

    print(pdf_link)
    confer_num: str = (
        re.search(r"conferNum=[^&]*", pdf_link).group(0).replace("conferNum=", "")
    )
    pdf_file_id: str = (
        re.search(r"pdfFileId=[^&]*", pdf_link).group(0).replace("pdfFileId=", "")
    )

    import requests

    # # # # # # # # # # #
    # HTTP POST method  #
    # # # # # # # # # # #
    respond = requests.post(
        action,
        data={
            "target": "I_TARGET",
            "enctype": "multipart/form-data",
            "conferNum": confer_num,
            "fileId": pdf_file_id,
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


@dataclass
class MP:
    __slots__ = (
        "generation",
        "_name",
        "party",
        "committee",
        "region",
        "gender",
        "n",
        "how",
    )
    generation: int
    _name: str
    party: str
    committee: Union[list, str]
    region: str
    gender: str
    n: str
    how: str

    @property
    def name(self) -> str:
        """Unicode normalized string"""
        return normalize("NFKC", self._name)

    def __eq__(self, o: Union[str, "MP"]) -> bool:
        """If `name` and / or `gender` is the same, then return True"""
        if isinstance(o, str):
            if normalize("NFKC", o) == normalize("NFKC", self.name):
                return True
        elif isinstance(o, MP):
            if (
                normalize("NFKC", self.name) == normalize("NFKC", o.name)
                and self.gender == o.gender
            ):
                return True
        return False

    @property
    def is_male(self) -> bool:
        return self.gender == "남"

    @property
    def is_female(self) -> bool:
        return self.gender == "여"


class MPList:
    __slots__ = "generation", "members"

    def __init__(self, ct1: Union[int, str]):
        self.generation: int = int(ct1)
        self.members: List[MP] = []
        import csv

        with open(
            CONGRESSMAN_DIR / f"{self.generation}_congressman_list.csv",
            "r",
            encoding="UTF-8",
        ) as congressman_list:
            reader = csv.reader(congressman_list)
            for line in reader:
                this_MP: MP = MP(
                    self.generation,
                    line[2],
                    line[3],
                    [] if line[4] == "" else line[4],
                    line[5],
                    line[6],
                    line[7],
                    line[8],
                )
                self.members.append(this_MP)

    @property
    def male(self) -> int:
        result: int = 0
        for mp in self.members:
            if mp.gender == "남":
                result += 1
        return result

    @property
    def female(self) -> int:
        result: int = 0
        for mp in self.members:
            if mp.gender == "여":
                result += 1
        return result

    @property
    def total(self) -> int:
        return len(self.members)

    def has(self, name: str):
        for mp in self.members:
            if normalize("NFKC", mp.name) == normalize("NFKC", name):
                return True
        return False

    @property
    def parties(self) -> list:
        result: List[str] = []
        for mp in self.members:
            if mp.party not in result:
                result.append(mp.party)
        return result

    @property
    def females(self) -> List[MP]:
        return [mp for mp in self.members if mp.is_female]

    @property
    def males(self) -> List[MP]:
        return [mp for mp in self.members if mp.is_male]

    def __repr__(self):
        return f"{self.__class__.__name__}(male={self.male}, female={self.female}, total={self.total})"

    def __iter__(self):
        return iter(self.members)

    def __eq__(self, target):
        return self.generation == target.generation and self.members == target.members


# alias
Assembly = MPList
