from AuthorWizard import createDid, createPool, openPool, downloadGenesis, listDids, listPools, transactionAuthorAgreement, listNetworks
import json
from getpass import getpass
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
from indy.error import ErrorCode, IndyError, WalletAccessFailed

walletHandle = 0

role = "Endorser"


async def signTxn(poolHandle, endorserDid, tAA):
    print("\nTransaction Signing\n-------------------\n")
    slash = '/'
    if platform.system() == "windows":
        slash ='\\'
    fileName = "authors-txn"
    filePath = os.getcwd() + slash + fileName
    signedFileName = "authors-signed-txn"
    signedFilePath = os.getcwd() + slash + signedFileName
    input("""The author will have sent you a Transaction in the file """+fileName+""". Copy that file to the directory you ran the program from, then press enter.""")

    if os.path.exists(signedFileName):
        input("\nA file named '"+signedFileName+"""' already exists and will be deleted.
Press Enter to continue""")
        os.remove(signedFileName)
    
    error = True
    while error:
        try:
            authorTxnFile = open(fileName)
            error = False
        except FileNotFoundError:
            print("\nThe file does not exist, Please ensure that the author sent you the correct file and it is in the directory you ran the program from.\n")
            print("File name:", fileName, '\n')
            input("Press enter when completed")
            error = True
            continue
        authorTxnReqJson = authorTxnFile.read()
        authorTxnFile.close()

    
        await writeAuthorToLedger(poolHandle, authorTxnReqJson, endorserDid, tAA)

    
        authorTxnReq = json.loads(authorTxnReqJson)
        authorTxnReq = authorTxnReq["txn"]
        if authorTxnReq["endorser"] != endorserDid:
            input("The file sent does not conatain the correct Endorser DID.  Please contact the Author and Request them to input the correct DID in their transaction, then replace the currant Transaction file and press enter.")
            error = True
            continue
        else:
            error = False
    authorTxnReq = json.dumps(authorTxnReq)

    endorsedTxn = await ledger.multi_sign_request(walletHandle, endorserDid, authorTxnReq)

    
    endorsedTxnFile = open(signedFilePath, 'w')
    endorsedTxnFile.write(endorsedTxn)
    endorsedTxnFile.close()
    return endorsedTxn, signedFileName


async def createWallet():
    print("\nWallet Creation\n---------------\n")

    
    walletName = "endorser_wizard_wallet" # input("What would you like to name your wallet?: ")
   #seed = input("Insert your seed here. If you want a random seed, insert nothing: ")
    walletKey = "endorser_wizard_wallet" #wallet.generate_wallet_key(seed)
    print("The Wizard will create a wallet for you named '"+walletName+"'. The key (password) to this wallet is'"+walletKey+"'")
 
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
 
    walletIndex = input("Please select a wallet or hit enter to create a new one("+str(len(walletList)+1)+"): ")
    if walletIndex.isnumeric():
        walletIndex = int(walletIndex)
    else:
        walletIndex = len(walletList)+1

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
                    walletIndex = i
                    walletExists = True
                    
            if walletExists:
                walletName = "endorser_wizard_wallet"
                print("\nThe wallet '"+walletList[walletIndex]+"' already exists, and will be used.")
            else:
                walletName = await createWallet()
        else:
            walletName = await createWallet()
    else:
        walletName = walletList[walletIndex-1]
    #userDir = os.path.expanduser("~")
    #walletList = os.listdir(userDir + "/.indy_client/wallet/")
    
    
    #walletList[int(walletIndex)-1]
    error = True
    while(error):
        if walletName == "endorser_wizard_wallet":
            walletKey = walletName
        else:
            walletKey = getpass("Enter your Wallet Key (password): ")
        
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
        except WalletAccessFailed:
            print("\nThe Key entered was incorrect. Please try again.\n")
        except:
            print("\n")
            print("Error opening wallet '" + walletName + "'")
            print("\n")
            break
        else:
            error = False
            print("...done")

    return
    #print("...done")

def becomeEndorser():
    print("Please go to https://selfserve.indiciotech.io to become an endorser if you are not already.")
    input("(enter to continue)")
    return

