#!/usr/bin/env python3

import json
import fitz
import re
import sys
from os import _exit
from ajconsole import Message
from ajcore import _USB_PDF_PATH


LOGGING = False
console = Message(enabled=LOGGING)


class PDFText:
    def __init__(self, pdf: fitz.Document):
        self.title = pdf.metadata["title"]
        self.speakers = []
        self.text = ""
        for page_index, page in enumerate(pdf):
            self.text += page.get_text()
        self.lines = self.text.split("\n")
        self.result = {}

    @staticmethod
    def get_stats_from_file(pdf_file_path: str):
        """
        Turns its argument into a PDFText object, decode the content,
        and returns speech stats as a Python dictionary (something like `{NAME: SPEECH_AS_TEXT}`).
        """
        fitz_doc = fitz.open(pdf_file_path)  # type: fitz.Document
        pdf_text = PDFText(fitz_doc)
        pdf_text.get_stats()
        return pdf_text.result

    def show_text(self) -> None:
        print(self.text)

    def get_speaker_info(self, line: str) -> str:
        """
        Checks every single line.
        If valid speaker info found, return a string containing speaker's name and job.
        Else, returns an empty string.
        """
        speaker_info_pattern = r"◯\S+ \S+ {1,2}"
        speaker_info = re.compile(speaker_info_pattern).search(line) or ""

        if isinstance(speaker_info, str):  # No match

            # LARGE CIRCLE found, but it's not a MP speaker.
            # It could be a non-politician speaker, or some skippable information.
            if "◯" in line:
                console.warn(line)
                console.error(
                    "No MP speaker info found, but ◯ found - Probably a non-politician speaker? If it was a non-politician speaker, then everything's fine; otherwise, could be an error."
                )
                return "LargeCircleButNoNewSpeaker"

                if "참석" in line:
                    return "EOF"
                elif "출석" in line:
                    return "EOF"

            elif "【" in line:
                return "EOF"

            elif line.startswith("◯출석"):
                return "EOF"
            else:
                return ""

        else:
            return speaker_info.group().strip()
        ...

    def is_line_pages_header(self, line: str) -> bool:
        """
        Checks if line is something like "제397회－제4차(2022년5월29일)  21"
        or "22  제397회－제4차(2022년5월29일)"
        """
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
            return True

        elif result_two:
            console.warn(
                "Page header(right) skipped: " + "\033[0m" + f'"{line}"', prefix="pg."
            )
            return True

        else:
            return False

        ...

    def is_line_bill_desc(self, line: str) -> bool:
        """Checks if line is bill info. Ignores this line if True."""
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
        Check if line is skippable. Ignores this line if True.
        """
        small_circle_pattern = r"^o"
        regex = re.compile(small_circle_pattern)
        result = regex.search(line)
        if result:
            console.warn(
                "Line starts with 'o' found: " + "\033[0m" + f'"{line}"', prefix=" o "
            )
            return True
        return False

        ...

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
        dismiss_act_pattern = r"\([0-9]{1,2}시[0-9]{1,2}분 산회\)"
        regex = re.compile(dismiss_act_pattern)
        result = regex.search(line)
        if result:
            console.error("-- End of conf --", prefix="EOF")
            return True
        return False

    def get_stats(self):

        current_speaker = ""

        for line in self.lines:

            # Scanning the line
            new_speaker = self.get_speaker_info(line)

            # Skipping the tail
            if new_speaker == "EOF":
                current_speaker = ""
                break

            elif new_speaker == "LargeCircleButNoNewSpeaker":
                console.warn("Large circle found but no one spoke")
                console.warn(line)
                current_speaker = ""
                continue  # Used to be `break` but then it sees non-politician speakers as EOF.
                ...

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

            # 1) Line is a normal line...
            # 2) Found a new speaker!
            else:

                if new_speaker:

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
    LOGGING = True
    console = Message(enabled=LOGGING)
    main()
