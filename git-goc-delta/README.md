# Delta-Goc-Ledger based on Git

This directory contains various Bash scripts implementing the different delta-based GOC-Ledger operations. The [git-hooks](./git-hooks/) directory contains Git hook scripts, that are copied to each repository when initializing a new author.

## Documentation

In the following, the different scripts are explained in alphabetical order.

### account-balance ([src](./account-balance))

````
account-balance [-v] <repo-path> <token type> [author-id]
````

Returns the current balance of the given account

`repo-path`: absolute path of the author repository  
`token type`: hash of the token  
`author-id`: (optional) the author, for which the balance should be computed; defaults to the author of this repository

### alias-get-author-id ([src](./alias-get-author-id))

````
alias-get-author-id <repo-path> <author-alias>
````

Returns the author identifier of the given alias. If no ID is found under the specified alias, exit code 1 is returned.

`repo-path`: absolute path of the author repository  
`author-alias`: alias of the author

### alias-get-token-id ([src](./alias-get-author-id))

````
alias-get-author-id <repo-path> <token-alias>
````

Returns the token identifier (hash of the initialization commit) of the given alias. If no ID is found under the specified alias, exit code 1 is returned.

`repo-path`: absolute path of the author repository  
`token-alias`: alias of the token

### author-initialize ([src](./author-initialize))

````
author-initialize <full-repo-path> <alias>
````

Initializes an author by setting up a new repository at the given directory, generating a ed25519 keypair and the for the Delta-GOC-Ledger required settings.  

Returns the ID (public key) of the initialized author.

`full-repo-path`: absolute path to the dictionary in which the new repository should be initialized  
`alias`: alias of the author

### repo-broadcast ([src](./repo-broadcast))

````
repo-broadcast <repo-path>
````

Pushes local frontier to any known remote.

`repo-path`: absolute path of the author repository

### repo-merge ([src](./repo-merge))

````
repo-merge <repo-path> [sender-id]
````

Merges the updates of the remote frontier with the local frontier, while verifying that the resulting frontier is correct.

`repo-path`: absolute path of the author repository  
`sender-id`: (optional) the author id of the sender of whose updates should be merged; if not set, the frontier of every remote will be merged

### repo-pull ([src](./repo-pull))

````
repo-pull <repo-path> <remote> <remote-author-id>
````

Fetches the remote frontier of the given remote.

`repo-path`: absolute path of the author repository  
`remote`: name of the git remote  
`remote-author-id`: the author id of the remote

### repo-push ([src](./repo-push))

````
repo-push <repo-path> <remote>
````

Pushes the local frontier to the given remote.

`repo-path`: absolute path of the author repository  
`remote`: name of the git remote

### token-ackFrom ([src](./token-ackFrom))

````
token-ackFrom <repo-path> <token-type> <sender-id> <amount>
````

Acknowledges all received tokens from the given sender, which are not already acknowledged.  
Exists with exit code 0 on success or exit code 1 on error. If all received tokens are already acknowledged, exit code 2 is returned.

`repo-path`: absolute path of the author repository  
`token-type`: hash of the token  
`sender-id`: the author id of the sender  
`amount`: the number of tokens that should be burned

### token-burn ([src](./token-burn))

````
token-burn <repo-path> <token type> <amount>
````

Creates the number of tokens for this account.  
Exists with exit code 0 on success or exit code 1 on error. If the account has insufficient balance, error code 2 is returned.

`repo-path`: absolute path of the author repository  
`token type`: hash of the token  
`amount`: the number of tokens that should be burned

### token-create ([src](./token-create))

````
token-create <repo-path> <token type> <amount>
````

Creates the number of tokens for this account.

`repo-path`: absolute path of the author repository  
`token type`: hash of the token  
`amount`: the number of tokens that should be created

### token-giveTo ([src](./token-giveTo))

````
token-giveTo <repo-path> <token-type> <recipient-id> <amount>
````

Transfers the desired amount of tokens to the specified account.  
Exists with exit code 0 on success or exit code 1 on error. If the account has insufficient balance for the transfer, error code 2 is returned.

`repo-path`: absolute path of the author repository  
`token-type`: hash of the token  
`recipient-id`: the author id of the recipient  
`amount`: the number of tokens that should be burned

### token-initialize ([src](./token-initialize))

````
token-initialize <repo-path> <alias>
````

Initializes a new token, with the requested alias. The SHA-1 hash of the commit is the ID of the initialized token.  
Returns the ID of the initialized token.

`repo-path`: absolute path where the directory and repository of this author should be initialized  
`alias`: alias of the initialized token

### Utilities

This folder contains additional scripts, that are rarely called from outside the implementation.

#### add-allowed-pubkey ([src](./utility/add-allowed-pubkey))

````
add-allowed-pubkey <public-key> [type]
````

Adds the given public-key to the allowed-signers file of this repository

`repo-path`: absolute path of the author repository  
`public-key`: public key that should be added to the allowed signers file  
`type`: (optional) type of the public key; defaults to 'ssh-ed25519'

#### key-sha256-fingerprint ([src](./utility/key-sha256-fingerprint))

````
key-sha256-fingerprint [--no-prefix] <repo-path> <public-key> [type]
````

Computes and returns the sha256 hash of the given public key. Computed hashes are cashed, meaning that subsequent calls with the same public key will not recompute the hash.

`repo-path`: absolute path of the author repository  
`public-key`: public key that should be added to the allowed signers file  
`type`: (optional) type of the public key; defaults to 'ssh-ed25519'

`--no-prefix`: returns the SHA256 hash without the "SHA256:" prefix

#### ls-tree-format ([src](./utility/ls-tree-format))

````
ls-tree-format [-b blob_sha1:path] [-t tree_sha1:path] 
````

Creates a tree consisting of the given blobs and trees and returns it in the ls-tree format, without writing it to any index file. The created tree is also not written to the object db.
Note: There is no validation if the created tree points to valid objects, it just converts the input into the ls-tree format.

`[-b blob_sha1:path]`: (optional) adds a blob with hash `blob_sha1` and name `path` to the returned tree. Can be used multiple times.  
`[-t tree_sha1:path]`: (optional) adds a tree with hash `tree_sha1` and name `path` to the returned tree. Can be used multiple times.

#### show-commit-graph ([src](./utility/show-commit-graph))

````
show-commit-graph <repo-path> [author-id] 
````

Displays the commit graph of the specified token type in the terminal. If an author is specified, only the append-only log for this token-type and author is shown.

`repo-path`: absolute path of the author repository  
`token-type`: hash of the token  
`author-id`: id of the author
