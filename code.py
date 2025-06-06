import os
import hashlib
import json
import shutil
import sys
from datetime import datetime

VCS_DIR = ".vcs"
OBJECTS_DIR = os.path.join(VCS_DIR, "objects")
COMMITS_FILE = os.path.join(VCS_DIR, "commits.json")
INDEX_FILE = os.path.join(VCS_DIR, "index.json")

def hash_content(content):
    return hashlib.sha1(content).hexdigest()

def init():
    if os.path.exists(VCS_DIR):
        print("Repository already initialized.")
        return
    os.makedirs(OBJECTS_DIR)
    with open(COMMITS_FILE, 'w') as f:
        json.dump([], f)
    with open(INDEX_FILE, 'w') as f:
        json.dump({}, f)
    print("Initialized empty VCS repository in .vcs/")

def add(filename):
    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist.")
        return
    with open(filename, 'rb') as f:
        content = f.read()
    sha1 = hash_content(content)
    path = os.path.join(OBJECTS_DIR, sha1)
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(content)
    index = load_index()
    index[filename] = sha1
    save_index(index)
    print(f"Added '{filename}'.")

def commit(message):
    index = load_index()
    if not index:
        print("No changes to commit.")
        return
    commits = load_commits()
    commit_data = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "snapshot": index.copy()
    }
    commits.append(commit_data)
    with open(COMMITS_FILE, 'w') as f:
        json.dump(commits, f, indent=2)
    save_index({})
    print(f"Committed changes: {message}")

def log():
    commits = load_commits()
    for i, commit in enumerate(reversed(commits)):
        print(f"Commit #{len(commits)-i-1}")
        print(f"Date: {commit['timestamp']}")
        print(f"Message: {commit['message']}")
        print("-" * 30)

def checkout(commit_number):
    commits = load_commits()
    if commit_number < 0 or commit_number >= len(commits):
        print("Invalid commit number.")
        return
    snapshot = commits[commit_number]["snapshot"]
    for filename, sha1 in snapshot.items():
        path = os.path.join(OBJECTS_DIR, sha1)
        with open(path, 'rb') as f:
            content = f.read()
        with open(filename, 'wb') as f:
            f.write(content)
    print(f"Checked out commit #{commit_number}.")

def load_commits():
    if not os.path.exists(COMMITS_FILE):
        return []
    with open(COMMITS_FILE, 'r') as f:
        return json.load(f)

def load_index():
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, 'r') as f:
        return json.load(f)

def save_index(index):
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f)

def status():
    index = load_index()
    if not index:
        print("No files staged.")
        return
    print("Staged files:")
    for file in index:
        print(f"  {file}")

def help():
    print("Commands:")
    print("  init               Initialize a repository")
    print("  add <filename>     Stage a file")
    print("  commit <msg>       Commit staged files")
    print("  log                Show commit history")
    print("  checkout <num>     Restore files from commit number")
    print("  status             Show staged files")
    print("  help               Show this help")

def main():
    if len(sys.argv) < 2:
        help()
        return
    cmd = sys.argv[1]
    if cmd == "init":
        init()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Specify file to add.")
        else:
            add(sys.argv[2])
    elif cmd == "commit":
        if len(sys.argv) < 3:
            print("Specify commit message.")
        else:
            commit(" ".join(sys.argv[2:]))
    elif cmd == "log":
        log()
    elif cmd == "checkout":
        if len(sys.argv) < 3:
            print("Specify commit number.")
        else:
            try:
                checkout(int(sys.argv[2]))
            except ValueError:
                print("Invalid commit number.")
    elif cmd == "status":
        status()
    else:
        help()

if __name__ == "__main__":
    main()

