#!/usr/bin/env python3

import json
import fitz
import re
from ajconsole import Message
from typing import Union, Type
from unicodedata import normalize


class _Status:
    def __str__(self):
        return self.__class__.__qualname__

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o):
        return str(self) == str(o)


class DoneInitializing(_Status):
    pass


class ProcessingText(_Status):
    pass


class PerformingRegexSearch(ProcessingText):
    pass


class InitializingPDFTextLines(ProcessingText):
    pass


class LookingForSpeaker(ProcessingText):
    pass


class AnjiDefinedWarning:
    def __init__(self, line: str):
        self.text = line

    pass


class LargeCircleFoundButNoValidNewSpeakerInfo(AnjiDefinedWarning):
    pass


class IsTheEndOfThisPDFFile(AnjiDefinedWarning):
    pass


class PDFText:
    def __init__(
        self,
        pdf: fitz.Document,
        *,
        file_name: str,
        enable_logging: bool = False,
        save: bool = False,
    ):
        # Real PDF file / conf title cause metadata is fucking useless
        self.real_title: str = ""

        self.save: bool = save
        self.file_name: str = file_name.split("/")[-1]

        # PDF processing status
        self.status: _Status = _Status()

        # Create logging instance
        self.console: Message = Message(enabled=enable_logging)

        # Meta information from PyMuPDF
        self.title: str = pdf.metadata["title"]

        # Speaker info line
        self.speakers: list[str] = []

        # From 'machine unreadable PDF file' -> 'text'
        self.lines: list[str] = []

        # Updating status
        self.update_status(InitializingPDFTextLines)

        for page_index, page in enumerate(pdf):
            lines_of_this_page: list = page.get_text().split("\n")
            for line in lines_of_this_page:
                self.lines.append(line)

        # Stats
        self.result: dict[str, list[str]] = {}

        # Updating status
        self.update_status(DoneInitializing)

    def save_result(self):
        import pickle

        with open(
            f"./serialized/{self.file_name[:4]}/{self.file_name.replace('.pdf', '.pickle')}",
            "wb",
        ) as target:
            pickle.dump(self.result, target)

    def update_status(self, new_status):
        self.status = new_status if self.status != new_status else self.status

    @staticmethod
    def get_stats_from_file(pdf_file_path: str):
        """
        Turns its argument into a PDFText object, decode the content,
        and returns speech stats as
        a Python dictionary (something like `{NAME: SPEECH_AS_TEXT}`).
        """
        fitz_doc = fitz.open(pdf_file_path)  # type: fitz.Document
        pdf_text = PDFText(fitz_doc, file_name=pdf_file_path)
        pdf_text.get_stats()
        return pdf_text.result

    def show_text(self) -> None:
        print(self.lines)

    def try_speaker_info(self, line: str) -> Union[str, AnjiDefinedWarning]:
        """
        Checks every single line.
        If valid speaker info found,
        return a string containing speaker's name and job.
        Else, return an empty string.
        """
        self.update_status(LookingForSpeaker)

        console = self.console

        # Search for LARGE_CIRCLE but don't catch it
        speaker_info_pattern = r"(?:◯)\S+ \S+ {1,2}"
        speaker_info = re.compile(speaker_info_pattern).search(line)

        if speaker_info is None:  # No match
            # LARGE CIRCLE found, but it's not a
            # valid speaker or anything useful
            # It could be a non-politician speaker,
            # or some skippable information.
            if "◯" in line:
                # Show unprintable characters for debugging
                console.warn(
                    '"' + line.replace("\n", "<NL>").replace(" ", "<SPACE>") + '"'
                )

                # Give some hint
                console.warn(
                    "No valid speaker found, but ◯ found (see above)",
                    prefix="[!]",
                )
                console.warn(
                    "Some possibilities:\n"
                    "      - End of file\n"
                    "      - Line or job title too long\n"
                    "      - An error\n"
                )
                console.warn(
                    "Will try to combine 2 lines.\n"
                    "    If combining succeeded, then everything will be fine,\n"
                    "    and this warning message should be ignored :)"
                )
                return LargeCircleFoundButNoValidNewSpeakerInfo(line)

                if "참석" in line:
                    return IsTheEndOfThisPDFFile(line)
                elif "출석" in line:
                    return IsTheEndOfThisPDFFile(line)
            elif "【" in line:
                return IsTheEndOfThisPDFFile(line)
            elif line.startswith("◯출석"):
                return IsTheEndOfThisPDFFile(line)
            else:
                return ""

        else:  # Return that info if found valid speaker info
            return speaker_info.group().strip()

    def is_line_pages_header(self, line: str) -> bool:
        """
        Checks if line is something like:
          - "제397회－제4차(2022년5월29일)  21"
          - "22  제397회－제4차(2022년5월29일)"
        etc.
        """
        console = self.console
        pages_header_pattern_one = r"^ ?\d{1,4}  제\S+\)$"
        pages_header_pattern_two = r"^제\d+\S+\)  \d{1,4}"
        regex_one = re.compile(pages_header_pattern_one)
        regex_two = re.compile(pages_header_pattern_two)
        result_one = regex_one.search(line)
        result_two = regex_two.search(line)

        if result_one:
            console.warn(
                "Page header(left) skipped:  " + "\033[0m" + f'"{line}"', prefix="pg."
            )
            if not self.real_title:
                self.real_title = line.split(" ")[-1]
            return True

        elif result_two:
            console.warn(
                "Page header(right) skipped: " + "\033[0m" + f'"{line}"', prefix="pg."
            )
            if not self.real_title:
                self.real_title = line.split(" ")[0]
            return True

        else:
            return False

    def is_line_bill_desc(self, line: str) -> bool:
        """Checks if line is bill info. Ignores this line if True."""
        console = self.console

        bill_pattern = r"^ ?\d+\. .+"
        regex = re.compile(bill_pattern)
        result = regex.search(line)
        if result:
            console.warn(
                "Bill description skipped: " + "\033[0m" + f'"{line}"', prefix=" B "
            )
            return True
        return False
        ...

    def is_line_started_with_small_circle(self, line: str) -> bool:
        """
        Check if line is skippable.
        Ignores this line if True.
        """
        console = self.console

        small_circle_pattern = r"^o"
        regex = re.compile(small_circle_pattern)
        result = regex.search(line)
        if result:
            console.warn(
                "Line starts with 'o' found: " + "\033[0m" + f'"{line}"', prefix=" o "
            )
            return True
        return False

    def is_line_action_desc(self, line: str) -> bool:
        """
        Check if line is an action description which can be skipped.
        e.g.
            - "(｢예｣ 하는 의원 있음)"
            - "(일동 기립)"
            - "(박수)"
            - "(19시51분)"
        etc.
        """
        console = self.console

        action_desc_pattern = r"^(\s\s\s\s)?\(.*\)\s?$"

        regex = re.compile(action_desc_pattern)
        result = regex.search(line)
        if result:
            console.warn(
                "Action description skipped: " + "\033[0m" + f'"{line}"', prefix="[-]"
            )
            return True
        return False

    def is_line_end_of_conf(self, line: str) -> bool:
        console = self.console

        dismiss_act_pattern = r"\([0-9]{1,2}시[0-9]{1,2}분 산회\)"
        regex = re.compile(dismiss_act_pattern)
        try:
            result = regex.search(line)
        except Exception as e:
            print(line)
            raise e
        if result:
            console.log("-- End of conf --", prefix="EOF")
            print("---", line)
            return True

        if line.startswith("◯출석") or line.startswith("◯참석") or line.startswith("【"):
            console.log(f"Looks like this is the end of the conf:\n" f'    "{line}"')
            return True

        return False

    def is_line_useless(self, line: str) -> bool:
        return (
            True
            if self.is_line_action_desc(line)
            or self.is_line_bill_desc(line)
            or self.is_line_pages_header(line)
            else False
        )

    def get_stats(self):
        """
        The main loop for handling text analysis
        """
        console = self.console

        current_speaker: str = ""

        # Sometimes the line of speaker info gets too long
        # that line could not be parsed properly
        # For example,
        # Line 1: "◯가습기살균제사건과4․16세월호참사특별조사"
        # Line 2: "위원장 장완익  먼저 헬기를 못 탄 이유에 대해"
        # Line 3: "서 조금 더 조사가 이루어져야 되겠습니다마는"
        # etc.
        # So it's necessary to remember the previous line.
        previous_line: str = ""

        for line in self.lines:
            line = normalize("NFKC", line)

            if self.is_line_end_of_conf(line):
                current_speaker = ""
                console.warn("Reached the end of file", prefix="EOF")
                console.log(
                    f"\n{'#' * 31}\nTotal: {len(set(self.speakers))} speakers\n{'#' * 31}",
                    prefix="",
                )
                # Stop handling text
                break

            # Skipping action descriptions & page headers
            elif self.is_line_action_desc(line):
                if self.is_line_end_of_conf(line):
                    break
                continue

            elif self.is_line_pages_header(line):
                continue

            # Skipping action desc & bill info
            elif self.is_line_started_with_small_circle(line):
                current_speaker = ""
                continue

            elif self.is_line_bill_desc(line):
                current_speaker = ""
                continue

            # Scanning the line
            else:
                new_speaker = self.try_speaker_info(line)

            # If the line before has a LARGE CIRCLE but no speaker found
            if previous_line:
                if not self.is_line_useless(line):
                    line = previous_line + line
                    console.log(f'Line combined:\n    "{line}"')
                    # Clear the `previous_line`
                    previous_line = ""
                    console.log("Now analyzing combined new line")
                    new_speaker = self.try_speaker_info(line)
                else:
                    console.warn(
                        "Line NOT combined since "
                        "this line seems to be useless:"
                        '\n----> "' + line + '"'
                    )
                    input("What do you think? ")
                    continue

            # Skipping the tail
            if isinstance(new_speaker, IsTheEndOfThisPDFFile):
                current_speaker = ""
                # Stop handling text
                break

            elif isinstance(new_speaker, LargeCircleFoundButNoValidNewSpeakerInfo):
                previous_line = line
                continue

            # 1) Line is a normal line...
            # 2) Found a new speaker!
            else:
                if new_speaker:
                    new_speaker = normalize("NFKC", new_speaker)
                    self.speakers.append(new_speaker)

                    if new_speaker not in self.result.keys():
                        current_speaker = new_speaker
                        self.result[new_speaker] = []
                        self.result[new_speaker].append(line.replace(new_speaker, ""))
                        console.log(
                            new_speaker.replace("◯", "") + " has appeared!",
                            prefix=" ◯ ",
                        )
                        continue

                    if not current_speaker:
                        current_speaker = new_speaker
                        self.result[new_speaker].append(line.replace(new_speaker, ""))
                        console.log(
                            new_speaker.replace("◯", "") + " relaunched the conf!",
                            prefix=">>>",
                        )
                        continue

                    if new_speaker != current_speaker:
                        self.result[new_speaker].append(line.replace(new_speaker, ""))
                        current_speaker = new_speaker
                        console.log(
                            new_speaker.replace("◯", "") + " just took the mic!",
                            prefix="···",
                        )
                        continue

                # A normal line
                else:
                    if current_speaker:
                        self.result[current_speaker].append(line)
                        continue

                    else:
                        console.auto_skipped(line)
                        continue

        self.nb_speakers = len(set(self.speakers))
        if self.save:
            self.save_result()
            print()
            console.log(f"{self.file_name}\n    Pickle file saved")

    @property
    def to_json(self):
        self.get_stats()
        string = json.dumps(self.result, ensure_ascii=False).encode("utf8")
        return string

    def write_json_to_stdout(self):
        string = json.dumps(self.result, ensure_ascii=False).encode("utf8")
        print(string.decode())


# alias
pdf_to_dict = PDFText.get_stats_from_file


class Main:
    def __init__(self):
        print(fitz.__doc__)
        print()

    def parse(self, file: str = "", save: bool = False):
        """Parse single PDF, save the parsed result if necessary"""
        self.file = file
        try:
            self.doc_obj = fitz.open(self.file)  # type: fitz.Document
            print("Found: " + self.file)
        except Exception as e:
            print("File not found!")
            raise e
        ajpdf_doc = PDFText(
            self.doc_obj, enable_logging=True, file_name=self.file, save=save
        )
        ajpdf_doc.get_stats()

        return ajpdf_doc

    def view_dir(self, dir: str):
        """Parse / view the whole directory"""
        self.dir = dir
        import os

        for file in os.listdir(self.dir):
            os.system(f"python ./ajpdf.py {self.dir}/{file}")
            # input("Continue? ")


if __name__ == "__main__":
    import sys

    _FILENAME = ""
    try:
        _FILENAME = sys.argv[1]
    except Exception as e:
        if not _FILENAME:
            print("FILE DOES NOT EXSIST")
            sys.exit(-1)
        else:
            raise e
    Main().parse(_FILENAME)
