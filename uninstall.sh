#!/bin/bash

log_info() {
    echo "INFO - $1"
}

log_error() {
    echo "ERROR - $1" >&2
    exit 1
}

# Remove Aseprite from Linux
uninstall_linux() {
    log_info "Uninstalling Aseprite from /opt/aseprite..."
    if [ -d "/opt/aseprite" ]; then
        sudo rm -rf /opt/aseprite || log_error "Failed to remove /opt/aseprite."
        log_info "Removed /opt/aseprite."
    else
        log_info "/opt/aseprite not found."
    fi

    if [ -f "$HOME/.local/share/applications/aseprite.desktop" ]; then
        rm "$HOME/.local/share/applications/aseprite.desktop" || log_error "Failed to remove desktop entry."
        log_info "Removed desktop entry."
    fi

    log_info "Aseprite uninstalled from Linux."
}

# Remove Aseprite from macOS
uninstall_macos() {
    log_info "Uninstalling Aseprite from /Applications..."
    if [ -d "/Applications/Aseprite.app" ]; then
        sudo rm -rf "/Applications/Aseprite.app" || log_error "Failed to remove /Applications/Aseprite.app."
        log_info "Removed /Applications/Aseprite.app."
    else
        log_info "/Applications/Aseprite.app not found."
    fi
    log_info "Aseprite uninstalled from macOS."
}

# Remove build dependencies and temp files
cleanup() {
    log_info "Removing build directories..."
    rm -rf "$HOME/deps" /tmp/aseprite /tmp/bundle
    log_info "Removed build directories."
}

# Main execution block
if [ "$(id -u)" -eq 0 ]; then
    log_error "Do not run this script as root. It will prompt for sudo when needed."
fi

case "$(uname -s)" in
    Linux*)
        uninstall_linux
        ;;
    Darwin*)
        uninstall_macos
        ;;
    *)
        log_error "Unsupported OS. Only Linux and macOS are supported."
        ;;
esac

cleanup

log_info "Uninstallation complete."

