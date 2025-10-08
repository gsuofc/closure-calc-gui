import subprocess

def get_git_hash():
    try:
        git_hash = subprocess.check_output(['git', 'describe', '--tags']).strip().decode('utf-8')

        status_output = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8')
        if status_output.strip():
            git_hash += "-modified"

        return git_hash
    except subprocess.CalledProcessError:
        return "***untracked build***"

def gen_version_info():
    current_git_hash = get_git_hash()
    with open("version_info.py", "w") as f:
        f.write(f'__git_hash__ = "{current_git_hash}"\n')
    print("Succesfully generated git version! %s"%current_git_hash)
    
if __name__ == "__main__":
    gen_version_info()