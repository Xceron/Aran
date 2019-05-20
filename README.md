# Filecrawl

A simple crawler obtaining all available files from the campus management platforms
Studip and moodle for University Trier

## Disclaimer
This version works only for the University Trier and Studip 4.
Use the [Studip RESTAPI](https://docs.studip.de/develop/Entwickler/RESTAPI)
if possible as Crawlers are forbidden by many universities. 

There are other open Source Clients supporting the API, e.g. [studip-fuse](https://github.com/N-Coder/studip-fuse)
or [STUD.IP-FileSync](https://github.com/rockihack/Stud.IP-FileSync).

## Installation

### Windows

1. Download [Python 3.4+](https://www.python.org)
2. Download filecrawl and unzip it.
3. open cmd
4. ``` cd /path/to/filecrawl/ ```
5. ```python -m pip install -r requirements.txt```

### MacOS and Linux
1. Download [Python 3.4+](https://www.python.org)
2. Download filecrawl and unzip it.
3. open terminal
4. ``` cd /path/to/filecrawl/ ```
5. ```pip3 install -r requirements.txt```
    + When you use a Linux Distro which isn't supported by the ```keyrings``` backend (e.g. Raspbian)
you also need to run ```pip3 install keyrings.alt```
## Usage

### Windows
Simply run the script with ``` python crawler.py ``` when you are in the filecrawl folder.
It will guide you through the setup when you run the script for the first time.

### MacOS and Linux
Simply run the script with ``` python3 crawler.py ``` when you are in the filecrawl folder.
It will guide you through the setup when you run the script for the first time.
+ You may get an Error when using ```help``` in the Setup on macOS stating that ```FIFinderSyncExtensionHost``` is
implemented in two paths - just ignore this. This also leads to a Finder window which is stuck
as long as the script is running.


## Credits & Licence

Under [MIT LICENCE](https://github.com/Xceron/studipcrawl/blob/master/LICENSE).
