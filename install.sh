#!/bin/bash

# Global variables
FILE_VERSION="1.3.14.4"
BASE_DIRECTORY="${HOME}/deps"
SKIA_DIRECTORY="${BASE_DIRECTORY}/skia"
ASEPRITE_DIRECTORY="/tmp/aseprite"
ASEPRITE_DESKTOP_FILE="${HOME}/.local/share/applications/aseprite.desktop"
BUNDLE_MACOS_DIRECTORY="/tmp/bundle"

# Function to log informational messages
log_info() {
    echo "INFO - $1"
}

# Function to log error messages and exit
log_error() {
    echo "ERROR - $1" >&2
    exit 1
}

# Function to execute a command and check its exit status
# Usage: execute_command <command> <arg1> <arg2> ...
execute_command() {
    log_info "Executing: $*"
    if ! "$@"; then
        log_error "Command failed: $*"
    fi
}

# Function to check if a command exists in the system's PATH
# Usage: check_command <command_name> <error_message>
check_command() {
    local cmd="$1"
    local error_msg="$2"
    if ! command -v "$cmd" &> /dev/null; then
        log_error "$error_msg"
    fi
}

# Function to check if Xcode command line tools are installed (macOS only)
is_xcode_installed() {
    if xcode-select --version &> /dev/null; then
        return 0 # True
    else
        return 1 # False
    fi
}

# Function to check if a directory exists and create it if not
check_and_create_directory() {
    local dir_path="$1"
    if [ ! -d "$dir_path" ]; then
        log_info "Creating directory: $dir_path"
        mkdir -p "$dir_path"
    else
        log_info "Directory already exists: $dir_path"
    fi
}

# Function to download and extract a file from a GitHub release
# Usage: download_file <user> <repo> <specific_file_name> <target_directory> <file_extension>
# specific_file_name: e.g., Skia-macOS-Release-x64.zip (can be empty if file_extension is used)
# file_extension: e.g., .zip (used if specific_file_name is empty)
download_file() {
    local user="$1"
    local repo="$2"
    local specific_file_name="$3"
    local directory="$4"
    local file_extension="$5"

    check_command "curl" "curl is not installed. Please install it to proceed."
    check_command "unzip" "unzip is not installed. Please install it to proceed."

    local url
    url="https://api.github.com/repos/${user}/${repo}/releases/latest"
    log_info "Fetching latest release information from: ${url}"
    local response
    if ! response=$(curl -s --fail "$url"); then
        log_error "Failed to fetch release information for ${user}/${repo}. Check repository name or network connectivity."
    fi

    local download_url=""
    local asset_name=""

    # Parse the JSON response to find the correct asset
    # This approach is robust for simple cases but could be replaced by 'jq' for complex JSON parsing
    if [ -n "$specific_file_name" ]; then
        asset_name=$(echo "$response" | grep -o '"name": "[^"]*'"${specific_file_name}"'[^"]*"' | sed 's/"name": "\(.*\)"/\1/')
        download_url=$(echo "$response" | grep -o '"browser_download_url": "[^"]*'"${specific_file_name}"'[^"]*"' | sed 's/"browser_download_url": "\(.*\)"/\1/')
    elif [ -n "$file_extension" ]; then
        asset_name=$(echo "$response" | grep -o '"name": "[^"]*'"${file_extension}"'[^"]*"' | sed 's/"name": "\(.*\)"/\1/' | head -n 1)
        download_url=$(echo "$response" | grep -o '"browser_download_url": "[^"]*'"${file_extension}"'[^"]*"' | sed 's/"browser_download_url": "\(.*\)"/\1/' | head -n 1)
    fi

    if [ -z "$download_url" ]; then
        log_error "Desired file ('${specific_file_name}' or any *.${file_extension}) not found in the latest release of ${user}/${repo}."
    fi

    check_and_create_directory "$directory"

    local filename="${directory}/${asset_name}"
    log_info "Downloading asset: ${download_url} to ${filename}"
    execute_command curl -L -o "$filename" "$download_url"

    log_info "Downloaded asset to: ${filename}"

    log_info "Extracting ${filename} to ${directory}"
    execute_command unzip -q "$filename" -d "$directory"
    log_info "Extracted the zip file."

    log_info "Removing downloaded zip file: $filename"
    execute_command rm "$filename"
}

