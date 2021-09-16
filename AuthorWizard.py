import json
from posixpath import join
import asyncio
import os
import logging
from logging import ERROR, WARNING, INFO, DEBUG, CRITICAL
import urllib
import datetime
import secrets
import string
from aiohttp import web
from ctypes import cdll
from indy import ledger, did, wallet, pool, anoncreds
from indy.error import ErrorCode, IndyError, PoolLedgerConfigAlreadyExistsError
import platform
import re



os.system("clear")
if platform.system() == "Windows":
    os.add_dll_directory(os.getenv('LIBINDY_DIR'))

role = "Author"
walletHandle = 0

def downloadGenesis(networkUrl):
    try:
        urllib.request.urlretrieve(networkUrl, "genesisFile")
    except:
        print("\n")
        print("Error downloading genesis file")
        print("\n")

async def createPool(network):

    if "indicioTestNet" == network:
        network_genesis_url="https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_testnet_genesis"
    elif "indicioDemoNet" == network:
        network_genesis_url="https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_demonet_genesis"
    elif "indicioMainNet" == network:
        network_genesis_url="https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_mainnet_genesis"
    else: network = "indicioTestNet"

    downloadGenesis(network_genesis_url)


    config = {
            "genesis_txn": "genesisFile"
    }
    configJson = json.dumps(config)

    try:
        await pool.create_pool_ledger_config(network, configJson)
    except PoolLedgerConfigAlreadyExistsError:
        print("The Network selected already exsists")
    except:
        print("\n")
        print("Error Adding Network")
        print("\n")
    
    return network

async def openPool(network):  
    poolList = await pool.list_pools()
    if network == "Network name not found":
        return "Network name not found"
    for i in range(len(poolList)):
        if network == str(i+1):
            network = list(poolList[i].values())
    network = str(network).replace('[\'', '')
    network = network.replace('\']', '')

    pool_handle = 0
    try:
        print("connecting to the network '" + network + "'...")
        pool_handle = await pool.open_pool_ledger(config_name=network, config=None)
    except:
        print("\n")
        print("Error connecting to network '" + network +"'")
        print("\n")
    else:
        print("...done")
        print()
    return pool_handle
 
async def listPools(role):
    print("\nConnect to a Network\n--------------------\n")
    try:
        poolList = await pool.list_pools()
    except:
        print("\n")
        print("Error creating list of networks")
        print("\n")

    print(role + "'s Networks:")
    for i in range(len(poolList)):
        print("   " + str(i + 1) + ":", *list(poolList[i].values()))
    print("   " + str(len(poolList)+1) + ": Add New Network")
    print()

    return poolList
 
async def createWallet():
    walletName = "wizard_wallet" # input("What would you like to name your wallet?: ")
    #seed = input("Insert your seed here. If you want a random seed, insert nothing: ")
    walletKey = "wizard_wallet" #wallet.generate_wallet_key(seed)
 
    walletID = {
        "id": walletName
    }
 
    walletKey = {
        "key": walletKey
    }
 
    walletKeyJson = json.dumps(walletKey)
    walletIDJson = json.dumps(walletID)
 
   #create wallet code
    print("Creating new wallet '" + walletName + "'...")
 
    try:
        await wallet.create_wallet(walletIDJson, walletKeyJson)
    except:
        print("\n")
        print("Error creating wallet '" + walletName + "'")
        print("\n")
 
    else:
        print("...done")

    return walletName

def listWallets():
    print("\nWallet Selection\n----------------\n")
    print("Below is a list of the wallets you have available.  Choose the wallet with the Author DID you are going to use to issue credentials.")
    print("If you don't have an Author DID, you can choose 'Create new wallet'.")
    print()
    userDir = os.path.expanduser("~")
    dirExists = True
    filePath = "/.indy_client/wallet/"
    if platform.system() == "Windows":
        filePath = "\.indy_client\wallet\\"
    try:
        walletList = os.listdir(userDir + filePath)
    except FileNotFoundError:
        dirExists = False
        print("You have no wallets yet")
        print("\n")
    except:
        print("\n")
        print("Error getting the list of wallets")
        print("\n")
    else:
        print("Your Wallets:")
        for i in range(len(walletList)):
            print(' ' + str(i+1) + ":", walletList[i])
        print(' ' + str(len(walletList) + 1) + ": Create New Wallet")
   
    return walletList
 
