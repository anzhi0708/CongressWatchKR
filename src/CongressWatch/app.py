#!/usr/bin/env python3

import sys
import logging
from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label, Footer, Header
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from os import get_terminal_size
from fitz import Document
from _job_titles import JOB_TITLES


class SpeechContentScreen(Screen):
    """Pop up window that shows certain MP's speech"""

    BINDINGS = [Binding("q,escape", "pop_screen", "back")]

    def __init__(self, key, doc_obj) -> None:
        super().__init__()

        self.key: str = key
        self.doc_obj: Document = doc_obj
        self.buffer: str = ""

    def get_terminal_size(self) -> tuple[int, int]:
        return get_terminal_size()

    def compose(self) -> ComposeResult:
        yield Label(self.key, id="speaker_name_and_title")

        for index, line in enumerate(self.doc_obj.result[self.key]):
            if len(self.buffer) + len(line) >= self.get_terminal_size()[0] // 2:
                self.buffer = self.buffer.replace("  ", "\n")
                yield Label(self.buffer, classes="speech")
                self.buffer = line
                continue
            else:
                self.buffer += line
                continue

        if self.buffer:
            yield Label(self.buffer, classes="speech")

        yield Footer()


class TableScreen(Screen):
    """The main window"""

    BINDINGS = [
        Binding("escape,q", "quit", "quit"),
        Binding("x", "select", "show speech"),
    ]

    def __init__(self, doc_obj) -> None:
        super().__init__()

        self.doc_obj: Document = doc_obj

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        self.table: DataTable = DataTable(id="mp_table", zebra_stripes=True)

        self.table.add_column("Index")
        self.table.add_column("Name & Title", width=15)
        self.table.add_column("[b]Name[/b]", width=17)
        self.table.add_column("Job Title")

        # `self.doc_obj.result` - dict[str, list[str]]
        for index, name in enumerate(self.doc_obj.result):
            job_title_and_name: list[str] = name.split(" ")

            # Removing "◯"
            job_title_and_name = list(
                map(lambda e: e.replace("◯", ""), job_title_and_name)
            )

            # @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @
            """
            with open("./LOG.log", "a") as f:
                f.write(str(job_title_and_name))
            """
            # @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @

            for title in JOB_TITLES:
                if title in job_title_and_name:
                    _job: str = title
                    _name: str = name.replace(_job, "").replace("◯", "").strip()
                    break
            else:
                for name_or_job in job_title_and_name:
                    if len(name_or_job) >= 4:
                        _job = name_or_job
                        job_title_and_name.remove(_job)
                        _name = job_title_and_name[0]
                        break
                else:
                    for name_or_job in job_title_and_name:
                        if "위원" in name_or_job:
                            _job = name_or_job
                            job_title_and_name.remove(_job)
                            _name = job_title_and_name[0]
                            break
                    else:
                        err_msg: str = (
                            f"No valid job title found ({job_title_and_name = })"
                        )
                        e: Exception = RuntimeError(err_msg)
                        logging.warning(err_msg)
                        print(
                            f"\n{__file__}:\nError has been recorded. Check 'log/' for more.",
                            file=sys.stderr
                        )
                        raise e
            self.table.add_row(str(index + 1), name[1:], f"[b]{_name}[/b]", _job)

        yield Vertical(
            Horizontal(self.table, id="mp_table_horizontal"),
        )

        yield Footer()

    def on_mount(self) -> None:
        self.table.focus()

    def action_select(self) -> None:
        _row: int = self.table.cursor_row
        _cell = self.table.get_row_at(_row)[1]
        import re

        _cell_content: str = re.sub(r"\[.*\]", "", _cell)
        self.current_dict_key: str = "◯" + _cell_content
        self.app.push_screen(SpeechContentScreen(self.current_dict_key, self.doc_obj))


class CongressWatch(App[None]):
    """App"""

    CSS_PATH = "style.css"

    def __init__(self) -> None:
        super().__init__()
        """
        _COLS, _ROWS = get_terminal_size()
        self.cols: int = _COLS
        self.rows: int = _ROWS
        """

    def on_mount(self):
        from ajpdf import Main as ajpdf_main

        self.doc_obj = ajpdf_main().parse(sys.argv[1])
        self.title: str = self.doc_obj.real_title
        self.push_screen(TableScreen(self.doc_obj))


if __name__ == "__main__":
    from datetime import datetime

    logging.basicConfig(
        level=logging.WARNING,
        datefmt="%Y-%m-%d %H.%M.%S",
        format="%(asctime)s %(levelname)s %(message)s",
        filename=f'./log/{datetime.now().strftime("%Y.%m.%d")}',
    )
    app = CongressWatch()
    app.run()
