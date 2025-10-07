import subprocess

def get_git_hash():
    try:
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
        return git_hash
    except subprocess.CalledProcessError:
        return "***untracked build***"

if __name__ == "__main__":
    current_git_hash = get_git_hash()
    with open("version_info.py", "w") as f:
        f.write(f'__git_hash__ = "{current_git_hash}"\n')
    print("Succesfully generated git version! %s"%current_git_hash)