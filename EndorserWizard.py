from AuthorWizard import createDid, createPool, openPool, downloadGenesis, listDids, listPools, transactionAuthorAgreement, listNetworks
import json
import logging
from posixpath import join
import sys
import asyncio
import platform
import os
import urllib
import configparser
import tempfile
import argparse
import datetime
import base58
import re
import secrets
import string
from aiohttp import web
import platform
from ctypes import cdll
from indy import ledger, did, wallet, pool, anoncreds
import indy
from indy.error import ErrorCode, IndyError

walletHandle = 0

role = "Endorser"


async def signTxn(poolHandle, endorserDid, tAA):
    slash = '/'
    if platform.system() == "windows":
        slash ='\\'
    fileName = "authors-txn"
    filePath = os.getcwd() + slash + fileName
    signedFileName = "authors-signed-txn"
    signedFilePath = os.getcwd() + slash + signedFileName
    input("""The author will have sent you a Transaction in a file.
Copy that file to the 'author-endorser-wizards' directory then press enter.""")

        
    authorTxnFile = open(filePath)
    authorTxnReqJson = authorTxnFile.read()
    authorTxnFile.close()
    await writeAuthorToLedger(poolHandle, authorTxnReqJson, endorserDid, tAA)
    
    authorTxnReq = json.loads(authorTxnReqJson)
    authorTxnReq = authorTxnReq["txn"]

    authorTxnReq = json.dumps(authorTxnReq)

    endorsedTxn = await ledger.multi_sign_request(walletHandle, endorserDid, authorTxnReq)

    if os.path.exists(signedFileName):
        os.remove(signedFileName)
    
    endorsedTxnFile = open(signedFilePath, 'w')
    endorsedTxnFile.write(endorsedTxn)
    endorsedTxnFile.close()
    return endorsedTxn, signedFilePath





async def createWallet():
    walletName = "endorser_wizard_wallet" # input("What would you like to name your wallet?: ")
   #seed = input("Insert your seed here. If you want a random seed, insert nothing: ")
    walletKey = "endorser_wizard_wallet" #wallet.generate_wallet_key(seed)
 
    walletID = {
        "id": walletName
    }
 
    walletKey = {
        "key": walletKey
    }
 
    walletKeyJson = json.dumps(walletKey)
    walletIDJson = json.dumps(walletID)
 
   #create wallet code
    print("Creating new wallet '"+walletName+"'...")
 
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
    walletList = []
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
    walletList = listWallets()
    print(' ' + str(len(walletList) + 1) + ": Create New Wallet")
 
    walletIndex = int(input("Please choose the number associated with the wallet that contains your Endorser DID on the network the author wants to write a transaction to: "))
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
    
    if walletIndex == len(walletList)+1:
        if dirExists:
            walletExists = False
            for i in range(len(walletList)):
                if walletList[i] == "endorser_wizard_wallet":
                    walletExists = True
                    
            if walletExists:
                walletName = "endorser_wizard_wallet"
            else:
                walletName = await createWallet()
        else:
            walletName = await createWallet()
    else:
        walletName = walletList[walletIndex-1]
    #userDir = os.path.expanduser("~")
    #walletList = os.listdir(userDir + "/.indy_client/wallet/")
    
    
    #walletList[int(walletIndex)-1]

    walletKey = input("Key: ")
    
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

    return
    #print("...done")

def becomeEndorser():
    print("Please go to https://selfserve.indiciotech.io to become an endorser if you are not already.")
    input("(enter to continue)")
    return

async def writeAuthorToLedger(poolHandle, authorTxnJson, endorserDid, tAA):
    authorTxn = json.loads(authorTxnJson)
    authorDid = authorTxn["author_did"]
    authorVerKey = authorTxn["author_ver_key"]
    tAA = tAA["result"]
    reqJson = ''
    respJson = ''

    utctimestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    
    try:
        reqJson = await ledger.build_get_nym_request(endorserDid, authorDid)
    except:
        print("Error building get nym request")
    try:
        respJson = await ledger.submit_request(poolHandle, reqJson)
    except:
        print("Error retrieving nym from ledger")
    resp = json.loads(respJson)
    if resp["result"]["seqNo"] == None:
        result = ''
        try:
            reqJson = await ledger.build_nym_request(endorserDid, authorDid, authorVerKey, "newAuthor", None)
        except:
            print("Error initiating nym request")
        try:
            reqJson = await ledger.append_txn_author_agreement_acceptance_to_request(reqJson, tAA["data"]["text"], tAA["data"]["version"], None, "for_session", utctimestamp)
        except:
            print("Error appending TAA")
        try:
            result = await ledger.sign_and_submit_request(poolHandle, walletHandle, endorserDid, reqJson)
        except IndyError:
            print("Error sending Author DID to ledger because structure was invalid, was it copied correctly?")
        except:
            print("Error sending Author Did to ledger")
        print("Result:", result)

        result = json.loads(result)
        if result["op"] == "REJECT":
            print("Check the above result to identify why writing the authors did to the ledger was rejected")
            exit()
        
    else:
        print("DID is on ledger.\n")
    return

