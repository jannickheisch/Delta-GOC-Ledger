import git
import os
import subprocess
import shutil
import pandas as pd

bundle_path = "./results/single-repo-git-goc-delta/bundles" # change these paths for calculating the state-based naive sizes
csv_path ="/results/single-repo-git-goc-delta/naive_sizes.csv"

tmp_path = "./tmp"


sizes = []

progress = 0
max = len(os.listdir(bundle_path))
shutil.rmtree(tmp_path, ignore_errors=True)
os.mkdir(tmp_path)


bundle_lst = os.listdir(bundle_path)

for bundle in sorted(os.listdir(bundle_path), key=lambda x: int(x.split(".")[0])):
    naive_blob_size = 0
    naive_tree_size = 0
    naive_blob_count = 0
    naive_tree_count = 0
    print(f"{progress}/{max}: {bundle}")

    name = bundle.split(".")[0]
    path = os.path.join(bundle_path, bundle)
    tmp_bundle_path = os.path.join(tmp_path, bundle)
    #shutil.copy(path, tmp_bundle_path)
    #subprocess.call(["git", "clone", bundle], cwd=tmp_path)

    repo_path = os.path.join(tmp_path, name)
    repo = git.Repo.clone_from(path, repo_path)
    origin = repo.remotes[0]


    traversed_commits = []

    for ref in origin.refs:
        for commit in repo.iter_commits(ref, first_parent=True):
            if commit.hexsha in traversed_commits:
                continue
            traversed_commits.append(commit.hexsha)

            tree = commit.tree
            naive_tree_size += tree.size
            naive_tree_count += 1

            for b in tree.blobs:
                naive_blob_size += b.size
                naive_blob_count += 1

            for t in tree.trees:
                naive_tree_size += t.size
                naive_tree_count += 1
                for b in t.blobs:
                    naive_blob_size+= b.size
                    naive_blob_count += 1
    repo.close()
    shutil.rmtree(repo_path)
    sizes.append([name, naive_blob_count, naive_blob_size, naive_tree_count, naive_tree_size])
    progress += 1

csv = pd.DataFrame(sizes, columns=["num_of_operations", "naive_blob_count", "naive_blob_size", "naive_tree_count", "naive_tree_size"])
csv.to_csv(csv_path, index=False)