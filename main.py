import logging
import os
import platform
import subprocess
import zipfile

import requests

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

BASE_DIRECTORY = os.path.expanduser('~/deps')
SKIA_DIRECTORY = os.path.join(BASE_DIRECTORY, 'skia')
ASEPRITE_DIRECTORY = os.path.expanduser('/tmp/aseprite')
ASEPRITE_DESKTOP_FILE = os.path.expanduser('~/.local/share/applications/aseprite.desktop')
BUNDLE_MACOS_DIRECTORY = os.path.expanduser('/tmp/bundle')


def execute_command(command, success_message, error_message):
    try:
        subprocess.run(command, check=True)
        logging.info(success_message)
    except subprocess.CalledProcessError:
        logging.error(error_message)
        exit(1)


def execute_command_shell(command, success_message, error_message):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        logging.info(success_message)
    except subprocess.CalledProcessError:
        logging.error(error_message)
        exit(1)


def is_xcode_installed():
    try:
        result = subprocess.run(['xcode-select', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def check_and_create_directory(base_directory, skia_directory):
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        logging.info("Directory %s created.", base_directory)
    else:
        logging.info("Directory %s already exists.", base_directory)

    if not os.path.exists(skia_directory):
        os.makedirs(skia_directory)
        logging.info("Directory %s created.", base_directory)
    else:
        logging.info("Directory %s already exists.", base_directory)


def download_file(user, repo, file_name, directory, file_extension=None):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        logging.error("Timeout error while trying to get the latest release of %s/%s", user, repo)
        exit(1)

    data = response.json()
    for asset in data['assets']:
        if file_extension and asset['name'].endswith(file_extension) or asset['name'] == file_name:
            download_url = asset['browser_download_url']
            break
    else:
        logging.error("%s not found in the latest release.", file_name)
        exit(1)

    download_response = requests.get(download_url)

    filename = f"{directory}/{asset['name']}"

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'wb') as f:
        f.write(download_response.content)
    logging.info("Downloaded the latest release of %s/%s to %s", user, repo, filename)

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(directory)
    logging.info("Extracted the zip file to %s", directory)

    os.remove(filename)


def build_linux_aseprite(aseprite_directory):
    command = f"""
    cd {aseprite_directory} && \
    mkdir build && \
    cd build && \
    export CC=clang && \
    export CXX=clang++ && \
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_CXX_FLAGS:STRING=-stdlib=libc++ -DCMAKE_EXE_LINKER_FLAGS:STRING=-stdlib=libc++ -DLAF_BACKEND=skia -DSKIA_DIR=$HOME/deps/skia -DSKIA_LIBRARY_DIR=$HOME/deps/skia/out/Release-x64 -DSKIA_LIBRARY=$HOME/deps/skia/out/Release-x64/libskia.a -G Ninja .. && \
    ninja aseprite
    """
    process = subprocess.Popen(command, shell=True, executable="/bin/bash")
    process.wait()


def build_macos_x86_64_aseprite(aseprite_directory):
    command = f"""
    cd {aseprite_directory} && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_OSX_DEPLOYMENT_TARGET=10.9 -DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk -DLAF_BACKEND=skia -DSKIA_DIR=$HOME/deps/skia -DSKIA_LIBRARY_DIR=$HOME/deps/skia/out/Release-x64 -DSKIA_LIBRARY=$HOME/deps/skia/out/Release-x64/libskia.a -G Ninja .. && \
    ninja aseprite
    """
    process = subprocess.Popen(command, shell=True, executable="/bin/bash")
    process.wait()


def build_macos_arm_aseprite(aseprite_directory):
    command = f"""
    cd {aseprite_directory} && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0 -DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk -DLAF_BACKEND=skia -DSKIA_DIR=$HOME/deps/skia -DSKIA_LIBRARY_DIR=$HOME/deps/skia/out/Release-arm64 -DSKIA_LIBRARY=$HOME/deps/skia/out/Release-arm64/libskia.a -DPNG_ARM_NEON:STRING=on -G Ninja .. && \
    ninja aseprite
    """
    process = subprocess.Popen(command, shell=True, executable="/bin/bash")
    process.wait()


def move_linux_aseprite(aseprite_directory):
    source_directory = os.path.expanduser(aseprite_directory)
    target_directory = '/opt/aseprite'

    if not os.path.exists(target_directory):
        execute_command(['sudo', 'mkdir', '-p', target_directory], 'Directory created at /opt/aseprite directory.',
                        'Failed to create /opt/aseprite directory.')

    for filename in os.listdir(source_directory):
        source_file = os.path.join(source_directory, filename)
        target_file = os.path.join(target_directory, filename)

        execute_command(['sudo', 'mv', source_file, target_file], 'File move' + source_file + 'to' + target_file,
                        'Failed to move' + source_file + 'to' + target_file)


def create_desktop_file(aseprite_desktop_file):
    desktop_file = """[Desktop Entry]
Name=Aseprite
Type=Application
Icon=/opt/aseprite/data/icons/ase256.png
Exec=/opt/aseprite/build/bin/aseprite
Comment=Compile by Andre Carbajal
Categories=Graphics;
Terminal=false"""

    with open('/tmp/aseprite.desktop', 'w') as f:
        f.write(desktop_file)

    execute_command(['sudo', 'mv', '/tmp/aseprite.desktop', aseprite_desktop_file],
                    'File moved to {aseprite_desktop_file}',
                    'Failed to move file to {aseprite_desktop_file}')


def bundle_macos_aseprite(bundle_macos_directory, file_name, aseprite_directory):
    if not os.path.exists(bundle_macos_directory):
        os.makedirs(bundle_macos_directory)

    url = f"https://www.aseprite.org/downloads/trial/{file_name}"
    response = requests.get(url)

    file_directory = os.path.join(bundle_macos_directory, file_name)
    with open(file_directory, 'wb') as f:
        f.write(response.content)

    mount_directory = os.path.join(bundle_macos_directory, 'mount')
    if not os.path.exists(mount_directory):
        os.makedirs(mount_directory)

    execute_command_shell(
        f"""yes qy | hdiutil attach -quiet -nobrowse -noverify -noautoopen -mountpoint {mount_directory} {file_directory}""",
        'Disk image mounted.', 'Failed to mount disk image.')

    execute_command(['cp', '-rf', mount_directory + '/Aseprite.app', bundle_macos_directory + '/Aseprite.app'],
                    'Aseprite.app copied.', 'Failed to copy Aseprite.app.')
    execute_command_shell(['hdiutil', 'detach', mount_directory], 'Disk image detached.',
                          'Failed to detach disk image.')
    execute_command(['rm', '-rf', bundle_macos_directory + 'Aseprite.app/Contents/MacOS/aseprite'],
                    'Contents/MacOS removed.', 'Failed to remove Contents/MacOS.')
    execute_command(['cp', '-r', aseprite_directory + '/build/bin/aseprite',
                     bundle_macos_directory + '/Aseprite.app/Contents/MacOS/aseprite'], 'aseprite copied.',
                    'Failed to copy aseprite.')
    execute_command(['rm', '-rf', bundle_macos_directory + 'Aseprite.app/Contents/Resources/data'],
                    'Contents/Resources/data removed.', 'Failed to remove Contents/Resources/data.')
    execute_command(['cp', '-r', aseprite_directory + '/build/bin/data',
                     bundle_macos_directory + '/Aseprite.app/Contents/Resources/data'], 'data copied.',
                    'Failed to copy data.')


def install_on_linux():
    execute_command(['sudo', 'apt', 'update'], 'System updated.', 'Failed to update system.')
    execute_command(['sudo', 'apt', 'upgrade', '-y'], 'System upgraded.', 'Failed to upgrade system.')
    execute_command(['sudo', 'apt-get', 'install', '-y', 'g++', 'clang', 'libc++-dev', 'libc++abi-dev', 'cmake',
                     'ninja-build', 'libx11-dev', 'libxcursor-dev', 'libxi-dev', 'libgl1-mesa-dev',
                     'libfontconfig1-dev'], 'Dependencies installed.', 'Failed to install dependencies.')

    check_and_create_directory(BASE_DIRECTORY, SKIA_DIRECTORY)

    download_file('aseprite', 'skia', 'Skia-Linux-Release-x64-libc++.zip', SKIA_DIRECTORY)
    download_file('aseprite', 'aseprite', None, ASEPRITE_DIRECTORY, '.zip')

    build_linux_aseprite(ASEPRITE_DIRECTORY)

    move_linux_aseprite(ASEPRITE_DIRECTORY)

    create_desktop_file(ASEPRITE_DESKTOP_FILE)

    execute_command(['sudo', 'chmod', '+x', ASEPRITE_DESKTOP_FILE],
                    'Execution permission given to aseprite.desktop',
                    'Failed to give execution permission to aseprite.desktop')


def install_on_macos():
    if is_xcode_installed():
        logging.info('Xcode command line tools already installed')
    else:
        execute_command(['xcode-select', '--install'], 'Xcode command line tools installed.',
                        'Failed to install Xcode command line tools.')

    execute_command(['brew', 'install', 'cmake', 'ninja'], 'Dependencies installed.',
                    'Failed to install dependencies.')

    check_and_create_directory(BASE_DIRECTORY, SKIA_DIRECTORY)

    download_file('aseprite', 'aseprite', None, ASEPRITE_DIRECTORY, '.zip')

    if platform.machine() == 'x86_64':
        download_file('aseprite', 'skia', 'Skia-macOS-Release-x64.zip', SKIA_DIRECTORY)
        build_macos_x86_64_aseprite(ASEPRITE_DIRECTORY)
    elif 'arm' in platform.machine():
        download_file('aseprite', 'skia', 'Skia-macOS-Release-arm64.zip', SKIA_DIRECTORY)
        build_macos_arm_aseprite(ASEPRITE_DIRECTORY)

    bundle_macos_aseprite(BUNDLE_MACOS_DIRECTORY, 'Aseprite-v1.3.6-trial-macOS.dmg', ASEPRITE_DIRECTORY)

    execute_command(['sudo', 'cp', '-r', BUNDLE_MACOS_DIRECTORY + '/Aseprite.app', '/Applications/Aseprite.app'],
                    'Aseprite.app copied to /Applications directory.',
                    'Failed to copy Aseprite.app to /Applications directory.')


if __name__ == '__main__':
    if os.getuid() == 0:
        logging.error('This script should not be run as root.')
        exit(1)

    if platform.system() == 'Linux':
        install_on_linux()
    elif platform.system() == 'Darwin':
        install_on_macos()
    else:
        logging.error('Unsupported operating system.')
        exit(1)

    logging.info('Aseprite installed successfully.')
