from settings import branch

Version = "V0.0.1 Alpha 3"
git_user = "begeistert"
git_repo = "thingsboard"
git_branch = "master" if branch is "stable" else "beta"
wdir = "src"
sysfiles = ["boot.py", "main.py", "hcsr04.py", "server.py", "thingsboard.py", "ota.py"]
user_files = ["settings.py", "wifi.py"]