async def openWallet():
    walletList = listWallets()
    walletKey = ""
    print()
 
    walletIndex = input("Select the wallet you want to use to issue credentials: ")
    print()
    if walletIndex == len(walletList):
        walletName = createWallet()
    else:
        walletName = walletList[int(walletIndex)-1]
        walletKey = input("Enter your Wallet Key (password): ")
        print()

    userDir = os.path.expanduser("~")
    dirExists = True
    filePath = "/.indy_client/wallet/"
    if platform.system() == "Windows":
        filePath = "\.indy_client\wallet\\"
    try:
        walletList = os.listdir(userDir + filePath)
    except FileNotFoundError:
        dirExists = False
    except:
        print("\n")
        print("Error getting the list of wallets")
        print("\n")

    
    walletNameConfig = {
        "id": walletName
    }
    walletKeyConfig = {
        "key": walletKey
    }
    walletNameConfig = json.dumps(walletNameConfig)
    walletKeyConfig = json.dumps(walletKeyConfig)
    print("opening wallet '" + walletName + "'...")

    try:
        global walletHandle
        walletHandle = await wallet.open_wallet(walletNameConfig, walletKeyConfig)
    except:
        print("\n")
        print("Error opening wallet '" + walletName + "'")
        print("\n")
    else:
        print("...done")
        print()

    return
    
async def authorWizard(author):
    poolHandle = None
    print("\nAuthor Wizard\n-------------\n")
    print("To begin, you must select or add the network that you would like to use for issuing credentials. If you select \"Add New Network\" you will be given a choice of which network to add to your list of choices, then that network will be used during the rest of this session.")
    print()
    poolList = await listPools(role)
    userPool = input("Select the network you want to use("+str(len(poolList)+1)+"): ")
    print("\n")
    if userPool == str(len(poolList) + 1) or userPool == '':
       network = listNetworks()
       
       network = await createPool(network)
       poolHandle = await openPool(network)
    else:
       poolHandle = await openPool(userPool)
  
    #print("Below is a list of wallets:")
    await openWallet()
    
    authorDid, authorVerKey = await listDids(role, walletHandle)
   #listDids()
    #authorDid = input("Choose the index number of the did you want to use: ")
    #if authorDid == "last":
       #authorDidSeed = input("Enter your super secret seed for your new did: ")
       #authorDid = createDidFromSeed(authorDidSeed)
   #didUse(authorDid)
    
    tAA = await transactionAuthorAgreement(poolHandle, walletHandle, authorDid)

    print("\n")
    schemaID = ''

    schemaChoice = input("""The first step to creating a credential is to create a new schema or select an existing one.  A schema contains a list of attributes or fields that are to be associated with the credential that you will be issuing.

 1. Create a new schema 
 2. Use an existing one

Select an option(1/2): """)
    while True:
        if schemaChoice == '1':
            print('\n')
            schemaTxn = await createSchema(authorDid)
            await signSendTxn(authorDid, authorVerKey, schemaTxn, tAA, poolHandle)
            break
        elif schemaChoice == '2':
            break
        else:
            print("Invalid input, please input 1 or 2")
            print()
            schemaChoice = input("""
 1. Create a new schema 
 2. Use an existing one

Select an option(1/2): """)

    credDefTxn = await createCredDef(authorDid, poolHandle)

    await signSendTxn(authorDid, authorVerKey, credDefTxn, tAA, poolHandle)

    print()

    choice = input("The Transaction Author Wizard has finished.  Press 'q' to quit, or press enter to go to the main menu: ")
    if choice == 'q' or choice == 'Q':
        author = 0 
    return poolHandle, tAA, author

def displayMenu():
    print("Menu\n----\n")
    print("Options")
    print("  0: Author Wizard")
    print("  1: Create Schema")
    print("  2: Create Credential Definition")
    print("  3: Sign Transaction and Send to Ledger")
    print("  4: Add Network")
    print("  5: Connect to a Network")
    print("  6: Create Wallet")
    print("  7: Open Wallet")
    print("  8: Create DID")
    print("  9: Use DID")
    print(" 10: Display Menu")
    print("  q: Quit")

def listNetworks():
    print("Indicio Networks\n")
    print(" 1: Indicio MainNet")
    print(" 2: Indicio DemoNet")
    print(" 3: Indicio TestNet\n")
 
    network = input("Select a network to add(3): ")
    print("\n")
    if network == '1':
        network = "indicioMainNet"
    elif network == '2':
        network = "indicioDemoNet"
    else:
        network = "indicioTestNet"
    
    return network
 
