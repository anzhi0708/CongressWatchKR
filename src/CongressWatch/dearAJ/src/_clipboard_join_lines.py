import pyperclip as clipboard
import time


print(f"\033[3m{__file__}\033[0m")

cache: str = ""

while True:
    string_current = clipboard.paste()
    if string_current != "" and string_current != cache:
        new_string = string_current.replace("\n", "")
        cache = new_string
        clipboard.copy(new_string)
        current_time = time.localtime()
        current_time = (
            f"{current_time.tm_hour}:{current_time.tm_min}:{current_time.tm_sec}"
        )
        print(f'[{current_time}]\tGot string: "\033[3;32m{new_string}\033[0m"')
