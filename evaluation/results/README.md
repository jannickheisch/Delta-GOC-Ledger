# Simulation measurements

The measurements of the simulation for the [delta-based](./single-repo-git-goc-delta/) and [state-based](./single-repo-git-goc/) implementations.

In the following the different files are explained.

## size_measurements.csv ([delta-based](./single-repo-git-goc-delta/size_measurements.csv) | [state-based](./single-repo-git-goc/size_measurements.csv))

This file contains various measurements performed by the simulation application.

| Column  | Description |
| ------------- | ------------- |
| num_of_operations  | **[Primary key]** Number of executed token operations  |
| size_bundle_file  | Size of the measured total bundle file (containing the entire commit history)  |
| num_objects  | Number of all distinct Git objects  |
| num_deltas  | Number of Git objects, that are stored in a delta-chain  |
| size_pack_file  | Size of the pack file contained in the bundle file  |
| size_unpacked_repo  | Size of a unpacked (uncompressed) repository, containing all ledger objects (all objects referenced by refs/heads/*)  |
| #init  | Number of token initialize operations  |
| #create  | Number of create token operations  |
| #burn  | Number of burn token operations  |
| #giveTo  | Number of giveTo token operations  |
| #ackFrom  | Number of ackFrom token operations  |
| delta_bundle_size  | Size of the incremental bundle file size (includes 200 token operations each)  |

## git_sizer_measurements.csv ([delta-based](./single-repo-git-goc-delta/git_sizer_measurements.csv) | [state-based](./single-repo-git-goc/git_sizer_measurements.csv))

For more information about specific git-sizer metrics, refer to [git-sizer](https://github.com/github/git-sizer).

| Column  | Description |
| ------------- | ------------- |
| num_of_operations  | **[Primary key]** Number of executed token operations  |
| uniqueBlobCount  | Number of blob distinct objects  |
| uniqueBlobSize  | Total size of all distinct blob objects  |
| uniqueTreeCount  | Number of distinct tree objects  |
| uniqueTreeEntries  | Total number of entries in all distinct tree objects  |
| uniqueTreeSize  | Total size of all distinct tree objects  |
| uniqueCommitCount  | Number of distinct commit objects  |
| uniqueCommitSize  | Total size of all distinct commit objects  |
| naiveTreeSize  | Total size of all referenced tree objects (including duplicates)  |

## naive_sizes.csv ([delta-based](./single-repo-git-goc-delta/naive_sizes.csv) | [state-based](./single-repo-git-goc/naive_sizes.csv))

Shows the "naive" (i.e. assuming Git would not reuse objects) sizes and number of blob and tree objects, calculated by the [naive_blobs.py](../naive_blobs.py) script.

| Column  | Description |
| ------------- | ------------- |
| num_of_operations  | **[Primary key]** Number of executed token operations  |
| naive_blob_count  | "Naive" number of blob objects  |
| naive_blob_size  | "Naive" size of blob objects |
| naive_tree_count  | "Naive" number of tree objects  |
| naive_tree_size  | "Naive" size of tree objects  |

## simulation_overview.csv ([delta-based](./single-repo-git-goc-delta/simulation_overview.csv) | [state-based](./single-repo-git-goc/simulation_overview.csv))

Gives an overview of the amount of different operations that are executed by the simulation.

| Column  | Description |
| ------------- | ------------- |
| f_name  | **[Primary key]** Name of the file containing the ERC-20 transaction data for the simulated day (it is possible to simulate multiple subsequent days)  |
| num_init_account  | Number of new authors that needs to be initialized  |
| num_init_token  | Number of tokens that needs to be initialized  |
| num_create  | Number of create operations that need to be executed, in order to supply the accounts with sufficient balance for the transaction phase. |
| num_transactions  | Number of simulated ERC-20 transactions |

## simulation_phases.csv ([delta-based](./single-repo-git-goc-delta/simulation_phases.csv) | [state-based](./single-repo-git-goc/simulation_phases.csv))

Shows how many GOC-Ledger operations were executed in each simulation phase (described in Section 6.1.2).

**[Primary key]**: combination of `f_name` and `phase_name`

| Column  | Description |
| ------------- | ------------- |
| f_name  | Name of the file containing the ERC-20 transaction data for the simulated day (it is possible to simulate multiple subsequent days)  |
| phase_name  | Name of the simulation phase  |
| num_operations  | Number of simulated operations that were already executed, before starting the specified simulation phase  |
