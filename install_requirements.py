import os


def install_modules():
    if os.name == "nt":
        os.system("py -m pip install --upgrade pip")
        os.system("py -m pip install -r requirements.txt")
    else:
        os.system("python3 -m pip install --upgrade pip")
        os.system("python3 -m pip install -r requirements.txt")

    input("\nPress ENTER to exit the installation...")


install_modules()
