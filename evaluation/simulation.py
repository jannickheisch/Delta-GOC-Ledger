import argparse
import os
import pandas as pd
import gzip
import subprocess
import time
import logging
import shutil
import sys
from logging.handlers import RotatingFileHandler
import re
from git import Repo
import json
from git import Repo

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

# Paths to repository and executables
GOC_EXECUTABLES_PATH="../git-goc"
GOC_SINGLE_REPO_EXECUTABLES_PATH="./single-repo-git-goc"
DELTA_GOC_EXECUTABLES_PATH="../git-goc-delta"
DELTA_GOC_SINGLE_REPO_EXECUTABLES_PATH="./single-repo-git-goc-delta"
GOC_REPO_DIR= os.path.join(SCRIPTDIR, "./accounts")
DELTA_GOC_REPO_DIR=os.path.join(SCRIPTDIR, "./delta-accounts")

# setup logger
logger = logging.getLogger("simulator")

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%H:%M:%S %d-%m-%Y',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])


# parse args
parser = argparse.ArgumentParser()
parser.add_argument("db_path", type=str)
parser.add_argument("--tmp_path", type=str, default="./tmp", required=False)
parser.add_argument("--results_path", type=str, default="./results", required=False)
parser.add_argument("--delta", action='store_true', required=False)
args = parser.parse_args()
try:
    shutil.rmtree(args.tmp_path, ignore_errors=True)
    shutil.rmtree(args.results_path, ignore_errors=True)
except FileNotFoundError:
    pass

# create tmp and results folder
os.mkdir(args.tmp_path)
os.mkdir(args.results_path)

