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
- Install Python 3.9
- download latest from https://repo.sovrin.org/windows/libindy/stable
- extract the libindy folder to your desired directory
- Run in command prompt, set LIBINDY_DIR=\<Full path to the libindy folder\>
- set PYTHONPATH=C:\Python39\Lib\site-packages
- set PATH=C:\Python39
- pip3 install asyncio aiohttp indy base58 Python3-indy


### MacOs

#### Apple Setup Instructions

## Running Instructions

### Running using Docker

#### Endorser

- docker build -t endorser-wizard -f endorser-docker-file .
- docker run --rm -it -v <Path to git repository>/author-endorser-wizards:/root/author-endorser-wizards:z -v <Path to .indy_client>/wallet:/.indy_client/wallet:z -v <Path to .indy_client>/pool:/.indy_client/pool:z endorser-wizard 
-- \(If on windows run: docker run --rm -it -v <Path to git repository>\author-endorser-wizards:/root/author-endorser-wizards:z -v <Path to .indy_client>\wallet:/.indy_client/wallet:z -v <Path to .indy_client>\pool:/.indy_client/pool:z endorser-wizard\)
#### Author
- docker build -t author-wizard -f author-docker-file .
- docker run --rm -it -v <Path to git repository>/author-endorser-wizards:/root/author-endorser-wizards:z -v <Path to .indy_client>/wallet:/.indy_client/wallet:z -v <Path to .indy_client>/pool:/.indy_client/pool:z author-wizard
-- \(If on windows run: docker run --rm -it -v <Path to git repository>\author-endorser-wizards:/root/author-endorser-wizards:z -v <Path to .indy_client>\wallet:/.indy_client/wallet:z -v <Path to .indy_client>\pool:/.indy_client/pool:z author-wizard
