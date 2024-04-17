# Delta-GOC-Ledger Evaluation

Source code and results concerning the evaluation of the delta-based and state-based GOC-Ledger implementation.

## Overview

* [Blockchair_dataset](./blockchair_dataset/): directory containing the ERC-20 transactions dataset from [Blockchair](https://gz.blockchair.com/ethereum/erc-20/transactions/) used for the evaluation.
* [Results](./results/): directory with the documented measurements that were conducted during the simulation.
* [Single-repo-git-goc](./single-repo-git-goc/): a modified version of the state-based GOC-Ledger implementation, which performs all operations in a single repository.
* [Single-repo-git-goc-delta](./single-repo-git-goc-delta/): a modified version of the delta-based GOC-Ledger implementation, which performs all operations in a single repository.
* [naive_blobs.py](./naive_blobs.py): script to determine "naive" size of blobs based on the bundle files created during simulation (could be implemented in simulation.py)
* [simulation.py](./simulation.py): script that simulates real ERC-20 transactions using the GOC-Ledger and conducts different measurements.
* [figures.py](./figures.py): script that analyzes the result data and generates the figures presented in the thesis.

## Evaluation

In this section, we give a brief overview of how the simulation was conducted. Please ensure that the directory paths specified in the scripts match your environment.

First, we run the simulation for the state-based approach:

````bash
python3 simulation.py ./blockchair_dataset
````

Then we re-run the simulation, but this time using the delta-based ledger:

````bash
python3 simulation.py --delta ./blockchair_dataset
````

Additionally, we developed a script to measure the "naive" blob sizes, without to rerun the experiments (only required for Fig. 6.8 b)):

````bash
python3 naive_blobs.py
````

Now the measurements that were taken throughout the simulations are stored in [results](./results/). We can now generate the figures:

````bash
python3 visualize.py
````

## Dependencies

In addition to the requirements for the GOC-ledger implementations, these dependencies are required for performing the simulation and visualize the resulting data:

* python3, with the following libraries:
  - pandas
  - GitPython
  - matplotlib
  - scikit-learn
* [git-sizer](https://github.com/github/git-sizer)