#!/bin/bash

# Upgrade script for Aseprite (Linux and macOS)
# Removes the previous installation and installs the latest version

log_info() {
    echo "INFO - $1"
}

log_error() {
    echo "ERROR - $1" >&2
    exit 1
}

# Run uninstall.sh
run_uninstall() {
    if [ -f "./uninstall.sh" ]; then
        log_info "Running uninstall.sh to remove previous Aseprite installation..."
        bash ./uninstall.sh || log_error "Uninstall failed. Aborting upgrade."
    else
        log_info "uninstall.sh not found. Skipping uninstall step."
    fi
}

# Run install.sh
run_install() {
    if [ -f "./install.sh" ]; then
        log_info "Running install.sh to install the latest Aseprite version..."
        bash ./install.sh || log_error "Install failed. Upgrade incomplete."
    else
        log_error "install.sh not found. Cannot proceed with upgrade."
    fi
}

# Main execution block
if [ "$(id -u)" -eq 0 ]; then
    log_error "Do not run this script as root. It will prompt for sudo when needed."
fi

run_uninstall
run_install

log_info "Aseprite upgrade complete."

