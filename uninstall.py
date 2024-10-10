import logging
import os
import platform
import subprocess

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

ASEPRITE_DIRECTORY = os.path.expanduser('/tmp/aseprite')
ASEPRITE_DESKTOP_FILE = os.path.expanduser('~/.local/share/applications/aseprite.desktop')
BUNDLE_MACOS_DIRECTORY = os.path.expanduser('/tmp/bundle')
TARGET_DIRECTORY_LINUX = '/opt/aseprite'
APPLICATIONS_DIRECTORY_MACOS = '/Applications/Aseprite.app'


def execute_command(command, success_message, error_message):
    try:
        subprocess.run(command, check=True)
        logging.info(success_message)
    except subprocess.CalledProcessError:
        logging.error(error_message)
        exit(1)


def remove_linux_aseprite():
    if os.path.exists(TARGET_DIRECTORY_LINUX):
        execute_command(['sudo', 'rm', '-rf', TARGET_DIRECTORY_LINUX], 'Aseprite directory removed.',
                        'Failed to remove Aseprite directory.')

    if os.path.exists(ASEPRITE_DESKTOP_FILE):
        execute_command(['sudo', 'rm', ASEPRITE_DESKTOP_FILE], 'Aseprite desktop file removed.',
                        'Failed to remove Aseprite desktop file.')

    logging.info('Aseprite uninstalled successfully on Linux.')


def remove_macos_aseprite():
    if os.path.exists(APPLICATIONS_DIRECTORY_MACOS):
        execute_command(['sudo', 'rm', '-rf', APPLICATIONS_DIRECTORY_MACOS], 'Aseprite.app removed from Applications.',
                        'Failed to remove Aseprite.app from Applications.')

    if os.path.exists(BUNDLE_MACOS_DIRECTORY):
        execute_command(['rm', '-rf', BUNDLE_MACOS_DIRECTORY], 'Bundle directory removed.',
                        'Failed to remove bundle directory.')

    logging.info('Aseprite uninstalled successfully on MacOS.')


if __name__ == '__main__':
    if os.getuid() != 0:
        logging.error('This script must be run as root.')
        exit(1)

    if platform.system() == 'Linux':
        remove_linux_aseprite()
    elif platform.system() == 'Darwin':
        remove_macos_aseprite()
    else:
        logging.error('Unsupported operating system.')
        exit(1)