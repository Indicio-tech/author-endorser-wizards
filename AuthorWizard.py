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
from indy.error import ErrorCode, IndyError
import platform

os.system("clear")
if platform.system() == "Windows":
    os.add_dll_directory(os.getenv('LIBINDY_DIR'))

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
 
async def listPools():
    print("\nConnect to a Network\n--------------------\n")
    try:
        poolList = await pool.list_pools()
    except:
        print("\n")
        print("Error creating list of networks")
        print("\n")

    print("Author's Networks:")
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
   #list wallet code
    return walletList
 
async def openWallet():
   #walletList = listWallets()
   #print(' ' + str(len(walletList) + 1) + ": Create New Wallet")
 
   #walletIndex = input("Choose the index number of the wallet you want to open: ")
   #if walletIndex == len(walletList):
   #    createWallet()

    walletName = "none"
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
    
        
    if dirExists:
        walletExists = False
        for i in range(len(walletList)):
            if walletList[i] == "wizard_wallet":
                walletExists = True
                
        if walletExists:
            walletName = "wizard_wallet"
        else:
            walletName = await createWallet()
    else:
        walletName = await createWallet()

    #walletList[int(walletIndex)-1]

    #walletKey = input("Key: ")
    
    walletNameConfig = {
        "id": walletName
    }
    walletKeyConfig = {
        "key": walletName
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
        print('\n')

    return
    
async def authorWizard():
    poolHandle = None
    print("\nAuthor Wizard\n-------------\n")
    print("To begin, you must select or add the network that you would like to use for issuing credentials. If you select \"Add New Network\" you will be given a choice of which network to add to your list  of choices, then that network will be used during the rest  of this session.")
    print()
    poolList = await listPools()
    userPool = input("Select the network you want to use("+str(len(poolList)+1)+"): ")
    print("\n")
    if userPool == str(len(poolList) + 1) or userPool == '':
       network = listNetworks()
       
       network = await createPool(network)
       poolHandle = await openPool(network)
    else:
       poolHandle = await openPool(userPool)
  
   #print("Below is a list of wallets:")
   
    print("Here is the list of DIDs in your wallet.")
    print()
    authorDid, authorVerKey = await listDids()
   #listDids()
    #authorDid = input("Choose the index number of the did you want to use: ")
    #if authorDid == "last":
       #authorDidSeed = input("Enter your super secret seed for your new did: ")
       #authorDid = createDidFromSeed(authorDidSeed)
   #didUse(authorDid)
    print("\n")
    
    tAA = await transactionAuthorAgreement(poolHandle, authorDid)

    print("\n")
    schemaID = ''

    schemaChoice = input("""Do you want to... 
 1. Create a new schema or 
 2. Use an existing one?

 (1/2):""")
    while True:
        if schemaChoice == '1':
            schemaTxn = await createSchema(authorDid)
            await signSendTxn(authorDid, authorVerKey, schemaTxn, tAA, poolHandle)
            break
        elif schemaChoice == '2':
            break
        else:
            print("Invalid input, please input 1 or 2")
            print()
            schemaChoice = input("""Do you want to... 
 1. Create a new schema or 
 2. Use an existing one?

 (1/2):""")

    credDefTxn = await createCredDef(authorDid, poolHandle)

    await signSendTxn(authorDid, authorVerKey, credDefTxn, tAA, poolHandle)

    print()
    return poolHandle, tAA

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
 
async def createDid():
    

    seed = input("Input the seed for your DID, if it is blank it will be generated for you:")
    print()
    if seed == '':
        seed = seed.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))
        print("New Seed:", seed)
    
    
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
    else:
        print("Created DID:", authorDid[0])
        print("VerKey:", authorDid[1])
        print()
        input("After you have saved your Seed in a safe place and recorded your Author DID and Verkey for later use, please hit enter to continue.")
        print()

    metadataChoice = input("Would you like to add metadata for your did? (Y/n): ")
    if metadataChoice == 'n' or metadataChoice == 'N':
        print()
    else:
        didMetadata = "Author DID created by wizard"
        print("\n")
        try:
            await did.set_did_metadata(walletHandle, authorDid[0], didMetadata)
        except IndyError:
            print("\n")
            print("Error setting metadata")
            print("\n")
            raise
        except:
            print("system error")
            raise

    return authorDid

async def listDids():
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
        if len(didList[i]["did"]) == 22:
            print("     " + str(i + 1) + " |", didList[i]["did"], '|', didList[i]["metadata"])
        else:
            print("     " + str(i + 1) + " |", didList[i]["did"], " |", didList[i]["metadata"])


    print("     " + str(len(didList)+1) + " |", "Create New DID        ", '|', "Create a new DID to use")
    print()
    index = input("Choose the index of the did you would like to use (" + str(len(didList)+1) + "): ")
    print()
    
    if index == '':
        authorDid, authorVerKey = await createDid()
    elif index == str(len(didList)+1):
        authorDid, authorVerKey = await createDid()
    else:
        index = int(index) - 1
        authorDid = didList[index]["did"]
        authorVerKey = didList[index]["verkey"]
        

    return authorDid, authorVerKey

async def signSendTxn(authorDid, authorVerKey, authorsTxn, tAA, poolHandle):
    tAA = tAA["result"]
