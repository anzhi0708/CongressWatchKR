from colorama import Fore, Back, Style


class Message:
    """Friendly console output"""

    def __init__(self, enabled=False):
        self.enabled = enabled

    def _red(self, text: str):
        return Fore.RED + text + Fore.RESET

    def _green(self, text: str):
        return Fore.GREEN + text + Fore.RESET

    def _yellow(self, text: str):
        return Fore.YELLOW + text + Fore.RESET

    def _grey(self, text: str):
        return Fore.LIGHTBLACK_EX + text + Fore.RESET

    def _bg_red(self, text: str):
        return Fore.BLACK + Back.RED + text + Fore.RESET + Back.RESET

    def _bg_green(self, text: str):
        return Fore.BLACK + Back.GREEN + text + Fore.RESET + Back.RESET

    def _bg_yellow(self, text: str):
        return Fore.BLACK + Back.YELLOW + text + Fore.RESET + Back.RESET

    def log(self, text: str, end="\n", prefix="[+]"):
        if self.enabled:
            print(self._bg_green(prefix), self._green(text), end=end)

    def warn(self, text: str, end="\n", prefix="[?]"):
        if self.enabled:
            print(self._bg_yellow(prefix), self._yellow(text), end=end)

    def error(self, text: str, end="\n", prefix="[!]"):
        if self.enabled:
            print(self._bg_red(prefix), self._red(text), end=end)

    def faded(self, text: str, end="\n", prefix=""):
        if self.enabled:
            print(
                (self._grey(prefix) + " " if prefix else "") + self._grey(text), end=end
            )

    def auto_skipped(self, text: str):
        if self.enabled:
            print(Fore.YELLOW + "···" + Fore.RESET + " ", end="")
            self.warn(text=text, prefix="")

    def highlight(self, text: str):
        if self.enabled:
            print(self._bg_red(text))
