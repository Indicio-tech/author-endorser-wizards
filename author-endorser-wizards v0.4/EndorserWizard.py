import json
import logging
from posixpath import join
import sys
import asyncio
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

async def createDid():
    
    seed = input("Input the seed for your did, if it is blank it will be generated for you: ")
    if seed == '':
        seed = seed.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))
    print("Seed:", seed)
    print("Copy this seed and put in a secure place")
    print()
    seedJson = {
        "seed": seed
    }
    
    seedJson = json.dumps(seedJson)
    endorserDid, endorserVerKey = await did.create_and_store_my_did(walletHandle, seedJson)
    print("DID:", endorserDid, "\nVer Key:", endorserVerKey)
    print()

    metadataChoice = input("Would you like to add metadata for your did? (y/n): ")
   
    if metadataChoice == 'y':
        didMetadata = input("Input metadata here: ")
        did.set_did_metadata(walletHandle, endorserDid, didMetadata)
    return endorserDid

async def listDids():
    didListJson = await did.list_my_dids_with_meta(walletHandle)
    
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
    index = int(input("Choose your did's index: "))
    index = index - 1
    if index == len(didList):
        endorserDid, endorserVerKey = await createDid()
    else:
        endorserDid = didList[index]["did"]

    return endorserDid

async def signTxn(poolHandle, endorserDid, tAA):
    authorTxnReqJson = input("The author will have sent you a Transaction as a json.\nPaste that Transaction here: ")
    
    await writeAuthorToLedger(poolHandle, authorTxnReqJson, endorserDid, tAA)
    
    authorTxnReq = json.loads(authorTxnReqJson)
    authorTxnReq = authorTxnReq["txn"]

    authorTxnReq = json.dumps(authorTxnReq)

    endorsedTxn = await ledger.multi_sign_request(walletHandle, endorserDid, authorTxnReq)
    return endorsedTxn

async def openPool(network):  
    poolList = await pool.list_pools()
    if network == "Network name not found":
        return "Network name not found"
    for i in range(len(poolList)):
        if network == str(i+1):
            network = list(poolList[i].values())
    network = str(network).replace('[\'', '')
    network = network.replace('\']', '')
 
    pool_handle = await pool.open_pool_ledger(config_name=network, config=None)
    return pool_handle
 
async def listPools():
    poolList = await pool.list_pools()

    print("Endorser's Pools:")
    for i in range(len(poolList)):
        print("   " + str(i + 1) + ":", *list(poolList[i].values()))
    print("   " + str(len(poolList)+1) + ": Create New Pool")

    return poolList

async def transactionAuthorAgreement(poolHandle, endorserDid):
    answered = False
    add_taa_resp_json = json.dumps({"response": "none"})
    
    print("Please agree to the Transaction Author Agreement(TAA) before continuing.")
    print()
    print("The TAA can be read at https://github.com/Indicio-tech/indicio-network/blob/main/TAA/TAA.md if connecting to an Indicio network, which includes agreeing to not place any Personaly Identifiable Information(PII) or any illeagal material on the ledger.")
    
    while not answered:
        agreeTAA = input("Do you accept the TAA(Y/N)?")
        if agreeTAA == 'y' or agreeTAA == 'Y':
            add_taa_req = await ledger.build_get_txn_author_agreement_request(endorserDid, None)
            
            print()
            add_taa_resp = await ledger.sign_and_submit_request(poolHandle, walletHandle, endorserDid, add_taa_req)
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
    
    add_taa_resp_json = json.loads(add_taa_resp)

    return add_taa_resp_json

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
   #print("Creating new wallet '"+walletName+"'...")
 
    await wallet.create_wallet(walletIDJson, walletKeyJson)
 
   #print("...done")
 
    return walletName
 
def listWallets():
    userDir = os.path.expanduser("~")
    walletList = os.listdir(userDir + "/.indy_client/wallet/")
 
    print("Your Wallets:")
 
    for i in range(len(walletList)):
        print(' ' + str(i+1) + ":", walletList[i])
   #list wallet code
    return walletList
 
async def openWallet():
    walletList = listWallets()
    print(' ' + str(len(walletList) + 1) + ": Create New Wallet")
 
    walletIndex = input("Choose the index number of the wallet you want to open: ")

    walletName = "none"
    exists = False
    if walletIndex == len(walletList) + 1:
        for i in range(len(walletList)):
            if walletList[i] == "endorser_wizard_wallet":
                exists = True
        
        if not exists:
            walletName = await createWallet()
        else:
            walletName = "endorser_wizard_wallet"
    else:
        walletName = walletList[walletIndex]
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
    
    global walletHandle
    walletHandle = await wallet.open_wallet(walletNameConfig, walletKeyConfig)
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

    utctimestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    reqJson = await ledger.build_get_nym_request(endorserDid, authorDid)
    respJson = await ledger.submit_request(poolHandle, reqJson)
    resp = json.loads(respJson)
    if resp["result"]["seqNo"] == None:
        reqJson = await ledger.build_nym_request(endorserDid, authorDid, authorVerKey, "newAuthor", None)
        reqJson = await ledger.append_txn_author_agreement_acceptance_to_request(reqJson, tAA["data"]["text"], tAA["data"]["version"], None, "for_session", utctimestamp)
        result = await ledger.sign_and_submit_request(poolHandle, walletHandle, endorserDid, reqJson)
        print("Result:", result)
        if result["op"] == "REJECT":
            print("Check the above result to identify why writing the authors did to the ledger was rejected")
            exit()
        
    else:
        print("DID is on ledger.\n")
    return

async def main():
    print("Hello, welcome to the endorser wizard!")
    await openWallet()
    await listPools()
    network = input("Choose the pool you want to open: ")
    poolHandle = await openPool(network)
    endorserDid = await createDid()
    tAA = await transactionAuthorAgreement(poolHandle, endorserDid)
    input("Press enter to continue when the Author has completed his side.")
    becomeEndorser()

    endorsedTxn = await signTxn(poolHandle, endorserDid, tAA)
    print('\n')
    print("Signed txn:", endorsedTxn, "\nPass the above Transaction back to the author to send to the ledger.")

    

    return


if __name__ == "__main__":
    asyncio.run(main())