# note: check for endorser using get nym
    utctimestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    fileName = "authors-txn.txt"
    signedFileName = "authors-signed-txn.txt"

    try:
        authorsTxn = await ledger.append_txn_author_agreement_acceptance_to_request(authorsTxn, tAA["data"]["text"], tAA["data"]["version"], None, 'for_session', utctimestamp)
    except:
        print("\n")
        print("Error appending the TAA")
        print("\n")
        
    endorserDid = input("input your endorser's did: ")
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
    
    slash = '/'
    if platform.system() == "windows":
        slash ='\\'
    if os.path.exists(fileName):
        input("A file named '"+fileName+"""' already exists and will be over written.
If you would like to keep the original file, rename it now.
Press Enter to continue""")

    print("Transaction file: author-endorser-wizards" + slash + fileName)

    try:
        txnFile = open(fileName, "x")
    except:
        print("Replacing the previous version of " + fileName + "...")
        txnFile = open(fileName, "w")
    else: 
        print("Writing", fileName + "...")
    txnFile.write(authorsTxnWithDid)
    txnFile.close()
    print("...done")
    print()
    input("""The endorser needs to sign this transaction.  
Send the file named '"""+fileName+"' to the endorser.")

    input("""The Endorser will have sent a file named '"""+signedFileName+"""'.
Copy that file to the 'author-endorser-wizards' directory then press enter.""")
    error = True
    while error:
        try:
            authorsSignedTxnFile = open(signedFileName)
            error == False
        except FileNotFoundError:
            print("The file does not exsist, Please ensure that the endorser sent you the correct file and it is in the correct directory.")
            print("""File path: author-endorser-wizards/
File name:""", signedFileName)
            input("Press enter when completed")
            error = True
    authorsSignedTxn = authorsSignedTxnFile.read()
    authorsSignedTxnFile.close()

    error = False
    try:
        await ledger.submit_request(poolHandle, authorsSignedTxn)
    except IndyError as CommonInvalidStructure:
        print("ERROR: Could not write txn to ledger", CommonInvalidStructure)
        print()
        error = True
    except ErrorCode.LedgerInvalidTransaction:
        print("ERROR: Could not write txn to ledger")
        print()
        error = True
    if not error:
        print("\n")
        print("Successfully written to the ledger.")
    return

async def createSchema(authorDid):
    print("Schema Creation\n---------------\n")
    name = input("Enter name of schema: ")
    version = input("Enter version: ")
    attrs = []

    add = True
    i = 0
    print("Enter the schema's attributes names one at a time ('done' to stop, ... to restart).")
    while add:
        attrs.append(input("Attribute: "))
        if attrs[i] == '':
            attrs.remove(attrs[i])
            i -= 1
        elif attrs[i] == "done":
            attrs.remove("done")
            add = False
        elif attrs[i] == "...":
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
        print("Schema ID:", schemaId)
        print("This will be required to create a credential definition.  Please copy or save for later use.")
        print()
        return schemaTxn
    else:
        return "error"

async def createCredDef(authorDid, poolHandle):
    invalidSchema = True
    credDefTxn = '{"none":"0"}'
    while invalidSchema:
        schemaID = input("Input the schema ID to use for this cred def: ")
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
            schemaJsonResp = '"error": "indyerror"'
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
            print("Most likely the schema is not on the ledger, Please try again with a valid schema ID")
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



async def transactionAuthorAgreement(poolHandle, authorDid):
    answered = False
    add_taa_resp_json = json.dumps({"response": "none"})
    
    print("Please agree to the Transaction Author Agreement(TAA) before continuing.")
    print()
    print("The TAA can be read at https://github.com/Indicio-tech/indicio-network/blob/main/TAA/TAA.md if connecting to an Indicio network, which includes agreeing to not place any Personally Identifiable Information(PII) or any illeagal material on the ledger.")
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
    authorDid = 'none'
    authorVerKey = 'none'
    authorsTxn = 'none'
    await openWallet()
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
        poolHandle, tAA = await authorWizard()
  
 
   # Display menu for the different options for
   # author endorser communication
 
    displayMenu()
    author = 1
 
   # loop to allow user to choose many different options from the menu
 
    while author:
        authorAction = input("Author Actions: ")
        if authorAction == 'q':
            author = 0
        elif authorAction == '0':
            poolHandle, tAA = await authorWizard()
        elif authorAction == '1':
            authorDid, authorVerKey = await listDids()
            await createSchema(authorDid)
        
        elif authorAction == '2':
            #listSchemas
            #createCredDef(schema)
            authorsTxn = await createCredDef(authorDid, poolHandle)
        elif authorAction == '3':
            if poolHandle == 0:
                print("There is no network connected. Please connect to a network first (option 5)")
            elif authorsTxn == 'none':
                print("A transaction has not been created yet. Please create a transaction first (options 1 or 2)")
            elif authorDid == 'none' or authorVerKey == 'none':
                print("the Author's DID has not been selected.  Please select a DID to use (option 9)")
            else:
                tAA = await transactionAuthorAgreement(poolHandle, authorDid)
                await signSendTxn(authorDid, authorVerKey, authorsTxn, tAA, poolHandle)
        elif authorAction == '5':
            network = listNetworks()
            await createPool(network)
            print("Network '", network, "' added.")
        elif authorAction == '6':
            poolList = await listPools()
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

            await createDid()

        elif authorAction == '10':
            authorDid, authorVerKey = await listDids()
            #useDid(authorDid)
        else:
            displayMenu()
    if poolHandle:
        await pool.close_pool_ledger(poolHandle)
    await wallet.close_wallet(walletHandle)




if __name__ == "__main__":
    asyncio.run(main())