async def createDid(role, walletHandle):
    valid = False
    authorDid = ''

    
    print("A 'seed' is required for you to be able to add your "+role+" DID to any other wallet. This seed should be stored in a safe place.")
    print()
    while not valid:
        seed = input("Please enter an alpha-numeric 32 character seed, or hit 'enter' to have one created for you: ")
        
        print()
        if seed == '':
            seed = seed.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))
            print(role+" Seed:", seed)
            valid = True
        elif len(seed) < 32:
            print("\nThe seed you entered is too short\n")
            valid = False
            continue
        elif len(seed) > 32:
            print("\nThe seed you entered is too long\n")
            valid = False
            continue
        else:
            valid = True
            break
        for i in range(len(seed)):
            if not seed[i].isalnum():
                print("\nThe seed you entered is invalid because it contains an invald character.\n") 
                valid = False
                break
        
    
    
    seedJson = {
        "seed": seed
    }
    
    seedJson = json.dumps(seedJson)
    try:
        authorDid = await did.create_and_store_my_did(walletHandle, seedJson)
    except:
        print("\n")
        print("Error creating DID")
        print("\n")
        raise
    else:
        print(role+" DID:", authorDid[0])
        print(role+" VerKey:", authorDid[1])
        print()
        input("After you have saved your Seed in a safe place and recorded your "+role+" DID and Verkey for later use, please hit enter to continue.")
        print()

    
    didMetadata = role + " DID created by wizard"
    print()
    try:
        await did.set_did_metadata(walletHandle, authorDid[0], didMetadata)
    except IndyError:
        print("\n")
        print("Error setting metadata")
        print("\n")
        raise
    except:
        print("system error\n")
        raise

    return authorDid

async def listDids(role, walletHandle):
    didListJson = ''
    print("\n"+role+"'s DIDs\n------------\n")
    print("Adding issuer transactions to the ledger requires you to create and maintain an \""+role+" DID\".  Select your "+role+" DID from the following list, or create a new one and save the seed in a safe place. ")
    print()
    try:
        didListJson = await did.list_my_dids_with_meta(walletHandle)
    except:
        print("\n")
        print("Error getting the list of dids from current wallet.  Please make sure you have a wallet open.")
        print("\n")

    
    didList = json.loads(didListJson)

    print(" " + "Index |", "         DID         ", " | Metadata")
    print("-------+------------------------+----------")

    for i in range(len(didList)):
        if len(didList[i]["did"]) == 22 and i < 9:
            print("     " + str(i + 1) + " |", didList[i]["did"], '|', didList[i]["metadata"])
        elif len(didList[i]["did"]) == 22 and i >= 9:
            print("    " + str(i + 1) + " |", didList[i]["did"], '|', didList[i]["metadata"])
        elif len(didList[i]["did"]) == 21 and i < 9:
            print("     " + str(i + 1) + " |", didList[i]["did"], ' |', didList[i]["metadata"])
        else:
            print("    " + str(i + 1) + " |", didList[i]["did"], " |", didList[i]["metadata"])


    if len(didList) > 9:
        print("    " + str(len(didList)+1) + " |", "Create New DID        ", '|', "Create a new DID to use")
    else:
        print("     " + str(len(didList)+1) + " |", "Create New DID        ", '|', "Create a new DID to use")
    print()
    index = input("Select an "+role+" DID (" + str(len(didList)+1) + "): ")
    print()
    
    if index == '':
        authorDid, authorVerKey = await createDid(role, walletHandle)
    elif index == str(len(didList)+1):
        authorDid, authorVerKey = await createDid(role, walletHandle)
    else:
        index = int(index) - 1
        authorDid = didList[index]["did"]
        authorVerKey = didList[index]["verkey"]
        

    return authorDid, authorVerKey

async def signSendTxn(authorDid, authorVerKey, authorsTxn, tAA, poolHandle):
    tAA = tAA["result"]
