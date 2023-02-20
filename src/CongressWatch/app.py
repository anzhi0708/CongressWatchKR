#!/usr/bin/env python3


from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label, Footer, Header
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from os import get_terminal_size
from fitz import Document


class SpeechContentScreen(Screen):
    """Pop up window that shows certain MP's speech"""

    BINDINGS = [Binding("q,escape", "pop_screen", "back")]

    def __init__(self, key, doc_obj) -> None:
        super().__init__()
        self.key: str = key
        self.doc_obj: Document = doc_obj
        self.buffer: str = ""

    def get_terminal_size(self):
        return get_terminal_size()

    def compose(self) -> ComposeResult:
        yield Label(self.key)

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

    def __init__(self, doc_obj):
        super().__init__()
        self.doc_obj: Document = doc_obj

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        self.table: DataTable = DataTable(id="mp_table", zebra_stripes=True)
        self.table.add_column("Index")
        self.table.add_column("Name & Title")
        self.table.add_column("[b]Name[/b]", width=17)
        self.table.add_column("Job Title")

        for index, name in enumerate(self.doc_obj.result):
            job_title_and_name: list[str] = name.split(" ")
            if "위원" in job_title_and_name:
                _job = "위원"
                _name = name.replace(_job, "").replace("◯", "").strip()
            else:
                for element in job_title_and_name:
                    if len(element) > 3:
                        _job = element.replace("◯", "")
                        _name = name.replace(_job, "").replace("◯", "").strip()
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

        _cell_content = re.sub(r"\[.*\]", "", _cell)
        self.current_dict_key: str = "◯" + _cell_content
        self.app.push_screen(SpeechContentScreen(self.current_dict_key, self.doc_obj))


class CongressWatch(App[None]):
    CSS_PATH = "style.css"

    def __init__(self):
        super().__init__()
        _COLS, _ROWS = get_terminal_size()
        self.cols = _COLS
        self.rows = _ROWS

    def on_mount(self):
        from ajpdf import Main as ajpdf_main
        import sys

        self.doc_obj = ajpdf_main().parse(sys.argv[1])
        self.title = self.doc_obj.real_title
        self.push_screen(TableScreen(self.doc_obj))


if __name__ == "__main__":
    app = CongressWatch()
    app.run()
