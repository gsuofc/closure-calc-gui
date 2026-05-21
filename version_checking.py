from github import Github

token = None # Put your GitHub API token here if you want to access a private repo.
repo_path = "gsuofc/closure-calc-gui"

def get_latest_version_number():
    g = Github(token)
    repo = g.get_repo(repo_path)
    latest = repo.get_latest_release()
    return latest.tag_name

def is_newer_version(current_version_hash):
    g = Github(token)
    repo = g.get_repo(repo_path)
    release = repo.get_latest_release()
    release_commit = repo.get_commit(release.tag_name)
    release_date = release_commit.commit.author.date

    local_commit = repo.get_commit(current_version_hash)
    local_date = local_commit.commit.author.date

    if local_date > release_date:
        print("Running later code than release (developing/testing out main)")
    elif local_date < release_date:
        print("Code is older than latest release. Should prompt for update.")
        return True
    else:
        print("Running Latest Release")

    return False