# note: check for endorser using get nym
    utctimestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    slash = '/'
    if platform.system() == "windows":
        slash ='\\'
    fileName = "authors-txn"
    filePath = os.getcwd() + slash + fileName
    signedFileName = "authors-signed-txn"
    signedFilePath = os.getcwd() + slash + signedFileName

    try:
        authorsTxn = await ledger.append_txn_author_agreement_acceptance_to_request(authorsTxn, tAA["data"]["text"], tAA["data"]["version"], None, 'for_session', utctimestamp)
    except:
        print("\n")
        print("Error appending the TAA")
        print("\n")
        
    endorserDid = input("An Endorser must now sign your transaction before you can write it to the network.  Please enter the Endorser DID of your chosen Endorser: ")
    try:
        authorsTxn = await ledger.append_request_endorser(authorsTxn, endorserDid)
    except:
        print("\n")
        print("Error appending the endorser")
        print("\n")
    try:
        authorsTxn = await ledger.sign_request(walletHandle, authorDid, authorsTxn)
    except:
        print("\n")
        print("Error with author signing transaction")
        print("\n")

    authorsTxnWithDid = {
        "txn": json.loads(authorsTxn),
        "author_did": authorDid,
        "author_ver_key": authorVerKey
    }
    authorsTxnWithDid = json.dumps(authorsTxnWithDid)
    
    print("We have completed the first phase of preparing your transaction!\n  The transaction will be in a file named '" + fileName + "' in the same directory that you started this program from.\n  ")
    print()
    if os.path.exists(fileName):
        input("A file named '"+fileName+"""' already exists and will be deleted.
Press Enter to continue\n""")
        os.remove(fileName)
    if os.path.exists(signedFileName):
        os.remove(signedFileName)

    
    try:
        txnFile = open(filePath, "x")
    except:
        print("Replacing the previous version of " + fileName + "...")
        txnFile = open(filePath, "w")
    else: 
        print("\nWriting", fileName + "...")

    txnFile.write(authorsTxnWithDid)
    txnFile.close()
    print("...done\n")
    print()
    input("Please send this file to your endorser so that they can sign and return it to you, then press enter to continue.")

    input("""The Endorser will have sent a file named '"""+signedFileName+"""'.
Copy that file to the directory that you started the program from then press enter.""")
    error = True
    while error:
        try:
            authorsSignedTxnFile = open(signedFileName)
            error = False
        except FileNotFoundError:
            print("The file does not exist, Please ensure that the endorser sent you the correct file and it is in the directory you ran the program from.\n")
            print("File name:", signedFileName, '\n')
            input("Press enter when completed")
            error = True
    authorsSignedTxn = authorsSignedTxnFile.read()
    authorsSignedTxnFile.close()

    error = False
    try:
        await ledger.submit_request(poolHandle, authorsSignedTxn)
    except IndyError as CommonInvalidStructure:
        print("ERROR: Could not write txn to network", CommonInvalidStructure)
        print()
        error = True
    except ErrorCode.LedgerInvalidTransaction:
        print("ERROR: Could not write txn to network")
        print()
        error = True
    if not error:
        print("\n")
        print("Successfully written to the network.")
    return

async def createSchema(authorDid):
    print("Schema Creation\n---------------\n")
    validVer = False
    hasDot = False

    print("Schema creation requires you to select a name, a version number, and the attributes you would like to have for the schema. The 'Schema Name' is your choice but should be descriptive enough for you to remember its purpose.\n")
    
    name = input("Enter Schema Name: ")
    print("\nA schema version must contain either 1 or 2 '.'s, and must have at least one number before and after each '.'\nExamples: 1.0, 35.2.1, 0.12345")
    print()
    while not validVer:
        version = str(input("Enter Schema Version (1.0): "))
    #    for i in range(len(version)-2):
     #       if version[i+1] == '.':
    #            hasDot = True
    #        if (version[i+1].isnumeric() or version[i+1] == '.') and (version[i].isnumeric() or version[i] == '.') and (version[i+2].isnumeric() or version[i+2] == '.'):
    #            validVer = True
    #        else:
    #            validVer = False
    #            print("The version you entered is invalid.(not numeric)\n")
    #            break