async def writeAuthorToLedger(poolHandle, authorTxnJson, endorserDid, tAA):
    authorTxn = json.loads(authorTxnJson)
    try:
        authorDid = authorTxn["author_did"]
    except KeyError:
        print("\nThe given txn did not contain the Author's DID\n")
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
        print("Error retrieving nym from network")
    resp = json.loads(respJson)
    if resp["result"]["seqNo"] == None:
        result = ''
        try:
            reqJson = await ledger.build_nym_request(endorserDid, authorDid, authorVerKey, None, None)
        except:
            print("Error initiating nym request")
        try:
            reqJson = await ledger.append_txn_author_agreement_acceptance_to_request(reqJson, tAA["data"]["text"], tAA["data"]["version"], None, "for_session", utctimestamp)
        except:
            print("Error appending TAA")
        try:
            result = await ledger.sign_and_submit_request(poolHandle, walletHandle, endorserDid, reqJson)
            print("\nWriting the Author's DID to the network...")
        except IndyError:
            print("\nError sending Author DID to network because structure was invalid, was it copied correctly?")
        except:
            print("\nError sending Author Did to network")
        

        result = json.loads(result)
        
        if result["op"] == "REJECT":
            print("Result:", result, '\n')
            print("Check the above result to identify why writing the authors did to the network was rejected")
            exit()
        else:
            print("\nSuccessfully wrote the Author DID to the network.\n")
        
    else:
        print("\nThe Author DID is already on the network.\n")
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

async def endorserWizard(endorser):
    poolHandle = None
    network = ''
    endorsing = True
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

    print("\nFor the transaction to be sent to the network, the Authors DID must be on the network. To add their DID to the network, you must agree to the TAA.\n")
    
    tAA = await transactionAuthorAgreement(poolHandle, walletHandle, endorserDid)
    input("\n\nPress enter to continue when the Author has completed building their transaction.")
    print()
    while endorsing:
        endorsedTxn, endorsedTxnName = await signTxn(poolHandle, endorserDid, tAA)
        print('\n')
        print("Signed txn file:", endorsedTxnName,"\n\nSend the above Transaction back to the Author to send to the network.")
        again = input("\nDo you have another Transaction to sign? (Y/n): ")
        if again == 'n' or again == 'N':
            endorsing = False
        else:
            continue
    print("\n")
    print("Thank you for using the Endorser Wizard.\n\n\n")

    choice = input("The Transaction Endorser Wizard has finished.  Press 'q' to quit, or press enter to go to the main menu: ")
    if choice == 'q' or choice == 'Q':
        endorser = 0

    return network, poolHandle, endorserDid, tAA, endorser

async def main():
    endorser = 1
    endorsedTxn = ''
    signWizard = input("""Welcome to the Transaction Endorser Wizard!\n\n
If you are running this, it means that you would like to endorse Hyperledger Indy based credentials for
an Author on the network that they want to issue from. This script will help you sign the transactions
your Author needs so you can then send them back to the Author who will send them to the network. The
"wizard" will guide you through each step of the process, but you can perform individual tasks by
referring to the main menu. (Hit 'enter' now to use the wizard, or type 'm' to go to the main menu): """)
    print("...")
    os.system("clear")
    print("Please choose the wallet that contains your Endorser DID on the network the author wants to write a transaction to.  If you do not have one yet you may select 'Create new wallet'.\n")
    await openWallet()
    if signWizard == 'm':
        network = ''
        poolHandle = 0
        endorserDid = ''
        tAA = ''
    else:
        network, poolHandle, endorserDid, tAA, endorser = await endorserWizard(endorser)
   # Display menu for the different options for
   # author endorser communication
   # do not display if wizard completed and choice is 'q'(quit)
    if endorser:
        displayMenu()
    
 
   # loop to allow user to choose many different options from the menu
 
    while endorser:
        endorserAction = input("Endorser Actions: ")
        if endorserAction == 'q':
            endorser = 0
        elif endorserAction == '0':
            network, poolHandle, endorserDid, tAA = await endorserWizard()
        elif endorserAction == '1':
            if poolHandle == 0:
                print("There is no network connected. Please connect a network first (option 3)")
            elif endorserDid == '':
                print("You have not yet chosen the DID to use for this transaction. Please specify your endorser DID (option 6)")
            elif tAA == '':
                print("agreement to the TAA is required for this action. Please agree to the TAA (option 8)")
            else:
                endorsedTxn, endorsedTxnName = await signTxn(poolHandle, endorserDid, tAA)
                print('\n')
                print("Signed txn file:", endorsedTxnName, "\nPass the above Transaction back to the author to send to the ledger.")
        elif endorserAction == '2':
            network = listNetworks()
            await createPool(network)
            print("connected to network '", network, "'.")
        elif endorserAction == '3':
            poolList = await listPools()
            endorserPool = input("Choose the index number of the network you wish to use: ")
            poolHandle = await openPool(endorserPool)
            poolName = str(poolList[int(endorserPool)-1].values()).replace('dict_values([', '')
            poolName = poolName.replace("])", '')
            print("Using the " + poolName + " network.")
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
