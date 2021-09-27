# Indicio Network Transaction Wizard

## Transaction Workflow for a New Issuer

This workflow documents the process for a new Issuer to be on-boarded to an ecosystem. The new Issuer is a transaction author. A transaction author works with a transaction endorser to write the Issuer DID, a schema, and a credential definition to the network. If an appropriate schema already exists on the ledger, it can be used instead of writing a redundant copy of the schema to the ledger for each issuer.
```plantuml
participant "Transaction Author" as Author
participant "Transaction Endorser" as Endorser
participant "Hyperledger\nIndy Network" as Network

note over Author: Select network
note over Author: Build Schema Transaction
Author -> Endorser: Author DID + Schema Transaction
Endorser -> Network: Author DID
note over Endorser: Sign Schema Transaction
Endorser -> Author: Signed Schema Transaction
Author -> Network: Signed Schema Transaction

note over Author: Build Credential Definition Transaction
Author -> Endorser: Credential Definition Transaction
note over Endorser: Sign Credential Definition Transaction
Endorser -> Author: Signed Credential Definition Transaction
Author -> Network: Signed Credential Definition Transaction
```