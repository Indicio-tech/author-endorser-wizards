from unittest.mock import patch
import pytest
from ..author import (
    main,
    author,
    listDids,
    createSchema,
    createCredDef,
    transactionAuthorAgreement,
    listNetworks,
    signSendTxn,
    createPool,
    listPools,
    openPool,
    createWallet,
    openWallet,
    createDid,
    displayMenu,
)


@patch(main, "author")
@patch(main, "listDids")
@patch(main, "createSchema")
@patch(main, "createCredDef")
@patch(main, "transactionAuthorAgreement")
@patch(main, "signSendTxn")
@patch(main, "createPool")
@patch(main, "listPools")
@patch(main, "listNetworks")
@patch(main, "openPool")
@patch(main, "createWallet")
@patch(main, "openWallet")
@patch(main, "createDid")
@patch(main, "displayMenu")
@pytest.mark.asyncio
async def test_author_menu(monkeypatch):
    await main()
    monkeypatch.setattr("builtins.input", lambda _: "0")
    author.assert_called_once()  # "  0: Author Wizard"
    monkeypatch.setattr("builtins.input", lambda _: "1")
    listDids.assert_called_once()  # "  1: Create Schema"
    createSchema.assert_called_once()  # "  1: Create Schema"
    monkeypatch.setattr("builtins.input", lambda _: "2")
    createCredDef.assert_called_once()  # "  2: Create Credential Definition"
    monkeypatch.setattr("builtins.input", lambda _: "3")
    transactionAuthorAgreement.assert_called_once()  # "  3: Sign Transaction"
    signSendTxn.assert_called_once()  # "  3: Send to Ledger"
    monkeypatch.setattr("builtins.input", lambda _: "4")
    listNetworks.assert_called_once()  # "  4: Add Network"
    createPool.assert_called_once()  # "  4: Add Network"
    monkeypatch.setattr("builtins.input", lambda _: "5")
    listPools.assert_called_once()  # "  5: Connect to a Network"
    openPool.assert_called_once()  # "  5: Connect to a Network"
    monkeypatch.setattr("builtins.input", lambda _: "6")
    createWallet.assert_called_once()  # "  6: Create Wallet"
    monkeypatch.setattr("builtins.input", lambda _: "7")
    openWallet.assert_called_once()  # "  7: Open Wallet"
    monkeypatch.setattr("builtins.input", lambda _: "8")
    createDid.assert_called_once()  # "  8: Create DID"
    monkeypatch.setattr("builtins.input", lambda _: "9")
    listDids.assert_called_once()  # "  9: Use DID"
    monkeypatch.setattr("builtins.input", lambda _: "10")
    displayMenu.assert_called_once()  # " 10: Display Menu"
    monkeypatch.setattr("builtins.input", lambda _: "q")
    assert main.author == "0"  # "  q: Quit"


def test_bar():
    assert True