# Helper class for executing the GOC ledger operations and performing measurements
class GOC():

    def __init__(self, single_repo_exec_path, account_dir, full_exec_path=None):
        self.path = single_repo_exec_path # path to GOC code
        self.account_dir = account_dir # path to GOC account dir
        self.full_exec_path = full_exec_path
        self.tmp_path = os.path.join(args.tmp_path, self.path.split("/")[-1]) # path to tmp dir
        os.mkdir(self.tmp_path)
        self.results_path = os.path.join(args.results_path, self.path.split("/")[-1]) # path to results dir
        os.mkdir(self.results_path)
        self.size_measure_file = os.path.join(self.results_path, "size_measurements.csv")
        self.git_sizer_measurements_file = os.path.join(self.results_path, "git_sizer_measurements.csv")
        self.phases_file =  os.path.join(self.results_path, "simulation_phases.csv")
        self.bundle_dir= os.path.join(self.results_path, "bundles")
        self.delta_old_refs= None
        self.delta_bundle_dir= os.path.join(self.results_path, "delta_bundles")
        os.mkdir(self.bundle_dir)
        self.accounts = []
        self.merge_needed = []
        self.num_of_token_operations = 0
        self.num_of_exec = 0
        # for measurement logging
        self.num_of_token_init = 0
        self.num_of_token_create= 0
        self.num_of_token_burn = 0
        self.num_of_token_giveTo= 0
        self.num_of_token_ackFrom = 0
        self.size_measurements = [] #pd.DataFrame(columns=["num_of_operations", "size_bundle_file", "size_pack_file", "size_unpacked_repo", "#init", "#create", "#burn", "#giveTo", "#ackFrom"])
        self.simulation_overview = []
        self.simulation_phases = []
        self.git_sizer_measurements = []
        shutil.rmtree(self.account_dir, ignore_errors=True)

        # if a path to the full goc executables (one author per repo) exists
        if full_exec_path:
            self.time_measurements_file=os.path.join(self.results_path, "time_measurements.csv")
            self.time_measurements=[]
            subprocess.call([os.path.join(full_exec_path, "author-initialize"), os.path.join(self.tmp_path, "sync_repo") ,"sync"])
            self.sync_repo=os.path.join(self.tmp_path, "sync_repo")




    def executeCommand(self, cmd):
        cmd = [str(i) for i in cmd] # make sure that every part of the command is a string
        cmd[0] = os.path.join(self.path, cmd[0])
        logger.debug("executing: %s", cmd) 
        exec = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out, err = exec.communicate()
        self.num_of_exec += 1
        logger.debug(out.decode())
        if self.num_of_token_operations % 200 == 0:
            self.measureRepoSize()
        if exec.returncode != 0:
            logger.fatal(f"Error executing command: {err.decode()}")
            #os._exit(1)

    def author_init(self, author_alias):
        cmd = ["initialize-author", self.account_dir, author_alias]
        self.executeCommand(cmd)
        self.num_of_token_operations += 1
        self.accounts.append(author_alias)
        # setup git remote
        if len(self.accounts) == 1 and self.full_exec_path:
            subprocess.call(["git", "remote", "add", "sync", os.path.join(SCRIPTDIR, self.sync_repo)], cwd=self.account_dir)


    def token_init(self, author_alias, token_alias):
        cmd = ["token-initialize", self.account_dir, author_alias, token_alias]
        self.executeCommand(cmd)
        self.num_of_token_operations += 1
        self.num_of_token_init += 1

    def token_create(self, author_alias, token_alias, amount):
        cmd = ["token-create", self.account_dir, token_alias, author_alias, amount]
        self.executeCommand(cmd)
        self.num_of_token_operations += 1
        self.num_of_token_create += 1
    
    def token_burn(self, author_alias, token_alias, amount):
        cmd = ["token-burn", self.account_dir, token_alias, author_alias, amount]
        self.executeCommand(cmd)
        self.num_of_token_operations += 1
        self.num_of_token_burn += 1

    def token_giveTo(self, author_alias, token_alias, receiver_alias, amount):
        cmd = ["token-giveTo", self.account_dir, token_alias, author_alias, receiver_alias, amount]
        self.executeCommand(cmd)
        self.num_of_token_operations += 1
        self.num_of_token_giveTo += 1

    def token_ackFrom(self, author_alias, token_alias, sender_alias):
        cmd = ["token-ackFrom", self.account_dir, token_alias, author_alias, sender_alias]
        self.executeCommand(cmd)
        self.num_of_token_operations += 1
        self.num_of_token_ackFrom += 1
    
    def check_balance(self, simulated_balance):
        is_balance_correct=True
        for (id, tokenID), expected_balance in simulated_balance.items():
            balance = self.getBalance(id, tokenID)
            if (balance != expected_balance):
                is_balance_correct=False
                logger.warning("Balance missmatch for account '%s'/'%s', expected: %s, actual: %s "
                                , id, tokenID, expected_balance, balance)
        return is_balance_correct


    def getBalance(self, account, tokenID):
        cmd = [os.path.join(self.path, "account-balance"), self.account_dir, str(tokenID), str(account)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        balance = output.decode()
        if not balance:
            return 0
        return int(balance)
 
    def create_overview(self, f_name, num_init_account, num_init_token, num_create, num_transactions):
        self.simulation_overview.append([f_name, num_init_account, num_init_token, num_create, num_transactions])
        csv = pd.DataFrame(self.simulation_overview, columns=["f_name", "num_init_account", "num_init_token", "num_create", "num_transactions"])
        csv.to_csv(os.path.join(self.results_path, "simulation_overview.csv"), index=False)
            
    def log_phase(self, f_name, phase_name):
        self.simulation_phases.append([f_name, phase_name, self.num_of_token_operations])
        csv = pd.DataFrame(self.simulation_phases, columns=["f_name", "phase_name", "num_operations"])
        csv.to_csv(self.phases_file, index=False)

    def measureRepoSize(self):
        # git-sizer -j --json-version=2 --branches 2> /dev/null
        logger.info("start measurements (%s ops)", self.num_of_token_operations)

        # create full bundle, measure num of objects and deltas
        logger.debug("create bundle")
        bundle_cmd=["git", "bundle", "create", "--progress", "-", "--branches"]
        bundle_p = subprocess.Popen(bundle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.account_dir)
        output, err = bundle_p.communicate()
        info_msg = err.decode()
        pattern= r'Total (\d+) \(delta (\d+)\)'
        try:
            num_objects, num_deltas = re.findall(pattern, info_msg)[0]
        except IndexError:
            logger.fatal("error reading num of deltas: %s", info_msg)
            os._exit(1)

        bundle_file_bytes = output

        bundle_path = os.path.join(self.bundle_dir, f"{self.num_of_token_operations}.bundle")

        # clone bundle and measure uncompressed size
        tmp_repo = os.path.join(self.tmp_path, "measure_repo")
        tmp_bundle = os.path.join(self.tmp_path, "measure.bundle")
        logger.debug("write bundlefile")
        with open(bundle_path, "wb") as f:
            f.write(bundle_file_bytes)
        
        with open(tmp_bundle, "wb") as f:
            f.write(bundle_file_bytes)
        logger.debug("clone repo")
        clone_cmd=["git", "clone", "measure.bundle", "measure_repo"]
        clone_p = subprocess.Popen(clone_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.tmp_path)
        clone_p.wait()

        packfile_name=""
        for f in os.listdir(f"{tmp_repo}/.git/objects/pack"):
            if f.endswith(".pack"):
                packfile_name=f
            os.rename(f"{tmp_repo}/.git/objects/pack/{f}", f"{tmp_repo}/{f}")

        pack_size=os.path.getsize(os.path.join(tmp_repo, packfile_name))
        logger.debug("unpack objects")
        unpack_cmd = f"git unpack-objects < {packfile_name}"
        unpack_p = subprocess.Popen(unpack_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tmp_repo, shell=True)
        unpack_p.communicate()

        size_cmd = ["du", "-sb", ".git"]
        size_p = subprocess.Popen(size_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tmp_repo)
        output, err = size_p.communicate()
        repo_size=int(output.decode().split("\t")[0])
        logger.debug("fetch refs")


        # compute delta bundle
        delta_bundle_p= subprocess.Popen('git bundle create - --branches --not --glob="refs/measurement/*"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.account_dir)
        output, err = delta_bundle_p.communicate()
        delta_bundle_size=len(output)

        # fetch all frontier refs into separate refs, to exclude them in the next measurement
        fetch_p = subprocess.Popen('git fetch --no-auto-maintenance --no-auto-gc . "refs/heads/*:refs/measurement/*"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.account_dir)
        _ , _ = fetch_p.communicate()

        #git-sizer measurements
        git_sizer_cmd=["git-sizer", "-j", "--json-version=2", "--branches"]
        git_sizer_p= subprocess.Popen(git_sizer_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.account_dir)
        output, err = git_sizer_p.communicate()

        naive_tree_size=0
        repo = Repo(self.account_dir)
        for head in repo.heads:
            ref = head.path
            for commit in repo.iter_commits(ref, first_parent=True):
                commit_tree=commit.tree
                naive_tree_size += commit_tree.size

                for tree in commit_tree.trees:
                    naive_tree_size += tree.size

        measurements_json=json.loads(output.decode())
        
        #save git_sizer measurements
        self.git_sizer_measurements.append([self.num_of_token_operations, measurements_json['uniqueBlobCount']['value'], measurements_json['uniqueBlobSize']['value'], measurements_json['uniqueTreeCount']['value'],
                                             measurements_json['uniqueTreeEntries']['value'], measurements_json['uniqueTreeSize']['value'], measurements_json['uniqueCommitCount']['value'], measurements_json['uniqueCommitSize']['value'], naive_tree_size ])
        git_sizer_csv= pd.DataFrame(self.git_sizer_measurements, columns=['num_of_operations', 'uniqueBlobCount', 'uniqueBlobSize', 'uniqueTreeCount', 'uniqueTreeEntries', 'uniqueTreeSize', 'uniqueCommitCount', 'uniqueCommitSize', 'naiveTreeSize'])
        git_sizer_csv.to_csv(self.git_sizer_measurements_file, index=False)

        # measure time required to update other replica
        if self.full_exec_path and len(self.accounts) > 0:
            logger.debug("measure push time")
            #measure push
            push_start_time=time.time()
            subprocess.call([os.path.join(self.path, "repo-push"), self.account_dir, self.accounts[0], "sync"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            push_finish_time=time.time()
            push_time=push_finish_time - push_start_time

            logger.debug("measure merge time")
            # measure merge frontier
            merge_start_time=time.time()
            subprocess.call([os.path.join(self.full_exec_path, "repo-merge"), os.path.join(SCRIPTDIR, self.sync_repo)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            merge_finish_time=time.time()
            merge_time=merge_finish_time-merge_start_time

            logger.debug("measure checkpoint time")
            #get all existing accounts
            get_refs_p=subprocess.Popen('git for-each-ref --format="%(refname)" "refs/heads/frontier/*/*"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.sync_repo)
            out, err = get_refs_p.communicate()
            refs = out.decode().split("\n")[:-1]
            accounts= []
            for ref in refs:
                split = ref.split("/")
                authorID = split[-1]
                tokenID = split[-2]
                accounts.append((tokenID, authorID))

            #measure checkpoint computation
            checkpoint_start_time=time.time()
            for acc in accounts:
                tokenID, authorID = acc
                subprocess.call([os.path.join(self.full_exec_path, "account-checkpoint"), self.sync_repo, tokenID, authorID])
            checkpoint_finish_time=time.time()
            checkpoint_time=checkpoint_finish_time-checkpoint_start_time

            self.time_measurements.append([self.num_of_token_operations, push_time, merge_time, checkpoint_time])
            csv = pd.DataFrame(self.time_measurements, columns=["num_of_operations", "push_time", "merge_time", "checkpoint_time"])
            csv.to_csv(self.time_measurements_file, index=False)


        # save measurements
        logger.debug("save csv")
        self.size_measurements.append([self.num_of_token_operations, len(bundle_file_bytes), int(num_objects), int(num_deltas), pack_size, repo_size, self.num_of_token_init, self.num_of_token_create, self.num_of_token_burn, self.num_of_token_giveTo, self.num_of_token_ackFrom, delta_bundle_size])
        csv = pd.DataFrame(self.size_measurements, columns=["num_of_operations", "size_bundle_file", "num_objects", "num_deltas", "size_pack_file", "size_unpacked_repo", "#init", "#create", "#burn", "#giveTo", "#ackFrom", "delta_bundle_size"])
        csv.to_csv(self.size_measure_file, index=False)

        logger.debug("wiping repo")
        os.remove(tmp_bundle)
        shutil.rmtree(tmp_repo)
        logger.debug("measurement finished")


# performs the simulations with the already computed simulation data
def simulate(exec: GOC, f_name, need_init_account, need_init_token, need_create, transactions):

    # 1. author init phase
    exec.create_overview(f_name, len(need_init_account), len(need_init_token), len(need_create), len(transactions))
    exec.log_phase(f_name, "author_init")
    for accID in need_init_account:
        exec.author_init(accID)
    
    # 2. token init phase
    exec.log_phase(f_name, "token_init")
    for (accID, tokenID) in need_init_token:
        exec.token_init(accID, tokenID)
    
    # 3. token create phase
    exec.log_phase(f_name, "token_create")
    for acc, amount in need_create.items():
        accID, tokenID = acc
        exec.token_create(accID, tokenID, amount)
    
    # 4. transaction phase
    exec.log_phase(f_name, "transactions_start")
    for sender, recipient, token_address, value in transactions:

        #create
        if sender == "0000000000000000000000000000000000000000":
            exec.token_create(recipient, token_address, value)
            continue
        #burn
        if recipient == "0000000000000000000000000000000000000000":
            exec.token_burn(sender, token_address, value)
            continue
        exec.token_giveTo(sender, token_address, recipient, value)
        exec.token_ackFrom(recipient, token_address, sender)
    exec.log_phase(f_name, "transactions_end")





# setup simulation
num_of_transactions = 0


if args.delta:
    goc = GOC(DELTA_GOC_SINGLE_REPO_EXECUTABLES_PATH, DELTA_GOC_REPO_DIR)
else:
    goc = GOC(GOC_SINGLE_REPO_EXECUTABLES_PATH, GOC_REPO_DIR)

# cached information needed to simulate the transactions
simulated_balance = {} # {(accID, tokenID): balance)}
existing_token = [] # [tokenID]
existing_accounts = [] # [accountID]

start_time = time.time()
logger.info("Start: %s", start_time)

# iterate over all files in specified directory, we expect that the files are stored as provided by Blockchair 
# (every day is stored as a single .tsv.gz file in the data directory)
for path in sorted(os.listdir(args.db_path)):
    if not path.endswith(".tsv.gz"):
        logger.error("File %s is not valid", path)
        continue

    logger.info("Opening %s", path)

    # simulate transactions in python and generate auxiliary data later used for simulating transaction with the GOC-Ledger
    with gzip.open(os.path.join(args.db_path, path), "r") as f:
        data = pd.read_csv (f, sep = '\t', converters={'value': int}) # block_id, transaction_hash, time, token_address, token_name, token_symbol, token_decimals, sender, recipient, value
        
        need_init_token = [] # [(accId, tokenID)]
        need_init_account = [] # [accountID]
        need_create = {} # {(accId, tokenID): value}
        transactions = [] # [[sender, receiver, tokentype, value]]
        

        for idx, transaction in data.iterrows():

            if transaction.value == 0:
                continue

            if transaction.sender == "0000000000000000000000000000000000000000" and transaction.recipient == "0000000000000000000000000000000000000000":
                continue

            if transaction.sender not in existing_accounts and transaction.sender != "0000000000000000000000000000000000000000":
                need_init_account.append(transaction.sender)
                existing_accounts.append(transaction.sender)
            
            if transaction.recipient not in existing_accounts and transaction.recipient != "0000000000000000000000000000000000000000":
                need_init_account.append(transaction.recipient)
                existing_accounts.append(transaction.recipient)


            # represents create op
            if transaction.sender == "0000000000000000000000000000000000000000":
                curr_balance = simulated_balance.get((transaction.recipient, transaction.token_address), 0)

                new_balance = curr_balance + transaction.value

                if transaction.token_address not in existing_token:
                    need_init_token.append((transaction.recipient, transaction.token_address))
                    existing_token.append(transaction.token_address)

                

                transactions.append([transaction.sender, transaction.recipient, transaction.token_address, transaction.value])
                simulated_balance[(transaction.recipient, transaction.token_address)] = new_balance
                continue
            

            # represents burn op
            if transaction.recipient == "0000000000000000000000000000000000000000":
                curr_balance = simulated_balance.get((transaction.sender, transaction.token_address), 0)
                new_balance = curr_balance - transaction.value
                if new_balance < 0:
                    already_needed = need_create.get((transaction.sender, transaction.token_address), 0)
                    need_create[(transaction.sender, transaction.token_address)] = already_needed + abs(new_balance)
                    new_balance = 0
                transactions.append([transaction.sender, transaction.recipient, transaction.token_address, transaction.value])
                simulated_balance[(transaction.sender, transaction.token_address)] = new_balance
                continue
            

            #perform transaction
            sender_balance = simulated_balance.get((transaction.sender, transaction.token_address), 0)
            receiver_balance = simulated_balance.get((transaction.recipient, transaction.token_address), 0)

            diff = sender_balance - transaction.value

            if diff < 0:
                already_needed = need_create.get((transaction.sender, transaction.token_address), 0)
                need_create[(transaction.sender, transaction.token_address)] = already_needed + abs(diff)
                sender_balance = 0
            else:
                sender_balance -= transaction.value

            if transaction.token_address not in existing_token:
                need_init_token.append((transaction.sender, transaction.token_address))
                existing_token.append(transaction.token_address)
            
            # update simulated balance
            simulated_balance[(transaction.sender, transaction.token_address)] = sender_balance
            receiver_balance = simulated_balance.get((transaction.recipient, transaction.token_address), 0) # get updated balance, because the sender and receiver could be equal
            receiver_balance += transaction.value

            transactions.append([transaction.sender, transaction.recipient, transaction.token_address, transaction.value])
            simulated_balance[(transaction.recipient, transaction.token_address)] = receiver_balance

        logger.debug("simulated_balance: %s", simulated_balance)
        logger.debug("need_init_token: %s", need_init_token)
        logger.debug("need_create %s", need_create)
    num_of_transactions += len(data.index)

    simulate(goc, f.name, need_init_account, need_init_token, need_create, transactions)


    # at the end of each simulated day, we check if the expected balance value matches with the simulated balance of the GOC-Ledger.
    logger.info("checking balance")
    if not goc.check_balance(simulated_balance):
        logger.fatal("Error missmatch between simulated balance and actual balance")
        os._exit(1)
        
    logger.info("Num op (goc): %s", goc.num_of_token_operations)
    logger.info("Num transactions: %s", num_of_transactions)


end_time=time.time()
logger.info("End: %s", end_time)
delta_time=end_time - start_time
logger.info("Duration: %s", delta_time)
shutil.rmtree(args.tmp_path,ignore_errors=True)
