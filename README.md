# Aseprite Installer for Linux (Debian-based) and macOS

This script automates the installation process of Aseprite. The original repository is:

[https://github.com/aseprite/aseprite](https://github.com/aseprite/aseprite)

Manual installation instructions for Aseprite are available at:

[https://github.com/aseprite/aseprite/blob/main/INSTALL.md](https://github.com/aseprite/aseprite/blob/main/INSTALL.md)

## Requirements

- Linux or macOS
- Xcode Command Line Tools (macOS only)
- Homebrew (macOS only)

> **Note:** Do not run any script as root. The script will prompt for `sudo` only when necessary.

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

## Uninstalling Aseprite (`uninstall.sh`)

To remove Aseprite from your system, use the uninstall script:

1. Make the script executable:

```bash
chmod +x uninstall.sh
```

2. Run the script:

```bash
./uninstall.sh
```

### What does the uninstall script do?

#### On Linux:
- Removes the `/opt/aseprite` directory
- Removes the desktop entry file from `~/.local/share/applications/`
- Cleans up build directories and temporary files

#### On macOS:
- Removes `/Applications/Aseprite.app`
- Cleans up build directories and temporary files

## Upgrading Aseprite (`upgrade.sh`)

To upgrade Aseprite to the latest version, use the upgrade script:

1. Make the script executable:

```bash
chmod +x upgrade.sh
```

2. Run the script:

```bash
./upgrade.sh
```

### What does the upgrade script do?

The upgrade script performs a complete reinstallation by:
1. Running `uninstall.sh` to remove the current installation
2. Running `install.sh` to install the latest version

This ensures you always have the most recent version of Aseprite with a clean installation.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.