#
        if version == '':
            version = '1.0'
    #        validVer = True
    #    elif version[0] == '.' or version[len(version)-1] == '.':
    #        validVer = False
    #        print("The version you entered is invalid.(invalid format)\n")
    #    elif len(version) <= 2:
    #        print("The version you entered is invalid.(too short)\n")
    #        validVer = False
    #    elif not validVer:
    #        continue
    #    elif not hasDot:
    #        print("The version you entered is invalid.(no dot)\n")
    #        validVer = False            
        validVer = re.match(r'^[0-9]+(?:\.[0-9]+){1,2}$', version)
        if not validVer:
            print("\nThe version you entered is invalid. A version must be in the form #.# or #.#.#\n") 

    attrs = []

    add = True
    i = 0
    print("\nSchema attributes must be numbers or lowercase letters without spaces or special characters. (underscores are ok)")
    print("Enter the schema's attributes names one at a time ('done' to stop, 'restart' to start over).\n")
    while add:
        attrs.append(input("Attribute "+ str(i+1) +": "))
        #valid = True
        #for j in range(len(attrs[i])):
        #    if attrs[i][j].isupper():
        #        print("The attribute entered is invalid and will be removed(uppercase)")
        #        valid = False
        #        break
        #    elif attrs[i][j].isspace():
        #        print("The attribute entered is invalid and will be removed(space)")
        #        valid = False
        #        break
        #    elif not attrs[i][j].isalnum():
        #        if attrs[i][j] == '_':
        #            valid = True
        #        else:
        #            print("The attribute entered is invalid and will be removed(special character)")
        #            valid = False
        #            break
        #    else:
        #        valid = True
        if not re.match(r'^[a-z]*(?:\_[a-z]*)*$', attrs[i]):
            print("The attribute entered is invalid and will be removed")
            attrs.remove(attrs[i])
            i -= 1
        elif attrs[i] == '':
            attrs.remove(attrs[i])
            i -= 1
        elif attrs[i] == "done":
            attrs.remove("done")
            add = False
        elif attrs[i] == "restart":
            print("\nRemoved all previously entered attributes. Please start again at attribute 1.\n")
            attrs.clear()
            i -= i + 1
        i += 1

    error = False
    try:
        schemaId, schema = await anoncreds.issuer_create_schema(authorDid, name, version, json.dumps(attrs))
    except:
        error = True
        print("\n")
        print("Error initiating schema txn.")
        print("\n")
    try:
        schemaTxn = await ledger.build_schema_request(authorDid, schema)
    except:
        error = True
        print("\n")
        print("Error building schema request")
        print("\n")
    if not error:
        print()
        print("Please record your new Schema ID.  It will be used later when you create credential definitions.\n\n")
        print("Schema ID:", schemaId, '\n')
        print()
        return schemaTxn
    else:
        return "error"

async def createCredDef(authorDid, poolHandle):
    print("\nCredential Definition Creation\n------------------------------\n")
    print("Credential Definitions, or Cred Defs, only require an existing Schema ID to be created, and allow you to issue credentials containing the specified Schema's attributes")
    print()
    invalidSchema = True
    credDefTxn = '{"none":"0"}'
    while invalidSchema:
        schemaID = input("Input the Schema ID to use for this Cred Def: ")
        getSchemaRequest = ''
        try:
            getSchemaRequest = await ledger.build_get_schema_request(authorDid, schemaID)
        except IndyError as err:
            print(err)
            print("Error getting schema")

        print()
        if poolHandle == 0:
            await listPools()
            pool = input("Input the index of the network to use: ")
            poolHandle = await openPool(pool)
        schemaJsonResp = 'nothing'
        try:
            schemaJsonResp = await ledger.submit_request(poolHandle, getSchemaRequest)
        except IndyError:
            print("indy is reporting an error")
            schemaJsonResp = '{"error": "indyerror"}'
        except:
            print("the system is reporting an error")
        
        schemaResp = json.loads(schemaJsonResp)
        schemaJson = {}
        try:
            schemaResp = schemaResp["result"]
            schemaJson = {
                "id": schemaID,
                "name": schemaResp["data"]["name"], 
                "version": schemaResp["data"]["version"], 
                "attrNames": schemaResp["data"]["attr_names"],
                "seqNo": schemaResp["seqNo"],
                "ver": '1.0'
            }
            invalidSchema = False
        except KeyError:
            print("Something went wrong when getting the schema")
            print("Most likely the schema is not on the network, Please try again with a valid schema ID")
            invalidSchema = True
            continue
        
        
        credDefId = ''
        credDefJson = ''
        credDefTxn = ''

        try:
            credDefId, credDefJson = await anoncreds.issuer_create_and_store_credential_def(walletHandle, authorDid, json.dumps(schemaJson), tag='1', signature_type = 'CL', config_json = json.dumps({"support_revocation": True}))
        except IndyError as err:
            print(err)
            print("Error while creating cred def")
        try:
            credDefTxn = await ledger.build_cred_def_request(authorDid, credDefJson)
        except IndyError as err:
            print(err)
            print("\nError building cred def request")
    return credDefTxn



