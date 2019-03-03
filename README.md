# Filecrawl

A simple crawler based on [requests](https://github.com/requests/requests/) obtaining all available files from the campus management platform Studip.

## Requirements

+ [Python 3.4+](https://www.python.org)
+ Package: [requests](https://github.com/requests/requests/)

## Installation

In order for studipcrawl to work you need to install requests, the documentation can be found [here](http://docs.python-requests.org/en/master/user/install/#install).

```
pip3 install requests
```

## Usage

Edit the path to the corresponding folder on your machine and your login data from your Studip-Account.

```python
### ----------------------------SETUP---------------------------- ###
# Only change this part of the program
# Change this to your username used in Studip
username = "USERNAME"
# Change this to your password used in Studip
password = "PASSWORD"
# Change this to the destination path where the files should be
# downloaded. The r"" has to stay in order to work!
dst_folder = r"path\to\folder"
### ------------------------------------------------------------- ###
```

Simply run the script with ``` python3 studipcrawl.py ```.

## Credits & Licence

Under [MIT LICENCE](https://github.com/Xceron/studipcrawl/blob/master/LICENSE).
