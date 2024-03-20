


import subprocess
import os
import shutil
import hashlib
import sys
import io


def cmd_stdout_b(cmdstr):
    p = subprocess.run(cmdstr,
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       check=True)
    return p.stdout

def cmd_stdout(cmdstr,print_=False):
    try:
        rets = cmd_stdout_b(cmdstr).decode("cp932")
        if print_:
            print(rets)
        return rets
    except Exception as e:
        if print_:
            print(e.stdout.decode("cp932"))
        raise e

def make_file(p,contents):
    if dir := os.path.dirname(p):
        os.makedirs(dir, exist_ok = True)
    with open(p,"w") as fh:
        fh.write(contents)

def hexdigest(path,type=None):
    m=hashlib.sha1()
    with open(path,"rb") as fh:
        contents = fh.read()
        if type == "blob":
            m.update(b"blob ")
            s = f"{len(contents)}"
            m.update(bytes(s,"iso-8859-1"))
            m.update(b"\x00")
        m.update(contents)
    return m.hexdigest()

def commit_file(name):
    make_file(f"{name}.txt",f"{name}\n") 
    cmd_stdout(f"git add {name}.txt")
    cmd_stdout(f"git commit -m {name}")


os.environ["GIT_AUTHOR_DATE"] = "Fri May 5 20:30:55 2023 +0900"
os.environ["GIT_COMMITTER_DATE"] = "Fri May 5 20:30:55 2023 +0900"
DIR_ORG = os.path.abspath(".")

