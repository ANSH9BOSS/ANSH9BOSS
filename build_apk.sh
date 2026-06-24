#!/bin/bash
# Native Android APK Compilation Script for ANSH9BOSS
set -e

echo "=== STARTING NATIVE ANDROID APK BUILD ==="
SDK_DIR="/home/ubuntu/android-sdk"
mkdir -p "$SDK_DIR"

if [ ! -f "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" ]; then
    echo "[*] Downloading Android SDK command line tools..."
    curl -sSL -o /home/ubuntu/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
    
    echo "[*] Extracting command line tools..."
    unzip -q /home/ubuntu/cmdline-tools.zip -d "$SDK_DIR"
    
    echo "[*] Setting up SDK folder structure..."
    mkdir -p "$SDK_DIR/cmdline-tools/latest"
    mv "$SDK_DIR/cmdline-tools/bin" "$SDK_DIR/cmdline-tools/latest/"
    mv "$SDK_DIR/cmdline-tools/lib" "$SDK_DIR/cmdline-tools/latest/"
    mv "$SDK_DIR/cmdline-tools/source.properties" "$SDK_DIR/cmdline-tools/latest/"
    mv "$SDK_DIR/cmdline-tools/NOTICE.txt" "$SDK_DIR/cmdline-tools/latest/"
    
    rm -f /home/ubuntu/cmdline-tools.zip
fi

echo "[*] Installing Android SDK platforms, platform-tools, and build tools (SDK 34)..."
# Automatically accept licenses and install tools
yes | "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" --sdk_root="$SDK_DIR" "platforms;android-34" "build-tools;34.0.0" "platform-tools"

echo "[*] Exporting ANDROID_HOME..."
export ANDROID_HOME="$SDK_DIR"

echo "[*] Compiling the APK using Gradle..."
cd /home/ubuntu/ansh9boss/android
# Run gradle to build debug APK
gradle assembleDebug

echo "[*] Copying built APK to web static folder..."
mkdir -p /home/ubuntu/ansh9boss/web/static
cp /home/ubuntu/ansh9boss/android/app/build/outputs/apk/debug/app-debug.apk /home/ubuntu/ansh9boss/web/static/ansh9boss.apk

echo "=== APK NATIVE BUILD SUCCESSFUL ==="
