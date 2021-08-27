[**Docker Instructions**](#docker)  
[Endorser](#endorser)  
[Author](#author)  
[**Alternate Setup Instructions**](#alternate)  
[Linux](#linux)  
[Windows](#windows)  
[Mac](#mac)  
[**Running Instructions**](#running)

# Author-Endorser-Wizards
Python program to walk through the author and endorser workflow to create schemas and cred defs.

## Docker Instructions <a id="docker"></a>

### Running the Endorser <a id="endorser"></a>
Once you have cloned the repo,

1. `docker build -t endorser-wizard -f endorser-docker-file .` (The dot is important as it signifies the current directory.)
2. `docker run --rm -it -v \<Path to git repository\>/author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>/wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>/pool:/root/.indy_client/pool:z endorser-wizard`
    * If on windows run: `docker run --rm -it -v \<Path to git repository\>\author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>\wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>\pool:/root/.indy_client/pool:z endorser-wizard\`
### Running the Author <a id="author"></a>
1. `docker build -t author-wizard -f author-docker-file .` (The dot is important as it signifies the current directory.)
2. `docker run --rm -it -v \<Path to git repository\>/author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>/wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>/pool:/root/.indy_client/pool:z author-wizard`
   * If on windows run: `docker run --rm -it -v \<Path to git repository\>\author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>\wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>\pool:/root/.indy_client/pool:z author-wizard`

## Alternate Setup Instructions <a id="alternate"></a>
If you're not using Docker, here are the individual setup and running instructions you can follow to run the author and endorser wizards.

### Linux 18.04 <a id="linux"></a>

On a clean install of Ubuntu 18.04, the following works to install and run the Appropriate Wizard.  Please adjust if appropriate for your environment.
#### Install libindy
1. `sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88`
2. `sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"`
3. `sudo apt-get update`
4. `sudo apt-get upgrade`
5. `sudo apt-get install -y libindy`

#### Install Python
1. `sudo apt install python3.8 -y`
2. `sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1`
3. `sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2`
4. `sudo apt install python3-pip git`
5. `pip3 install --upgrade pip`
6. `pip3 install aiohttp base58 indy Python3-indy asyncio`


### Windows 10 <a id="windows"></a>
1. Install Python 3.9
2. Download latest from https://repo.sovrin.org/windows/libindy/stable
3. Extract the libindy folder to your desired directory
4. Run in Command Prompt, `set LIBINDY_DIR=\<Full path to the libindy folder\>`
5. `set PYTHONPATH=C:\Python39\Lib\site-packages`
6. `set PATH=C:\Python39`
7. `pip3 install asyncio aiohttp indy base58 Python3-indy`


### MacOs <a id="mac"></a>
Instructions are coming soon.

## Running Instructions <a id="running"></a>
#### Navigate to the author-endorser-wizards directory:
1. `mk dir git` (Skip this step if you've already created a git directory)
2. `cd git`
3. `git clone https://github.com/Indicio-tech/author-endorser-wizards.git`
4. `cd author-endorser-wizards`

#### If you are the Author run:
1. `python3 AuthorWizard.py`
#### If you are the Endorser run:
1. `python3 EndorserWizard.py`
