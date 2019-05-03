# Filecrawl

A simple crawler obtaining all available files from the campus management platforms
Studip and moodle for University Trier

##Disclaimer
This version only works for the University Trier and Studip 4.
Use the [Studip RESTAPI](https://docs.studip.de/develop/Entwickler/RESTAPI)
if possible as Crawler are forbidden by many universities. 

There are other open Source Clients supporting the API, e.g. [studip-fuse](https://github.com/N-Coder/studip-fuse)
or [STUD.IP-FileSync](https://github.com/rockihack/Stud.IP-FileSync).

## Installation

###Windows

1. Download [Python 3.4+](https://www.python.org)
2. Download filecrawl and unzip it.
3. open cmd
4. ``` cd /path/to/filecrawl/ ```
5. ```python -m pip install -r requirements.txt```

###MacOS and Linux
1. Download [Python 3.4+](https://www.python.org)
2. Download filecrawl and unzip it.
3. open terminal
4. ``` cd /path/to/filecrawl/ ```
5. ```pip3 install -r requirements.txt```
    + When you use a Linux Distro which isn't supported by the ```keyrings``` backend (e.g. Raspbian)
you also need to run ```pip3 install keyrings.alt```
## Usage

###Windows
Simply run the script with ``` python filecrawl.py ``` when you are in the filecrawl folder.
It will guide you through the setup when you run the script for the first time.

###MacOS and Linux
Simply run the script with ``` python3 filecrawl.py ``` when you are in the filecrawl folder.
It will guide you through the setup when you run the script for the first time.
+ You may get an Error when using ```help``` in the Setup on macOS stating that ```FIFinderSyncExtensionHost``` is
implemented in two paths - just ignore this. This also leads to a Finder window which is stuck
as long as the script is running.

####Crontabs
When you want to run filecrawl as a crontab, you have to have root privileges or run everything with ```sudo```.
Also, you may have to change the path where the config will be saved in
[filecrawl/L233](https://github.com/Xceron/Filecrawl/blob/1169aa817fd9e20a54c7f6fc2c406fc2e5fdc6c6/filecrawl.py#L233),
[config_handling/L89](https://github.com/Xceron/Filecrawl/blob/04e178dad31a28cdeb0dd1002fec85b226681113/filecrawl/config_handling.py#L89)
and [config_handling/L100](https://github.com/Xceron/Filecrawl/blob/04e178dad31a28cdeb0dd1002fec85b226681113/filecrawl/config_handling.py#L100)
as the root user has no /User/ folder where the config will be stored.


## Credits & Licence

Under [MIT LICENCE](https://github.com/Xceron/studipcrawl/blob/master/LICENSE).