def displayMenu():
    print("Menu:")
    print("  0: Endorser Wizard")
    print("  1: Sign Authors transaction and send to ledger")
    print("  2: Create Pool")
    print("  3: Open Pool")
    print("  4: Create Wallet")
    print("  5: Open Wallet")
    print("  6: Use DID")
    print("  7: Write Author's DID to ledger")
    print("  8: Agree to the TAA")
    print("  9: Display Menu")
    print("  q: Quit")

async def endorserWizard():
    poolHandle = None
    network = ''
    print("\nEndorser Wizard\n-------------\n")
    print("To begin, you must select or add the network that the issuer would like to use for issuing credentials. If you select \"Add New Network\" you will be given a choice of which network to add to your list  of choices, then that network will be used during the rest  of this session.")
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
    endorserDid, endorserVerKey = await listDids(role, walletHandle)
    tAA = await transactionAuthorAgreement(poolHandle, walletHandle, endorserDid)
    input("Press enter to continue when the Author has completed his side.")

    endorsedTxn, endorsedTxnFile = await signTxn(poolHandle, endorserDid, tAA)
    print('\n')
    print("Signed txn file:", endorsedTxnFile,"\nPass the above Transaction back to the author to send to the ledger.")
    return network, poolHandle, endorserDid, tAA

async def main():
    
    endorsedTxn = ''
    signWizard = input("""Welcome to the Transaction Endorser Wizard!\n\n
If you are running this, it means that you would like to endorse Hyperledger Indy based credentials for
an Author on the network that they want to issue from. This script will help you sign the transactions
your Author needs so you can then send them back to the Author who will send them to the network. The
"wizard" will guide you through each step of the process, but you can perform individual tasks by
referring to the main menu. (Hit 'enter' now to use the wizard, or type 'm' to go to the main menu): """)
    print("...")
    os.system("clear")
    print("Please choose the wallet that contains your Endorser DID on the network the author wants to write a transaction to\n")
    await openWallet()
    if signWizard == 'y':
        network = ''
        poolHandle = 0
        endorserDid = ''
        tAA = ''
    else:
        network, poolHandle, endorserDid, tAA = await endorserWizard()
   # Display menu for the different options for
   # author endorser communication
 
    displayMenu()
    endorser = 1
 
   # loop to allow user to choose many different options from the menu
 
    while endorser:
        endorserAction = input("Endorser Actions: ")
        if endorserAction == 'q':
            endorser = 0
        elif endorserAction == '0':
            network, poolHandle, endorserDid, tAA = await endorserWizard()
        elif endorserAction == '1':
            if poolHandle == 0:
                print("There is no open pool. Please open a pool first (option 3)")
            elif endorserDid == '':
                print("You have not yet chosen the DID to use for this transaction. Please specify your endorser DID (option 6)")
            elif tAA == '':
                print("agreement to the TAA is required for this action. Please agree to the TAA (option 8)")
            else:
                endorsedTxn, endorsedTxnFile = await signTxn(poolHandle, endorserDid, tAA)
                print('\n')
                print("Signed txn file:", endorsedTxnFile, "\nPass the above Transaction back to the author to send to the ledger.")
        elif endorserAction == '2':
            network = listNetworks()
            await createPool(network)
            print("Pool '", network, "' created.")
        elif endorserAction == '3':
            poolList = await listPools()
            endorserPool = input("Choose the index number of the pool you wish to open: ")
            poolHandle = await openPool(endorserPool)
            poolName = str(poolList[int(endorserPool)-1].values()).replace('dict_values([', '')
            poolName = poolName.replace("])", '')
            print("Pool " + poolName + " opened.")
        elif endorserAction == '4':
            await createWallet()
            
        elif endorserAction == '5':
            await openWallet()
            
        elif endorserAction == '6':
            endorserDid = await listDids(role, walletHandle)
            #useDid(authorDid)
        elif endorserAction == '7':
            if poolHandle == 0:
                print("There is no open pool. Please open a pool first (option 3)")
            elif endorserDid == '':
                print("You have not yet chosen the DID to use for this transaction. Please specify your endorser DID (option 6)")
            elif tAA == '':
                print("agreement to the TAA is required for this action. Please agree to the TAA(option 8)")
            else:
                authorDid = input("Authors DID: ")
                authorVerKey = input("Author's Verkey: ")
                authorInfo = {
                    "author_did": authorDid,
                    "author_ver_key": authorVerKey
                }
                authorInfoJson = json.dumps(authorInfo)
            
                await writeAuthorToLedger(poolHandle, authorInfoJson, endorserDid, tAA)
        elif endorserAction == '8':
            if poolHandle == 0:
                print("Please open a pool first (option 3)")
            elif endorserDid == '':
                print("Please specify your endorser DID (option 6)")
            else:
                tAA = await transactionAuthorAgreement(poolHandle, walletHandle, endorserDid)
        else:
            displayMenu()
    if poolHandle:
        await pool.close_pool_ledger(poolHandle)
    if walletHandle:
        await wallet.close_wallet(walletHandle)

    return


if __name__ == "__main__":
    asyncio.run(main())
