# Aseprite Installer for Linux(Debian-based) and MacOS

This script automates the installation process of Aseprite, whose original repository can be found at:

[https://github.com/aseprite/aseprite](https://github.com/aseprite/aseprite)

The manual installation instructions for Aseprite are available at:

[https://github.com/aseprite/aseprite/blob/main/INSTALL.md](https://github.com/aseprite/aseprite/blob/main/INSTALL.md)

## Requirements

- Python 3.6 or higher
- Linux or MacOS operating system
- Xcode command line tools (only for MacOS)

## Installation

1. Clone this repository to your local machine.
2. Navigate to the directory containing the script.
3. Install the required dependencies using the following command:

```bash
pip3 install -r requirements.txt
```

### Usage

If you **have not used this script before**, use the following command to **install Aseprite**:

```bash
python3 install.py
```

If you **have used this script before** and want to **update the Aseprite version**, use the following command:

```bash
sudo python3 update.py
```

If you **want to uninstall Aseprite**, use the following command:

```bash
sudo python3 uninstall.py
```

### On Linux installation  this script will:

1. Check if the operating system is Linux.
2. Update and upgrade the system.
3. Install necessary dependencies.
4. Download and install Skia.
5. Download and install Aseprite.
6. Build Aseprite.
7. Move Aseprite to the appropriate directory.
8. Create a desktop file for Aseprite.
9. Give execution permission to the desktop file.

### On MacOs installation this script will:

1. Check if the operating system is MacOS.
2. Install necessary dependencies.
3. Download and install Skia.
4. Download and install Aseprite.
5. Build Aseprite.
6. Move Aseprite to the appropriate directory.
7. Bundle MacOS Aseprite.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
