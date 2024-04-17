import pandas as pd
import matplotlib.pyplot as plt
import shutil
import os
import math
import numpy as np
from sklearn.linear_model import LinearRegression

STATE_RESULTS_DIR="./results/single-repo-git-goc"
DELTA_RESULTS_DIR="./results/single-repo-git-goc-delta"
FIGURES_DIR="./figures"

shutil.rmtree(FIGURES_DIR, ignore_errors=True)
os.mkdir(FIGURES_DIR)

# read result data
state_GOC_size_data = pd.read_csv(os.path.join(STATE_RESULTS_DIR, "size_measurements.csv"))
delta_GOC_size_data = pd.read_csv(os.path.join(DELTA_RESULTS_DIR, "size_measurements.csv"))

state_GOC_gitsizer_data = pd.read_csv(os.path.join(STATE_RESULTS_DIR, "git_sizer_measurements.csv"))
delta_GOC_gitsizer_data = pd.read_csv(os.path.join(DELTA_RESULTS_DIR, "git_sizer_measurements.csv"))

#phases
#phase_data = pd.read_csv("simulation.phases")
start_init = 7935
start_create = 8016
start_transactions = 10935

xMax = state_GOC_size_data['num_of_operations'].max()

# Fig. 6.1 (Bundle file size)
bundle_data = state_GOC_size_data[['num_of_operations']].copy()
bundle_data = bundle_data.assign(state_bundle=state_GOC_size_data['size_bundle_file'].div(1000).round(2))
bundle_data = bundle_data.assign(delta_bundle=delta_GOC_size_data['size_bundle_file'].div(1000).round(2))

bundle_data.plot.line(x="num_of_operations", y=["state_bundle","delta_bundle"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.legend(["state", "delta"])
plt.xlim([0, xMax])
plt.ylim(bottom=0)

plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Size of bundle file in KB", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR, "bundle.png"), bbox_inches='tight')


# Fig. 6.2 (Total size of different git objects)
object_size_data = state_GOC_size_data[['num_of_operations']]
object_size_data = object_size_data.assign(state_blobs_size=state_GOC_gitsizer_data['uniqueBlobSize'].div(1000).round(2))
object_size_data = object_size_data.assign(state_trees_size=state_GOC_gitsizer_data['uniqueTreeSize'].div(1000).round(2))
object_size_data = object_size_data.assign(state_commits_size=state_GOC_gitsizer_data['uniqueCommitSize'].div(1000).round(2))

object_size_data = object_size_data.assign(delta_blobs_size=delta_GOC_gitsizer_data['uniqueBlobSize'].div(1000).round(2))
object_size_data = object_size_data.assign(delta_trees_size=delta_GOC_gitsizer_data['uniqueTreeSize'].div(1000).round(2))
object_size_data = object_size_data.assign(delta_commits_size=delta_GOC_gitsizer_data['uniqueCommitSize'].div(1000).round(2))

object_size_data.plot.line(x="num_of_operations", y=["state_blobs_size", "state_commits_size", "state_trees_size", "delta_trees_size"])
plt.legend(["state + delta blobs", "state + delta commits", "state trees", "delta trees"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])

plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Total size of distinct objects in KB", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR,"objects_size.png"), bbox_inches='tight')


# Fig. 6.3 a) (Total number of Git objects and delta objects)
general_object_data = state_GOC_size_data[['num_of_operations']]
general_object_data = general_object_data.assign(state_num_objects=state_GOC_size_data['num_objects'])
general_object_data = general_object_data.assign(state_num_deltas=state_GOC_size_data['num_deltas'])

general_object_data = general_object_data.assign(delta_num_objects=delta_GOC_size_data['num_objects'])
general_object_data = general_object_data.assign(delta_num_deltas=delta_GOC_size_data['num_deltas'])

general_object_data.plot.line(x="num_of_operations", y=["state_num_objects","state_num_deltas", "delta_num_objects", "delta_num_deltas"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])
plt.ylim(top=101000)
plt.legend(["state objects", "state delta-objects", "delta objects", "delta delta-objects"])
plt.xlabel("Number of token operations", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR,"general_object_count.png"), bbox_inches='tight')


# Fig. 6.3 b) (Number of blob, tree and commit objects)
object_data = state_GOC_size_data[['num_of_operations']]
object_data = object_data.assign(state_num_blobs=state_GOC_gitsizer_data['uniqueBlobCount'])
object_data = object_data.assign(state_num_trees=state_GOC_gitsizer_data['uniqueTreeCount'])
object_data = object_data.assign(state_num_commits=state_GOC_gitsizer_data['uniqueCommitCount'])

object_data = object_data.assign(delta_num_blobs=delta_GOC_gitsizer_data['uniqueBlobCount'])
object_data = object_data.assign(delta_num_trees=delta_GOC_gitsizer_data['uniqueTreeCount'])
object_data = object_data.assign(delta_num_commits=delta_GOC_gitsizer_data['uniqueCommitCount'])

object_data.plot.line(x="num_of_operations", y=["state_num_blobs", "state_num_commits", "state_num_trees", "delta_num_trees"])
plt.legend(["state + delta blobs", "state + delta commits", "state trees", "delta trees"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])

plt.xlabel("Number of token operations", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR,"distinct_objects_count.png"), bbox_inches='tight')