async def transactionAuthorAgreement(poolHandle, walletHandle, authorDid):
    answered = False
    add_taa_resp_json = json.dumps({"response": "none"})

    print("\nTransaction Author Agreement\n----------------------------\n")
    
    print("Please agree to the Transaction Author Agreement(TAA) before continuing.")
    print()
    print("Authors must agree to the Transaction Author Agreement(TAA) that exists on the network that they want to use for issuance. The TAA can be read at https://github.com/Indicio-tech/indicio-network/blob/main/TAA/TAA.md if connecting to an Indicio network, which includes agreeing to not place any Personally Identifiable Information(PII) or any illeagal material on the ledger.")
    print()
    add_taa_resp = ''
    while not answered:
        agreeTAA = input("Do you accept the TAA? (Y/N): ")
        if agreeTAA == 'y' or agreeTAA == 'Y':
            try:
                add_taa_req = await ledger.build_get_txn_author_agreement_request(authorDid, None)
            except IndyError:
                print("Error appending TAA to your transaction, has a transaction been created?")
            print()
            add_taa_resp = await ledger.sign_and_submit_request(poolHandle, walletHandle, authorDid, add_taa_req)
            answered = True
            print("You have agreed to the TAA for this session")
        elif agreeTAA == 'n' or agreeTAA == 'N':
            print("We are sorry, you are not able to write schemas or cred defs to the ledger until you agree to the TAA.")
            print()
            print("Press enter to view the menu")
            input()
            answered = True
        else:
            continue
    add_taa_resp_json = 'none'
    if not add_taa_resp == '':
        add_taa_resp_json = json.loads(add_taa_resp)

    return add_taa_resp_json

async def main():
    network = 0
    author = 1
    authorDid = 'none'
    authorVerKey = 'none'
    authorsTxn = 'none'
    poolHandle = 0
    poolList = await pool.list_pools()
    tAA = ''
    setup = input("""Welcome to the Author wizard!

If you are running this, it means that you would like to issue Hyperledger Indy based credentials, but
you are not an Endorser on the network from which you want to issue them. This script will help you
create and prepare the transactions you need that you can then send to an Endorser for their signature
before you send them to the network. The "wizard" will guide you through each step of the process, but
you can perform individual tasks by referring to the main menu. (Hit 'enter' now to use the wizard, or
type 'm' to go to the main menu):""")
    os.system("clear")
    if setup != 'm':
        poolHandle, tAA, author = await authorWizard(author)
  
 
   # Display menu for the different options for
   # author endorser communication
    if author:
        displayMenu()
     
   # loop to allow user to choose many different options from the menu
 
    while author:
        authorAction = input("Author Actions: ")
        if authorAction == 'q':
            author = 0
        elif authorAction == '0':
            poolHandle, tAA, author = await authorWizard(author)
        elif authorAction == '1':
            authorDid, authorVerKey = await listDids(role)
            await createSchema(authorDid)
        
        elif authorAction == '2':
            #listSchemas
            #createCredDef(schema)
            authorsTxn = await createCredDef(authorDid, poolHandle)
        elif authorAction == '3':
            if poolHandle == 0:
                print("There is no network connected. Please connect to a network first (option 6)")
            elif authorsTxn == 'none':
                print("A transaction has not been created yet. Please create a transaction first (options 1 or 2)")
            elif authorDid == 'none' or authorVerKey == 'none':
                print("the Author's DID has not been selected.  Please select a DID to use (option 9)")
            else:
                tAA = await transactionAuthorAgreement(poolHandle, walletHandle, authorDid)
                await signSendTxn(authorDid, authorVerKey, authorsTxn, tAA, poolHandle)
        elif authorAction == '5':
            network = listNetworks()
            await createPool(network)
            print("Network '", network, "' added.")
        elif authorAction == '6':
            poolList = await listPools(role)
            authorPool = input("Choose the index number of the network you wish to use: ")
            if authorPool == len(poolList) + 1:
                network = listNetworks()
                network = await createPool(network)
                poolHandle = await openPool(network)
            else:
                poolHandle = await openPool(authorPool)
            print("Pool opened.")
        elif authorAction == '7':
           
            await createWallet()
            
        elif authorAction == '8':
            await openWallet()
            
        elif authorAction == '9':

            await createDid(role, walletHandle)

        elif authorAction == '10':
            authorDid, authorVerKey = await listDids(role, walletHandle)
            #useDid(authorDid)
        else:
            displayMenu()
    if poolHandle:
        await pool.close_pool_ledger(poolHandle)
    await wallet.close_wallet(walletHandle)




if __name__ == "__main__":
    asyncio.run(main())




