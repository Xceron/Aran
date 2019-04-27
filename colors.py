# coding: utf-8
import platform
from colorama import init, Fore

init()


class Color:
    OK = Fore.BLUE + '[~] ' + Fore.RESET
    WARNING = Fore.YELLOW + "[!] " + Fore.RESET
    if platform.system() == "Windows":  # Windows cmd isn't able to output unicode characters correctly
        ERROR = Fore.RED + "[X] " + Fore.RESET
        SUCCESS = Fore.GREEN + "[S] " + Fore.RESET
    else:
        ERROR = Fore.RED + "[✗] " + Fore.RESET
        SUCCESS = Fore.GREEN + "[✓] " + Fore.RESET