# Function to build Aseprite for Linux
build_linux_aseprite() {
    local aseprite_directory="$1"
    log_info "Starting Aseprite build for Linux..."
    check_command "cmake" "CMake is not installed. Please install it to build Aseprite."
    check_command "ninja" "Ninja Build is not installed. Please install it to build Aseprite."

    execute_command bash -c "
    cd \"${aseprite_directory}\" || log_error \"Failed to change directory to ${aseprite_directory}\"
    mkdir -p build && cd build || log_error \"Failed to create/change to build directory\"

    # Set environment variables for clang compiler
    export CC=clang
    export CXX=clang++

    # Configure CMake for Linux build
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \\
          -DCMAKE_CXX_FLAGS:STRING=-stdlib=libc++ \\
          -DCMAKE_EXE_LINKER_FLAGS:STRING=-stdlib=libc++ \\
          -DLAF_BACKEND=skia \\
          -DSKIA_DIR=${HOME}/deps/skia \\
          -DSKIA_LIBRARY_DIR=${HOME}/deps/skia/out/Release-x64 \\
          -DSKIA_LIBRARY=${HOME}/deps/skia/out/Release-x64/libskia.a \\
          -G Ninja .. || log_error \"CMake configuration failed.\"

    # Build Aseprite using Ninja
    ninja aseprite || log_error \"Ninja build failed.\"
    "
    log_info "Aseprite Linux build completed."
}

# Function to build Aseprite for macOS (x86_64 architecture)
build_macos_x86_64_aseprite() {
    local aseprite_directory="$1"
    log_info "Starting Aseprite build for macOS (x86_64)..."
    check_command "cmake" "CMake is not installed. Please install it to build Aseprite."
    check_command "ninja" "Ninja Build is not installed. Please install it to build Aseprite."

    execute_command bash -c "
    cd \"${aseprite_directory}\" || log_error \"Failed to change directory to ${aseprite_directory}\"
    mkdir -p build && cd build || log_error \"Failed to create/change to build directory\"

    # Configure CMake for macOS x86_64 build
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \\
          -DCMAKE_OSX_ARCHITECTURES=x86_64 \\
          -DCMAKE_OSX_DEPLOYMENT_TARGET=10.9 \\
          -DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk \\
          -DLAF_BACKEND=skia \\
          -DSKIA_DIR=${HOME}/deps/skia \\
          -DSKIA_LIBRARY_DIR=${HOME}/deps/skia/out/Release-x64 \\
          -DSKIA_LIBRARY=${HOME}/deps/skia/out/Release-x64/libskia.a \\
          -G Ninja .. || log_error \"CMake configuration failed.\"

    # Build Aseprite using Ninja
    ninja aseprite || log_error \"Ninja build failed.\"
    "
    log_info "Aseprite macOS (x86_64) build completed."
}

# Function to build Aseprite for macOS (ARM64 architecture)
build_macos_arm_aseprite() {
    local aseprite_directory="$1"
    log_info "Starting Aseprite build for macOS (arm64)..."
    check_command "cmake" "CMake is not installed. Please install it to build Aseprite."
    check_command "ninja" "Ninja Build is not installed. Please install it to build Aseprite."

    execute_command bash -c "
    cd \"${aseprite_directory}\" || log_error \"Failed to change directory to ${aseprite_directory}\"
    mkdir -p build && cd build || log_error \"Failed to create/change to build directory\"

    # Configure CMake for macOS ARM64 build
    cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \\
          -DCMAKE_OSX_ARCHITECTURES=arm64 \\
          -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0 \\
          -DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk \\
          -DLAF_BACKEND=skia \\
          -DSKIA_DIR=${HOME}/deps/skia \\
          -DSKIA_LIBRARY_DIR=${HOME}/deps/skia/out/Release-arm64 \\
          -DSKIA_LIBRARY=${HOME}/deps/skia/out/Release-arm64/libskia.a \\
          -DPNG_ARM_NEON:STRING=on \\
          -G Ninja .. || log_error \"CMake configuration failed.\"

    # Build Aseprite using Ninja
    ninja aseprite || log_error \"Ninja build failed.\"
    "
    log_info "Aseprite macOS (arm64) build completed."
}

