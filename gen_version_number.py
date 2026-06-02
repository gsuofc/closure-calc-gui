from datetime import datetime
import subprocess
import sys

def get_version_tagged_desc():
    try:
        git_hash = subprocess.check_output(['git', 'describe', '--tags']).strip().decode('utf-8')

        status_output = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8')
        if status_output.strip():
            git_hash += "-modified"

        return git_hash
    except subprocess.CalledProcessError:
        return "***untracked build***"
    
def get_git_hash():
    try:
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
        return git_hash
    except subprocess.CalledProcessError:
        return None

def gen_version_info(build_info = "Other Build Method"):
    print("Build Method: %s"%build_info)
    current_git_hash = get_version_tagged_desc()
    raw_git_hash = get_git_hash()
    with open("version_info.py", "w") as f:
        f.write(f'__git_hash__ = "{current_git_hash}"\n')
        f.write(f'__git_raw_hash__ = "{raw_git_hash}"\n')
        f.write(f'__build_method__ = "{build_info}"\n')
        f.write(f'__time_built__ = "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"\n')
    print("Succesfully generated git version! %s"%current_git_hash)
    
    
if __name__ == "__main__":
    if len(sys.argv)>1:
        gen_version_info(sys.argv[1])
    else:
        gen_version_info()