# Fig. 6.4 (Incremental bundle file size)
delta_bundle_data = state_GOC_size_data[['num_of_operations']]
delta_bundle_data = delta_bundle_data.assign(state_bundle=state_GOC_size_data['delta_bundle_size'].div(1000).round(2))
delta_bundle_data = delta_bundle_data.assign(delta_bundle=delta_GOC_size_data['delta_bundle_size'].div(1000).round(2))

delta_bundle_data.plot.line(x="num_of_operations", y=["state_bundle","delta_bundle"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])
plt.legend(["state-based", "delta-based"])
plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Size of delta bundle file in KB", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR, "delta_bundle.png"), bbox_inches='tight')


# Fig. 6.5 (Size reduction of the delta-based approach compared to the state-based implementation)
delta_bundle_data = delta_bundle_data.assign(ratio=(( delta_bundle_data['state_bundle'] - delta_bundle_data['delta_bundle'] ) / delta_bundle_data['state_bundle'] * 100))

X = delta_bundle_data['num_of_operations'].values.reshape(-1, 1)
Y = delta_bundle_data['ratio'].values.reshape(-1, 1)
linear_regressor = LinearRegression()
linear_regressor.fit(X, Y)
Y_pred = linear_regressor.predict(X)
delta_bundle_data = delta_bundle_data.assign(regression=Y_pred)

r_2 = linear_regressor.score(X, Y) #coefficient of determination
print(f"R^2 (coefficient of determination): {r_2}")

delta_bundle_data.plot.line(x="num_of_operations", y=["ratio", "regression"], color=["#1f77b4", "black"], style=["-", "--"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])
plt.legend(["delta", "OLS Regression"])
plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Size reduction factor in %", fontsize=12)


plt.savefig(os.path.join(FIGURES_DIR, "delta_bundle_ratio.png"), bbox_inches='tight')


# Fig. 6.6 (Uncompressed repository size)
repo_data = state_GOC_size_data[['num_of_operations']]
repo_data = repo_data.assign(state_repo=state_GOC_size_data['size_unpacked_repo'].div(1000).round(2))
repo_data = repo_data.assign(delta_repo=delta_GOC_size_data['size_unpacked_repo'].div(1000).round(2))

repo_data.plot.line(x="num_of_operations", y=["state_repo","delta_repo"])

plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])
plt.legend(["state", "delta"])
plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Size of repository (excluding local data) in KB", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR,"repo.png"), bbox_inches='tight')


# Fig. 6.7 (Compression factor)
repo_data = repo_data.assign(state_ratio=(repo_data['state_repo'] / bundle_data['state_bundle']  * 100 ))
repo_data = repo_data.assign(delta_ratio=(repo_data['delta_repo'] / bundle_data['delta_bundle']  * 100 ))


