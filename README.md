# Delta-GOC-Ledger using Git

Implementation of the Delta-GOC-Ledger using Git as part of my master's thesis *Delta-GOC-Ledger: Incremental Checkpointing and Lower Message Sizes for Grow-Only Counters Ledgers with Delta-CRDTs*.

## Overview

This repository is structured as follows:

* [Evaluation](/evaluation/): evaluation source code and corresponding results.
* [Git-goc-delta](/git-goc-delta/): the implementation of the delta-based GOC-Ledger, consisting of multiple Bash scripts.
* [Git-goc-state](/git-goc-state/): the implementation of the state-based GOC-Ledger.

In addition, we provide a prototype ([delta-goc](/git-goc-delta/) and [state-goc](/git-goc-state/)) that combines those Bash scripts in a simple command line application.

## Quick Start

In this section the usage of this implementation is demonstrated with an example. The Delta-Goc-Ledger implementation and the state-based GOC-Ledger support the same basic token operations. Therefore, in the following examples, `delta-goc` can be replaced by `state-goc` to utilize the corresponding state-based GOC-Ledger operations.

We initialize two authors `alice` and `bob`:

````bash
delta-goc author init alice
delta-goc author init bob
````

`bob` pushes updates (the published alias) to `alice`:

````bash
delta-goc repo remote bob alice
delta-goc repo push bob alice
````

`alice` merges the received updates:

````bash
delta-goc repo merge alice
````

`alice` initializes a new token with alias `test-token` and subsequently creates 10 tokens, burns 3 and gives 5 to `bob`

````bash
delta-goc token init alice test-token
delta-goc token create alice test-token 10
delta-goc token burn alice test-token 3
delta-goc token giveto alice test-token bob 5
````

`alice` sends the updates to `bob` and `bob` merges them:

````bash
delta-goc repo remote alice bob
delta-goc repo push alice bob
delta-goc repo merge bob
````

`bob` acknowledges the token of `alice` and sends an update:

````bash
delta-goc token ackfrom bob test-token alice
delta-goc repo push bob alice
delta-goc repo merge alice
````

`alice` computes the balance of bob:

````bash
delta-goc token balance alice test-token bob
````

## Usage

In this section the different operations supported by the prototypes are explained. Most of the delta-based operations are also available in the state-based implementation. Therefore, in the following commands, the `delta-goc` can be replaced by `state-goc`, unless stated otherwise, to use the corresponding state-based operation.

In general, every command is provided as: ``delta-goc <operation type> <operation> [operation arguments]``

In the following, the four different main command categories *author*, *token*, *repo*, and *config* are presented.

### Author

#### `delta-goc author init <author alias>`

This initializes a new author by creating a new repository and publishing the specified alias.

### Token Operations

#### `delta-goc token init <author alias> <token alias>`

Initializes a new token type and assigns a specified token alias.

#### `delta-goc token create <author alias> <token alias> <amount>`

Creates the given `<amount>` of tokens of type `<token alias>` for the author `<author alias>`.

#### `delta-goc token burn <author alias> <token alias> <amount>`

Burns the given `<amount>` of tokens of type `<token alias>` for the author `<author alias>`.

#### `delta-goc token giveto <sender alias> <token alias> <recipient alias> <amount>`

Sends the given `<amount>` of tokens of type `<token alias>` from author `<sender alias>` to `<recipient alias>`.

#### `delta-goc token ackFrom <recipient alias> <token alias> <sender alias>`

Acknowledges all unacknowledged token fo type `<token alias>` received from `<sender alias>` by `recipient alias`.

#### `delta-goc token balance <author alias> <token alias> <query author alias>`

Computes the balance for token type `<token alias>` belonging to author `<query author alias>` in the current repository state of the author `<query author alias>`.

#### (**Delta-Goc-Only:**) `delta-goc token checkpoint <author alias> <token alias> <checkpoint author alias>`

Computes the current checkpoint, i.e. the latest full account state for author `<checkpoint author alias>` and token type `<token alias>` in the repository of author `<author alias>`.

#### `delta-goc token visualize <author alias> <token alias> [target author alias]`

Shows the commit graph of the specified token `<token alias>` in the repository of author `<author alias>`, on which the implementations operates on. If `[target author alias]``is specified, the append-only log for this author is displayed instead (subset of the entire token commit graph). This command is especially useful for understanding and debug the implementation. Can be combined with the [debug-mode](#configuration), to display additional information.

### Replication Methods

The following commands are used for replicating the current frontier states between authors.

> [!NOTE]
> These commands assume that the repository of the recipient is located in the *accounts directory*, specified in the `delta-goc` or `state-goc` script. However, since the replication is based on Git, the used Git commands (`git remote`, `git push`, `git fetch`) can be easily adapted to support additional protocols (e.g. https, ssh).

#### `delta-goc repo remote <author alias> <remote author alias>`

Adds the author `<remote author alias>` as a Git remote for the repository of `<author alias>`.

#### `delta-goc repo push <sender alias> <recipient alias>`

Pushes the current frontier of `<sender alias>` to `<recipient alias>`.

#### `delta-goc repo pull <recipient alias> <target alias> <target author ID>`

Pulls the current frontier of `<target alias>` with author ID `<target author ID>` to `<recipient alias>`.

#### `delta-goc repo broadcast <author alias>`

Pushes the current frontier to all known remotes.

#### `delta-goc repo merge <author alias> [remote author alias]`

Merges the received frontier with the local frontier at author `<author alias>`. If `[remote author alias]` is specified, only the updates of this author are merged (if the alias of this author is known). Otherwise, the updates of all authors are merged.

### Configuration

#### `delta-goc config <author alias> <config-name> [new-value]`

Sets the config `<config-name>` of the author `<author alias>` to the value `[new-value]`. If no value is specified, the current configuration value is returned.

Possible configurations:

* **autoMergeUpdates**: Whether updates received via pushing should be automatically merged with the current frontier state, i.e. the author does not need to explicitly call `delta-goc repo merge`.
  **Possible Values:** true, false  
  **Default Value:** false  

* **debug**: Whether the debug mode is enabled. The debug mode adds the name of the performed operation to the commit message, which can be helpful to debug the application, but increases message sizes.
  **Possible Values:** true, false  
  **Default Value:** false  

### Other

#### `delta-goc reset`

Removes the accounts directory, i.e. the repositories of all existing accounts.

## Dependencies

* Git (Tested with version 2.34.1)
* Bash
* OpenSSH (Tested with OpenSSH_8.9p1 Ubuntu-3ubuntu0.6, OpenSSL 3.0.2 15 Mar 2022)
* Python3 (for arithmetical operations)
