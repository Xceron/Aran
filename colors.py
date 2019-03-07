# simple class with ANSI color codes


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END: str = '\033[0m'
    WHITE = '\033[37m'
    OK = BLUE + '[~] ' + END
    WARNING = YELLOW + "[!] " + END
    ERROR = RED + "[✗] " + END
    SUCCESS = GREEN + "[✓] " + END
