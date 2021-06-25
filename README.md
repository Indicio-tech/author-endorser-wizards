# Author-Endorser-Wizards
Python program to walk through the author and endorser workflow to create schemas and cred defs

## Setup Instructions

### Linux 18.04

#### On a clean install of Ubuntu 18.04 the following works to install and run the Appropriate Wizard.  Please adjust if appropriate for your environment.
- sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
- sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"
- sudo apt-get update
- sudo apt-get upgrade
- sudo apt-get install -y libindy
- sudo apt install python3.8 -y
- sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
- sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
- sudo apt install python3-pip git
- pip3 install --upgrade pip
- pip3 install aiohttp base58 indy Python3-indy asyncio
- mkdir git
- cd git
- git clone https://github.com/Indicio-tech/author-endorser-wizards.git
- cd author-endorser-wizards
- If you are the Author run:
- python3 AuthorWizard.py
- If you are the Endorser run:
- python3 EndorserWizard.py

### Windows 10

#### Windows Setup Instructions
- set LIBINDY_DIR= path to indy.dll

### MacOs

#### Apple Setup Instructions