# Function to move built Aseprite files to /opt/aseprite on Linux
move_linux_aseprite() {
    local source_directory="$1"
    local target_directory='/opt/aseprite'

    log_info "Moving Aseprite build output from ${source_directory}/build/bin to ${target_directory}..."
    if [ ! -d "$target_directory" ]; then
        execute_command sudo mkdir -p "$target_directory"
    fi
    execute_command sudo cp -r "${source_directory}/build/bin/." "$target_directory"
    log_info "Aseprite files moved to /opt/aseprite."
}

# Function to create a .desktop file for Aseprite on Linux
create_desktop_file() {
    local aseprite_desktop_file="$1"
    local desktop_content="[Desktop Entry]
Name=Aseprite
Type=Application
Icon=/opt/aseprite/data/icons/ase256.png
Exec=/opt/aseprite/aseprite
Comment=Compile by Andre Carbajal
Categories=Graphics;
Terminal=false"

    log_info "Creating desktop file at: ${aseprite_desktop_file}"
    # Using tee with sudo to write to a privileged location
    echo "${desktop_content}" | sudo tee "${aseprite_desktop_file}" > /dev/null
    log_info "Desktop file created."
}

# Function to bundle Aseprite for macOS (creating an .app bundle)
bundle_macos_aseprite() {
    local bundle_macos_directory="$1"
    local file_name="$2" # e.g., Aseprite-vX.Y.Z-trial-macOS.dmg
    local aseprite_directory="$3"

    check_and_create_directory "$bundle_macos_directory"

    local url="https://www.aseprite.org/downloads/trial/${file_name}"
    local file_path="${bundle_macos_directory}/${file_name}"

    log_info "Downloading Aseprite trial DMG for bundling: ${url}"
    execute_command curl -L -o "$file_path" "$url"

    local mount_directory="${bundle_macos_directory}/mount"
    check_and_create_directory "$mount_directory"

    log_info "Mounting disk image: ${file_path}"
    # Mount the DMG and handle EULA acceptance
    log_info "Attempting to mount DMG (this may prompt for EULA acceptance)..."
    if ! hdiutil attach -quiet -nobrowse -noverify -noautoopen -mountpoint "${mount_directory}" "${file_path}" 2>/dev/null; then
        log_info "EULA prompt detected, accepting automatically..."
        echo "Y" | hdiutil attach -nobrowse -noverify -noautoopen -mountpoint "${mount_directory}" "${file_path}"
    fi

    log_info "Copying Aseprite.app from mounted image to staging directory..."
    # Check what's actually in the mounted directory
    log_info "Contents of mounted directory:"
    ls -la "${mount_directory}"
    
    # Find the .app file (it might be in a subdirectory)
    app_path=$(find "${mount_directory}" -name "*.app" -type d | head -1)
    if [ -z "$app_path" ]; then
        log_error "Could not find Aseprite.app in mounted DMG"
    fi
    
    log_info "Found app at: $app_path"
    execute_command cp -rf "$app_path" "${bundle_macos_directory}/Aseprite.app"

    log_info "Detaching disk image: ${mount_directory}"
    execute_command hdiutil detach "${mount_directory}"

    log_info "Removing existing Aseprite executable and data from copied app bundle..."
    execute_command rm -rf "${bundle_macos_directory}/Aseprite.app/Contents/MacOS/aseprite"
    execute_command rm -rf "${bundle_macos_directory}/Aseprite.app/Contents/Resources/data"

    log_info "Copying newly built Aseprite executable into the app bundle..."
    execute_command cp -r "${aseprite_directory}/build/bin/aseprite" "${bundle_macos_directory}/Aseprite.app/Contents/MacOS/aseprite"
    log_info "Copying newly built Aseprite data into the app bundle..."
    execute_command cp -r "${aseprite_directory}/build/bin/data" "${bundle_macos_directory}/Aseprite.app/Contents/Resources/data"
}

# Remove build dependencies and temp files
cleanup() {
    log_info "Removing build directories..."
    rm -rf "$HOME/deps" /tmp/aseprite /tmp/bundle
    log_info "Removed build directories."
}

