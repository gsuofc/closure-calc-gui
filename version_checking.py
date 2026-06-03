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

# REMOVE THIS WHEN WE REMOVE THE MAC BUILD - We are hardcoding the final mac build to be 0.3. This checks to see the latest 0.3 version
def get_latest_0_3_version(current_version_hash):
    # Check for latest 0.3 version
    g = Github(token)
    repo = g.get_repo(repo_path)
    releases = repo.get_releases()
    latest_0_3 = None
    for release in releases:
        latest_0_3 = release
        if "v0.3" in release.tag_name:
            break
        if "v0.2" in release.tag_name:
            break
        latest_0_3 = None

    if latest_0_3 is None:
        return (None, None, False)

    # Get the commit for both that version and this version
    release_commit = repo.get_commit(latest_0_3.tag_name)
    release_date = release_commit.commit.author.date

    local_commit = repo.get_commit(current_version_hash)
    local_date = local_commit.commit.author.date

    # Check if this version is outdated for 0.3
    is_outdated = False

    if local_date < release_date:
        print("Code is older than latest release. Should prompt for update.")
        is_outdated = True

    return (latest_0_3.tag_name, release_commit.sha,is_outdated)
