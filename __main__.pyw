# SETUP -----------------------------
from lib.setup.setup import install_modules
install_modules()

# START GAME ------------------------
from lib.game import main

if __name__ == "__main__":
    main()