# Main installation function for Linux
install_on_linux() {
    log_info "--- Starting Aseprite installation on Linux ---"

    log_info "Updating package lists and upgrading installed packages..."
    execute_command sudo apt update
    execute_command sudo apt upgrade -y

    log_info "Installing build dependencies: g++, clang, libc++-dev, etc."
    execute_command sudo apt-get install -y g++ clang libc++-dev libc++abi-dev cmake ninja-build libx11-dev libxcursor-dev libxi-dev libgl1-mesa-dev libfontconfig1-dev

    check_and_create_directory "${BASE_DIRECTORY}"
    check_and_create_directory "${SKIA_DIRECTORY}"
    check_and_create_directory "${ASEPRITE_DIRECTORY}"

    download_file 'aseprite' 'skia' 'Skia-Linux-Release-x64-libc++.zip' "${SKIA_DIRECTORY}" ''
    download_file 'aseprite' 'aseprite' '' "${ASEPRITE_DIRECTORY}" '.zip'

    build_linux_aseprite "${ASEPRITE_DIRECTORY}"

    move_linux_aseprite "${ASEPRITE_DIRECTORY}"

    create_desktop_file "${ASEPRITE_DESKTOP_FILE}"

    log_info "Setting executable permissions for the desktop file..."
    execute_command sudo chmod +x "${ASEPRITE_DESKTOP_FILE}"
    log_info "Execution permission given to ${ASEPRITE_DESKTOP_FILE}."

    log_info "--- Aseprite installed successfully on Linux ---"
}

# Main installation function for macOS
install_on_macos() {
    log_info "--- Starting Aseprite installation on macOS ---"

    if is_xcode_installed; then
        log_info 'Xcode command line tools already installed.'
    else
        log_info 'Installing Xcode command line tools...'
        execute_command xcode-select --install
        log_info 'Xcode command line tools installed.'
        # Give some time for Xcode tools to be fully available
        log_info "Waiting for Xcode command line tools installation to complete (10 seconds)..."
        sleep 10
    fi

    log_info "Installing Homebrew dependencies: cmake, ninja..."
    check_command "brew" "Homebrew is not found. Please install Homebrew first from https://brew.sh/"
    execute_command brew install cmake ninja

    check_and_create_directory "${BASE_DIRECTORY}"
    check_and_create_directory "${SKIA_DIRECTORY}"
    check_and_create_directory "${ASEPRITE_DIRECTORY}"

    download_file 'aseprite' 'aseprite' '' "${ASEPRITE_DIRECTORY}" '.zip'

    local machine_arch
    machine_arch=$(uname -m)
    if [ "${machine_arch}" == "x86_64" ]; then
        download_file 'aseprite' 'skia' 'Skia-macOS-Release-x64.zip' "${SKIA_DIRECTORY}" ''
        build_macos_x86_64_aseprite "${ASEPRITE_DIRECTORY}"
    elif [[ "${machine_arch}" == *"arm"* ]]; then # Covers arm64, etc.
        download_file 'aseprite' 'skia' 'Skia-macOS-Release-arm64.zip' "${SKIA_DIRECTORY}" ''
        build_macos_arm_aseprite "${ASEPRITE_DIRECTORY}"
    else
        log_error "Unsupported macOS architecture: ${machine_arch}. Only x86_64 and ARM-based architectures are supported."
    fi

    bundle_macos_aseprite "${BUNDLE_MACOS_DIRECTORY}" "Aseprite-v${FILE_VERSION}-trial-macOS.dmg" "${ASEPRITE_DIRECTORY}"

    log_info "Copying bundled Aseprite.app to /Applications directory..."
    execute_command sudo cp -r "${BUNDLE_MACOS_DIRECTORY}/Aseprite.app" "/Applications/Aseprite.app"

    log_info "--- Aseprite installed successfully on macOS ---"
}

# Main execution block
if [ "$(id -u)" -eq 0 ]; then
    log_error "This script should not be run as root. Please run it as a normal user, and it will prompt for sudo when necessary."
fi

case "$(uname -s)" in
    Linux*)
        install_on_linux
        ;;
    Darwin*)
        install_on_macos
        ;;
    *)
        log_error "Unsupported operating system. This script currently only supports Linux and macOS."
        ;;
esac

cleanup
