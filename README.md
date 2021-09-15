# Author-Endorser-Wizards
This open source project contains wizards that guide the user through the Author-Endorser workflow to create schemas and credential definitions. 

The easiest way to setup the author and endorser wizards is to use Docker. However, if that is not available to you, instructions for Linux, Windows 10, and Mac are also provided. 

[**Docker Instructions**](#docker)  
[Author](#author)  
[Endorser](#endorser)  
[**Alternate Setup Instructions**](#alternate)  
[Linux](#linux)  
[Windows](#windows)  
[Mac](#mac)  
[**Running Instructions**](#running)

---

## Docker Setup Instructions <a id="docker"></a>
Once you have cloned the repo, do the following:

### Running the Author Wizard <a id="author"></a>
1. `docker build -t author-wizard -f author-docker-file .` (The dot is important as it signifies the current directory.)
2. `docker run --rm -it -v \<Path to git repository\>/author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>/wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>/pool:/root/.indy_client/pool:z author-wizard`
   * If on windows run: `docker run --rm -it -v \<Path to git repository\>\author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>\wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>\pool:/root/.indy_client/pool:z author-wizard`

### Running the Endorser Wizard<a id="endorser"></a>

1. `docker build -t endorser-wizard -f endorser-docker-file .` (The dot is important as it signifies the current directory.)
2. `docker run --rm -it -v \<Path to git repository\>/author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>/wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>/pool:/root/.indy_client/pool:z endorser-wizard`
    * If on windows run: `docker run --rm -it -v \<Path to git repository\>\author-endorser-wizards:/root/author-endorser-wizards:z -v \<Path to .indy_client\>\wallet:/root/.indy_client/wallet:z -v \<Path to .indy_client\>\pool:/root/.indy_client/pool:z endorser-wizard\`

---

## Alternate Setup Instructions <a id="alternate"></a>
If you're not using Docker, here are the individual setup and running instructions you can follow to run the author and endorser wizards.

### Linux 18.04 <a id="linux"></a>

On a clean install of Ubuntu 18.04, the following works to install and run the Appropriate Wizard.  Please adjust as needed for your environment.
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

Skip to [Running Instructions](#running).


### Windows 10 <a id="windows"></a>
1. Install Python 3.9
2. Download latest from https://repo.sovrin.org/windows/libindy/stable
3. Extract the libindy folder to your desired directory
4. Run in Command Prompt: `set LIBINDY_DIR=\<Full path to the libindy folder\>`
5. `set PYTHONPATH=C:\Python39\Lib\site-packages`
6. `set PATH=C:\Python39`
7. `pip3 install asyncio aiohttp indy base58 Python3-indy`
8. Skip to [Running Instructions](#running).


### MacOs <a id="mac"></a>
On a Mac OSX workstation/laptop the following works to install and run the appropriate Wizard.  Please adjust as needed for your environment.

1. Build libindy  
Since there is no public build of libindy, you will need to build it yourself with the following set of instructions:
    1. Run the following commands in a terminal:
        1. `cd ~`
        2. `mkdir github`
        3. `cd github`
        4. `git clone https://github.com/hyperledger/indy-sdk.git` (You might need `xcode-select --install` if an error occurs or select “install” if it offers xcode tools)
        5. `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
        6. `curl https://sh.rustup.rs -sSf | sh`
	        1. Follow the on-screen instructions to install rust
        7. `brew install pkg-config libsodium automake autoconf cmake openssl zeromq zmq`
    2. NOTE: the _openssl_ path needs to match what you currently have on your system
        1. Run `ls /usr/local/Cellar/openssl/`
        2. Note the name of the directory shown 
        3. Use this directory in place of the one listed below in your _.profile_ file 
    3. Add the following lines to your _~/.profile_ file (making the correction shown in the previous step if needed)  
`export PATH="$HOME/.cargo/bin:$PATH:~/github/indy-sdk/libindy/target/debug:~/github/indy-sdk/cli/target/debug"`  
`export PKG_CONFIG_ALLOW_CROSS=1`  
`export CARGO_INCREMENTAL=1`  
`export RUST_LOG=indy=trace`  
`export RUST_TEST_THREADS=1`  
`export OPENSSL_DIR=/usr/local/Cellar/openssl/1.0.2p` #use your path  
`export LIBRARY_PATH=~/github/indy-sdk/libindy/target/debug/`  
`export LIBINDY_DIR=~/github/indy-sdk/libindy/target/debug/`
    4. Run the following commands from your terminal to build libindy and create a link to it:
        1. `source ~/.profile`
        2. `cd ~/github/indy-sdk/libindy`
        3. `cargo build`
        4. Use your own path in the following command: `ln -s /Users/username/github/indy-sdk/libindy/target/debug/*.dylib* /usr/local/lib`
2. Python 3.8 (or greater)  
If you do not already have it installed, install Python 3.8 or greater:
    1. `python3 --version`  (to check your version)
    2. There are multiple ways to do this for a Mac. Here is a link to one of the options: <https://installpython3.com/mac/>
3. `pip3 install aiohttp base58 indy Python3-indy asyncio`
4. `cd ~/github`
5. `git clone https://github.com/Indicio-tech/author-endorser-wizards.git`
6. `cd author-endorser-wizards`
7. If you are the Author run: `python3 AuthorWizard.py`
8. If you are the Endorser run: `python3 EndorserWizard.py`

---


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
