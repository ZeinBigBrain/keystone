#!/bin/bash
# Keystone launcher for macOS. Double-click to start.
# If Python 3.8+ isn't installed, it offers to install Python 3.12 from
# python.org (macOS asks for your password once), then starts the app.
cd "$(dirname "$0")" || exit 1

PY_PKG_URL="https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg"

find_python() {
    PY=""
    for c in python3 \
             /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
             /usr/local/bin/python3 /opt/homebrew/bin/python3 python; do
        path="$(command -v "$c" 2>/dev/null)" || continue
        # Apple's /usr/bin/python3 is only a placeholder until the developer
        # tools are installed; running it pops up an install dialog, so skip it then.
        if [ "$path" = "/usr/bin/python3" ] && ! xcode-select -p >/dev/null 2>&1; then
            continue
        fi
        if "$path" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
            PY="$path"
            return
        fi
    done
}

find_python

if [ -z "$PY" ]; then
    echo
    echo "Keystone needs Python 3.8 or newer, and it isn't installed on this Mac."
    echo
    read -r -p "Install Python 3.12 from python.org now? (about 45 MB) [y/N] " answer
    if [[ "$answer" =~ ^[Yy] ]]; then
        pkg="/tmp/keystone-python.pkg"
        echo
        echo "Downloading $PY_PKG_URL"
        if curl -fL --progress-bar -o "$pkg" "$PY_PKG_URL"; then
            echo
            echo "Installing. macOS will ask for the password you use to log in to this Mac."
            if sudo installer -pkg "$pkg" -target /; then
                rm -f "$pkg"
                find_python
            else
                echo
                echo "Opening the installer instead. Click through it, then double-click start.command again."
                open "$pkg"
                read -r -p "Press Enter to close."
                exit 1
            fi
        else
            echo "The download failed. Check your internet connection."
        fi
    fi
fi

if [ -z "$PY" ]; then
    echo
    echo "Python isn't installed yet. Opening the download page:"
    echo "install Python 3, then double-click start.command again."
    open "https://www.python.org/downloads/" >/dev/null 2>&1
    echo
    read -r -p "Press Enter to close."
    exit 1
fi

"$PY" server.py
echo
read -r -p "Keystone has stopped. Press Enter to close."
