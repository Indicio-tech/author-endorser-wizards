import json
from posixpath import join
import asyncio
import os
import urllib
import datetime
import secrets
import string
from aiohttp import web
from ctypes import cdll
from indy import ledger, did, wallet, pool, anoncreds
from indy.error import ErrorCode, IndyError

walletHandle = 0

def downloadGenesis(networkUrl):
    try:
        urllib.request.urlretrieve(networkUrl, "genesisFile")
    except:
        print("\n")
        print("Error downloading genesis file")
        print("\n")

async def createPool(network):

    if "indicioTestnet" == network:
        network_genesis_url="https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_testnet_genesis"
    elif "indicioDemonet" == network:
        network_genesis_url="https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_demonet_genesis"
    elif "indicioMainnet" == network:
        network_genesis_url="https://raw.githubusercontent.com/Indicio-tech/indicio-network/main/genesis_files/pool_transactions_mainnet_genesis"
    else: network = "Network name not found"

    downloadGenesis(network_genesis_url)


    config = {
            "genesis_txn": "genesisFile"
    }
    configJson = json.dumps(config)

    try:
        await pool.create_pool_ledger_config(network, configJson)
    except:
        print("\n")
        print("Error creating pool")
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
        pool_handle = await pool.open_pool_ledger(config_name=network, config=None)
    except:
        print("\n")
        print("Error opening pool '" + network +"'")
        print("\n")
    return pool_handle
 
async def listPools():
    try:
        poolList = await pool.list_pools()
    except:
        print("\n")
        print("Error creating list of pools")
        print("\n")

    print("Author's Pools:")
    for i in range(len(poolList)):
        print("   " + str(i + 1) + ":", *list(poolList[i].values()))
    print("   " + str(len(poolList)+1) + ": Create New Pool")
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
    try:
        walletList = os.listdir(userDir + "/.indy_client/wallet/")
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
    try:
        walletList = os.listdir(userDir + "/.indy_client/wallet/")
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

    return
    
async def authorWizard():
    poolHandle = None
    print("Welcome to the Author Transaction Creation Wizard!")
    print("Below is a list of pools:")
    poolList = await listPools()
    userPool = input("Choose the index number of the pool you want to open: ")
    if userPool == str(len(poolList) + 1):
       network = listNetworks()
       
       network = await createPool(network)
       poolHandle = await openPool(network)
    else:
       poolHandle = await openPool(userPool)
  
   #print("Below is a list of wallets:")
   
    print("Here is the list of dids in your wallet.")
    authorDid, authorVerKey = await listDids()
   #listDids()
    #authorDid = input("Choose the index number of the did you want to use: ")
    #if authorDid == "last":
       #authorDidSeed = input("Enter your super secret seed for your new did: ")
       #authorDid = createDidFromSeed(authorDidSeed)
   #didUse(authorDid)
    
    
    tAA = await transactionAuthorAgreement(poolHandle, authorDid)
    schemaID = ''

    schemaChoice = input("Do you want to... \n 1. Create a new schema or \n 2. Use an existing one?\n (1/2):")
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
            schemaChoice = input("Do you want to... \n 1. Create a new schema or \n 2. Use an existing one?\n (1/2):")

    credDefTxn = await createCredDef(authorDid, poolHandle)

    await signSendTxn(authorDid, authorVerKey, credDefTxn, tAA, poolHandle)

    print()
    return poolHandle, tAA

def displayMenu():
    print("Menu:")
    print("  0: Author Wizard")
    print("  1: Create Schema")
    print("  2: Sign Schema and send to ledger")
    print("  3: Create Credential Definition")
    print("  4: Sign Cred def and send to ledger")
    print("  5: Create Pool")
    print("  6: Open Pool")
    print("  7: Create Wallet")
    print("  8: Open Wallet")
    print("  9: Create DID")
    print(" 10: Use DID")
    print(" 11: Display Menu")
    print("  q: Quit")
 
def listNetworks():
    print(" 1: indicioTestnet")
    print(" 2: indicioDemonet")
    print(" 3: indicioMainnet")
 
    network = input("which network do you want to use? : ")
 
    if network == '1':
        network = "indicioTestnet"
    elif network == '2':
        network = "indicioDemonet"
    elif network == '3':
        network = "indicioMainnet"
    return network
 
