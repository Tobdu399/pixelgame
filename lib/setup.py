from os import name as operating_system
from os.path import dirname, abspath
import subprocess


def install_modules():
    path = dirname(abspath(__file__))

    if operating_system == "nt":  # Windows
        subprocess.call("py -m pip install --upgrade pip",               shell=True)
        subprocess.call(f"py -m pip install -r {path}/requirements.txt", shell=True)
    else:
        subprocess.call("python3 -m pip install --upgrade pip",               shell=True)
        subprocess.call(f"python3 -m pip install -r {path}/requirements.txt", shell=True)


if __name__ == "__main__":
    # Show some info if this file is executed manually

    print("=======| PIXEL GAME SETUP |=======")
    print(" Installing Modules! Please wait.\n")

    install_modules()

    print("==================================")

    input("\nPress ENTER to exit the installation...")