repo_data.iloc[1: , :].plot.line(x="num_of_operations", y=["state_ratio","delta_ratio"]) # we skipped the first measurement, because it is an extreme outlier (this is documented in the evaluation chapter)
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.xlim([0, xMax])
plt.legend(["state", "delta"])
plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Compression factor in %", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR,"bundle_repo_compression_ratio.png"), bbox_inches='tight')


# Fig. 6.8 a) (Tree objects size)
tree_size_data = state_GOC_size_data[['num_of_operations']]
tree_size_data = tree_size_data.assign(state_tree=state_GOC_gitsizer_data['uniqueTreeSize'].div(1000).round(2))
tree_size_data = tree_size_data.assign(state_tree_naive=state_GOC_gitsizer_data['naiveTreeSize'].div(1000).round(2))

tree_size_data = tree_size_data.assign(delta_tree=delta_GOC_gitsizer_data['uniqueTreeSize'].div(1000).round(2))
tree_size_data = tree_size_data.assign(delta_tree_naive=delta_GOC_gitsizer_data['naiveTreeSize'].div(1000).round(2))

tree_size_data.plot.line(x="num_of_operations", y=["state_tree","delta_tree", "state_tree_naive", "delta_tree_naive"], style=["-", "-", "--", "--"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.legend(["state-based tree size", "delta-based tree size", "naive state-based tree size", "naive delta-based tree size"])
plt.xlim([0, xMax])
plt.xlabel("Number of token operations", fontsize=12)
plt.ylabel("Size in KB", fontsize=12)
plt.savefig(os.path.join(FIGURES_DIR,"tree_size.png"), bbox_inches='tight')


# Fig. 6.8 b) (Blob objects size)
naive_delta = pd.read_csv(os.path.join(DELTA_RESULTS_DIR, "naive_sizes.csv"))
naive_state = pd.read_csv(os.path.join(STATE_RESULTS_DIR, "naive_sizes.csv"))

blob_size_data = state_GOC_size_data[['num_of_operations']]
blob_size_data = blob_size_data.assign(state_blobs=state_GOC_gitsizer_data['uniqueBlobSize'].div(1000).round(2))
blob_size_data = blob_size_data.assign(state_blobs_naive=naive_state['naive_blob_size'].div(1000).round(2))

blob_size_data = blob_size_data.assign(delta_blobs=state_GOC_gitsizer_data['uniqueBlobSize'].div(1000).round(2))
blob_size_data = blob_size_data.assign(delta_blobs_naive=naive_delta['naive_blob_size'].div(1000).round(2))

blob_size_data.plot.line(x="num_of_operations", y=["state_blobs", "delta_blobs", "state_blobs_naive", "delta_blobs_naive"], style=["-", "-", "--", "--"])
plt.axvspan(0, start_create, color='red', alpha=0.2) # account + token init
plt.axvspan(start_create + 1, start_transactions, color='blue', alpha=0.2) # token create
plt.legend(["state blobs", "delta blobs", "state blobs naive", "delta blobs naive"])
# plt.title("tree object size")
plt.xlim([0, xMax])
plt.xlabel("Number of token operations")
plt.ylabel("Size in KB")
plt.savefig(os.path.join(FIGURES_DIR,"blob_size.png"), bbox_inches='tight')

# Calculating average size reduction of state-based implementation compared to the naive approach

blob_size_data = blob_size_data.assign(total_size_state=blob_size_data['state_blobs'] + state_GOC_gitsizer_data['uniqueTreeSize'].div(1000).round(2))
blob_size_data = blob_size_data.assign(total_size_state_naive=blob_size_data['state_blobs_naive'] + state_GOC_gitsizer_data['naiveTreeSize'].div(1000).round(2))

blob_size_data = blob_size_data.assign(size_reduction=(blob_size_data['total_size_state_naive'] - blob_size_data['total_size_state']) / blob_size_data['total_size_state_naive'] * 100 )

print("Avg state-based size reduction compared to the naive approach:", blob_size_data['size_reduction'].mean())
