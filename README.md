# Aseprite Installer for Linux (Debian-based) and macOS

This script automates the installation process of Aseprite. The original repository is:

[https://github.com/aseprite/aseprite](https://github.com/aseprite/aseprite)

Manual installation instructions for Aseprite are available at:

[https://github.com/aseprite/aseprite/blob/main/INSTALL.md](https://github.com/aseprite/aseprite/blob/main/INSTALL.md)

## Requirements

- Linux or macOS
- Xcode Command Line Tools (macOS only)
- Homebrew (macOS only)

## Installation using the Bash script (`install.sh`)

1. Clone this repository to your local machine.
2. Navigate to the directory containing the script.
3. Make the script executable:

```bash
chmod +x install.sh
```

4. Run the script:

```bash
./install.sh
```

> **Note:** Do not run the script as root. The script will prompt for `sudo` only when necessary.

### What does the script do?

#### On Linux:
1. Checks that the OS is Linux.
2. Updates and upgrades the system.
3. Installs required dependencies (`g++`, `clang`, `cmake`, `ninja`, etc).
4. Downloads and extracts Skia.
5. Downloads and extracts Aseprite.
6. Builds Aseprite.
7. Moves binaries to `/opt/aseprite`.
8. Creates a `.desktop` file for Aseprite.
9. Sets executable permissions for the `.desktop` file.

#### On macOS:
1. Checks that the OS is macOS.
2. Installs Xcode Command Line Tools if needed.
3. Installs required dependencies (`cmake`, `ninja` via Homebrew).
4. Downloads and extracts Skia and Aseprite.
5. Builds Aseprite for the detected architecture (x86_64 or ARM64).
6. Creates an Aseprite `.app` bundle and copies it to `/Applications`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.