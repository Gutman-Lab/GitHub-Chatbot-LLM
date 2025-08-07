import os
from git import Repo

# List of GitHub repositories to clone
REPOS = [
    "https://github.com/digitalslidearchive/digital_slide_archive",
    "https://github.com/DigitalSlideArchive/HistomicsUI",
    "https://github.com/DigitalSlideArchive/HistomicsTK"
]

def clone_repo(repo_url, save_dir="data"):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    path = os.path.join(save_dir, repo_name)
    if not os.path.exists(path):
        print(f"Cloning {repo_url} into {path}")
        Repo.clone_from(repo_url, path)
    else:
        print(f"Repository {repo_name} already exists at {path}")
    return path

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for repo in REPOS:
        clone_repo(repo)