async def createDid():
    

    seed = input("Input the seed for your did, if it is blank it will be generated for you:")
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
        print("It is advised to save this information in a secure location")
        print()

    metadataChoice = input("Would you like to add metadata for your did? (y/n): ")
    print()
    if metadataChoice == 'y':
        didMetadata = input("Input metadata here: ")
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
    index = int(input("Choose the index of the did you would like to use (or choose 'create' to make a new one): "))
    index = index - 1
    if index == len(didList):
        authorDid, authorVerKey = await createDid()
        
    else:
        authorDid = didList[index]["did"]
        authorVerKey = didList[index]["verkey"]
        

    return authorDid, authorVerKey

async def signSendTxn(authorDid, authorVerKey, authorsTxn, tAA, poolHandle):
    tAA = tAA["result"]
# note: check for endorser using get nym
    utctimestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

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
    print(authorsTxnWithDid)

    authorsSignedTxn = input("The endorser needs to sign this transaction, copy it then send it to the endorser to sign.\n Input signed transaction here: ")
    
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
        print("Successfully written to the ledger.")
    return

async def createSchema(authorDid):
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
    schemaID = input("Input the schema ID to use for this cred def: ")
    getSchemaRequest = ''
    try:
        getSchemaRequest = await ledger.build_get_schema_request(authorDid, schemaID)
    except IndyError as err:
        print(err)
        print("Error getting schema")

    print()
    if not poolHandle:
        await listPools()
        pool = input("Input the index of the pool to use: ")
        poolHandle = await openPool(pool)
    schemaJsonResp = 'none'
    try:
        schemaJsonResp = await ledger.submit_request(poolHandle, getSchemaRequest)
    except IndyError:
        print("indy is reporting an error")
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
    except KeyError:
        print("Something went wrong when getting the schema")
    
    
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
    print("The TAA can be read at https://github.com/Indicio-tech/indicio-network/blob/main/TAA/TAA.md if connecting to an Indicio network, which includes agreeing to not place any Personaly Identifiable Information(PII) or any illeagal material on the ledger.")
    add_taa_resp = ''
    while not answered:
        agreeTAA = input("Do you accept the TAA(Y/N)?")
        if agreeTAA == 'y' or agreeTAA == 'Y':
            add_taa_req = await ledger.build_get_txn_author_agreement_request(authorDid, None)
            
            print()
            add_taa_resp = await ledger.sign_and_submit_request(poolHandle, walletHandle, authorDid, add_taa_req)
            answered = True
            print("Great! You are all ready to go.")
        elif agreeTAA == 'n' or agreeTAA == 'N':
            print("we are sorry, you are not able to write schemas or cred defs to the ledger.")
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
    await openWallet()
    poolHandle = 0
    poolList = await pool.list_pools()
    addTAA = json.dumps({"key": "value"})
    setup = input("Hello! If you would like to skip the transaction creation wizard, type 'y' otherwise hit enter: ")
    if setup != 'y':
        poolHandle, addTAA = await authorWizard()
  
 
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
            poolHandle, addTAA = await authorWizard()
        elif authorAction == '1':
            authorDid = await listDids()
            await createSchema(authorDid)
        elif authorAction == '2':
            #sendSignSchema()
            print("fixme: send schema option")
        elif authorAction == '3':
            #listSchemas
            #createCredDef(schema)
            await createCredDef(authorDid, poolHandle)
        elif authorAction == '4':
            #sendSignCredDef
            print("Fixme: send cred def")
        elif authorAction == '5':
            network = listNetworks()
            await createPool(network)
            print("Pool '", network, "' created.")
        elif authorAction == '6':
            poolList = await listPools()
            authorPool = input("Choose the index number of the pool you wish to open: ")
            if authorPool == len(poolList) + 1:
                network = listNetworks()
      
                network = await createPool(network)
                await openPool(network)
            else:
                network = await openPool(authorPool)
            print("Pool \'" + network + "\' opened.")
        elif authorAction == '7':
           
            await createWallet()
            print("wallet has been created")
        elif authorAction == '8':
            await openWallet()
            print("wallet has been opened")
        elif authorAction == '9':
            seed = input("would you like to use a seed? (Y/n): ")
            if seed == 'n':
               #createDidFromSeed("none")
                print("FIXME: create did with random seed")
            else:
                authorDidSeed = input("enter a seed to use for the did: ")
                print("FIXME: create did")
        elif authorAction == '10':
            authorDid = await listDids()
            #useDid(authorDid)
        else:
            displayMenu()
    if poolHandle:
        await pool.close_pool_ledger(poolHandle)
    await wallet.close_wallet(walletHandle)




if __name__ == "__main__":
    asyncio.run(main())




