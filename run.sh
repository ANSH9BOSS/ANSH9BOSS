#!/bin/bash

echo "============================================="
echo "   ANSH9BOSS - AUTO INSTALLER & RUNNER       "
echo "============================================="

# Detect if running in Termux
if [ -d "/data/data/com.termux" ]; then
    echo "[*] Android Termux environment detected."
    if ! command -v python &> /dev/null; then
        echo "[+] Installing Python..."
        pkg update -y && pkg install python -y
    fi
else
    echo "[*] Linux/macOS environment detected."
    if ! command -v python3 &> /dev/null; then
        echo "[-] Error: Python3 is not installed. Please install Python3 manually."
        exit 1
    fi
fi

# Install dependencies (fallbacks for break-system-packages overrides)
echo "[*] Installing Python dependencies (rich, pyfiglet)..."
python3 -m pip install --break-system-packages rich pyfiglet 2>/dev/null || python3 -m pip install rich pyfiglet || pip3 install rich pyfiglet || pip install rich pyfiglet

# Run the analyzer
if [ -f "ansh9boss.py" ]; then
    python3 ansh9boss.py "$@"
else
    echo "[*] Downloading latest ansh9boss.py from GitHub..."
    curl -sSL -o ansh9boss.py https://raw.githubusercontent.com/ANSH9BOSS/ansh9boss/main/ansh9boss.py
    python3 ansh9boss.py "$@"
fi
