# script to install Aseprite in linux

import os
import platform
import subprocess
import zipfile

import requests


def check_os():
    if platform.system() != 'Linux':
        print('This script is intended to be used on Linux systems only.')
        exit()


def update_system():
    print('Updating system...')
    command = ['sudo', 'apt', 'update']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('System updated.')


def upgrade_system():
    print('Upgrading system...')
    command = ['sudo', 'apt', 'upgrade', '-y']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('System upgraded.')


def install_dependencies():
    print('Installing dependencies...')
    command = ['sudo', 'apt-get', 'install', '-y', 'g++', 'clang', 'libc++-dev', 'libc++abi-dev', 'cmake',
               'ninja-build', 'libx11-dev', 'libxcursor-dev', 'libxi-dev', 'libgl1-mesa-dev', 'libfontconfig1-dev']
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('Dependencies installed.')


def check_and_create_directory():
    base_directory = os.path.expanduser('~/deps')
    skia_directory = os.path.join(base_directory, 'skia')

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


def download_skia(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    data = response.json()
    for asset in data['assets']:
        if asset['name'] == 'Skia-Linux-Release-x64-libc++.zip':
            download_url = asset['browser_download_url']
            break
    else:
        print("Skia-Linux-Release-x64-libc++.zip not found in the latest release.")
        return

    download_response = requests.get(download_url)

    directory = os.path.expanduser('~/deps/skia')
    filename = f"{directory}/Skia-Linux-Release-x64-libc++.zip"

    with open(filename, 'wb') as f:
        f.write(download_response.content)
    print(f"Downloaded the latest release of {user}/{repo} to {filename}")

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(directory)
    print(f"Extracted the zip file to {directory}")

    os.remove(filename)
    print(f"Deleted the downloaded file {filename}")


def download_aseprite(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(url)
    data = response.json()
    for asset in data['assets']:
        if asset['name'].endswith('.zip'):
            download_url = asset['browser_download_url']
            break
    else:
        print("No .zip file found in the latest release.")
        return

    download_response = requests.get(download_url)

    directory = os.path.expanduser('~/descargas/aseprite')
    filename = f"{directory}/{asset['name']}"

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'wb') as f:
        f.write(download_response.content)
    print(f"Downloaded the latest release of {user}/{repo} to {filename}")

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(directory)
    print(f"Extracted the zip file to {directory}")

    os.remove(filename)
    print(f"Deleted the downloaded file {filename}")


def build_aseprite():
    command = """
    cd ~/descargas/aseprite && \
    mkdir build && \
    cd build && \
    export CC=clang && \
    export CXX=clang++ && \
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_CXX_FLAGS:STRING=-stdlib=libc++ -DCMAKE_EXE_LINKER_FLAGS:STRING=-stdlib=libc++ -DLAF_BACKEND=skia -DSKIA_DIR=$HOME/deps/skia -DSKIA_LIBRARY_DIR=$HOME/deps/skia/out/Release-x64 -DSKIA_LIBRARY=$HOME/deps/skia/out/Release-x64/libskia.a -G Ninja .. && \
    ninja aseprite
    """
    process = subprocess.Popen(command, shell=True, executable="/bin/bash")
    process.wait()


def move_aseprite():
    source_directory = os.path.expanduser('~/descargas/aseprite')
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


def create_desktop_file():
    desktop_file = """
[Desktop Entry]
Name = Aseprite
Type = Application
Icon = /opt/aseprite/data/icons/ase256.png
Exec = /opt/aseprite/build/bin/aseprite
Comment = Compile by Andre Carbajal
Categories = Graphics
Terminal = false
    """

    desktop_file_path = os.path.expanduser('~/.local/share/applications/aseprite.desktop')

    # Write the desktop file content to a temporary file
    with open('/tmp/aseprite.desktop', 'w') as f:
        f.write(desktop_file)

    # Move the temporary file to the final location with sudo
    command = ['sudo', 'mv', '/tmp/aseprite.desktop', desktop_file_path]
    subprocess.Popen(command, stdout=subprocess.PIPE).communicate()

def give_execution_permission():
    desktop_file_path = os.path.expanduser('~/.local/share/applications/aseprite.desktop')
    command = ['chmod', '+x', desktop_file_path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()

    print(f"Given execution permission to {desktop_file_path}")


if __name__ == '__main__':
    check_os()

    update_system()
    upgrade_system()

    install_dependencies()

    check_and_create_directory()

    download_skia('aseprite', 'skia')

    download_aseprite('aseprite', 'aseprite')

    build_aseprite()

    move_aseprite()

    create_desktop_file()
    give_execution_permission()
