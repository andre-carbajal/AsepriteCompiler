# script to install Aseprite in linux

import os
import platform
import subprocess
import zipfile

import requests

BASE_DIRECTORY = os.path.expanduser('~/deps')
SKIA_DIRECTORY = os.path.join(BASE_DIRECTORY, 'skia')
ASEPRITE_DIRECTORY = os.path.expanduser('/tmp/aseprite')
ASEPRITE_DESKTOP_FILE = os.path.expanduser('~/.local/share/applications/aseprite.desktop')


def check_os():
    if platform.system() != 'Linux':
        print('This script is intended to be used on Linux systems only.')
        exit()
    print('Linux system detected.')


def update_system():
    print('Updating system started...')
    command = ['sudo', 'apt', 'update']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('System updated.')


def upgrade_system():
    print('Upgrading system started...')
    command = ['sudo', 'apt', 'upgrade', '-y']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('System upgraded.')


def install_dependencies():
    print('Installing dependencies for Aseprite... This may take a while')
    command = ['sudo', 'apt-get', 'install', '-y', 'g++', 'clang', 'libc++-dev', 'libc++abi-dev', 'cmake',
               'ninja-build', 'libx11-dev', 'libxcursor-dev', 'libxi-dev', 'libgl1-mesa-dev', 'libfontconfig1-dev']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('Dependencies installed.')


def check_and_create_directory(base_directory, skia_directory):
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        print(f"Directory {base_directory} created.")
    else:
        print(f"Directory {base_directory} already exists.")

    if not os.path.exists(skia_directory):
        os.makedirs(skia_directory)
        print(f"Directory {skia_directory} created.")
    else:
        print(f"Directory {skia_directory} already exists.")


def download_skia(user, repo, skia_fila_name, skia_directory):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    data = response.json()
    for asset in data['assets']:
        if asset['name'] == skia_fila_name:
            download_url = asset['browser_download_url']
            break
    else:
        print(f"{skia_fila_name} not found in the latest release.")
        exit()

    download_response = requests.get(download_url)

    filename = f"{skia_directory}/{skia_fila_name}"

    with open(filename, 'wb') as f:
        f.write(download_response.content)
    print(f"Downloaded the latest release of {user}/{repo} to {filename}")

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(skia_directory)
    print(f"Extracted the zip file to {skia_directory}")

    os.remove(filename)


def download_aseprite(user, repo, file_extension, aseprite_directory):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    data = response.json()
    for asset in data['assets']:
        if asset['name'].endswith(file_extension):
            download_url = asset['browser_download_url']
            break
    else:
        print("No .zip file found in the latest release.")
        exit()

    download_response = requests.get(download_url)

    filename = f"{aseprite_directory}/{asset['name']}"

    if not os.path.exists(aseprite_directory):
        os.makedirs(aseprite_directory)

    with open(filename, 'wb') as f:
        f.write(download_response.content)
    print(f"Downloaded the latest release of {user}/{repo} to {filename}")

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(aseprite_directory)
    print(f"Extracted the zip file to {aseprite_directory}")

    os.remove(filename)


def build_aseprite(aseprite_directory):
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


def move_aseprite(aseprite_directory):
    source_directory = os.path.expanduser(aseprite_directory)
    target_directory = '/opt/aseprite'

    if not os.path.exists(target_directory):
        command = ['sudo', 'mkdir', '-p', target_directory]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, error = process.communicate()

    for filename in os.listdir(source_directory):
        source_file = os.path.join(source_directory, filename)
        target_file = os.path.join(target_directory, filename)

        command = ['sudo', 'mv', source_file, target_file]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        output, error = process.communicate()

    print(f"Moved files from {source_directory} to {target_directory}")


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

    command = ['sudo', 'mv', '/tmp/aseprite.desktop', aseprite_desktop_file]
    subprocess.Popen(command, stdout=subprocess.PIPE).communicate()


def give_execution_permission(aseprite_desktop_file):
    command = ['sudo', 'chmod', '+x', aseprite_desktop_file]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()

    print(f"Given execution permission to {aseprite_desktop_file}")


if __name__ == '__main__':
    check_os()

    update_system()
    upgrade_system()

    install_dependencies()

    check_and_create_directory(BASE_DIRECTORY, SKIA_DIRECTORY)

    download_skia('aseprite', 'skia', 'Skia-Linux-Release-x64-libc++.zip', SKIA_DIRECTORY)

    download_aseprite('aseprite', 'aseprite', '.zip', ASEPRITE_DIRECTORY)

    build_aseprite(ASEPRITE_DIRECTORY)

    move_aseprite(ASEPRITE_DIRECTORY)

    create_desktop_file(ASEPRITE_DESKTOP_FILE)
    give_execution_permission(ASEPRITE_DESKTOP_FILE)
