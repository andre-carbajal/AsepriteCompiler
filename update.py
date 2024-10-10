import logging
import os
import platform

from install import install_on_macos, install_on_linux
from uninstall import remove_linux_aseprite, remove_macos_aseprite

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

if __name__ == '__main__':
    if os.getuid() != 0:
        logging.error('This script must be run as root.')
        exit(1)

    if platform.system() == 'Linux':
        remove_linux_aseprite()
        install_on_linux()
    elif platform.system() == 'Darwin':
        remove_macos_aseprite()
        install_on_macos()
    else:
        logging.error('Unsupported operating system.')
        exit(1)