$ErrorActionPreference = "Stop"
Write-Host "============================================="
Write-Host "   ANSH9BOSS - AUTO INSTALLER AND RUNNER"
Write-Host "============================================="

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
} catch {
    Write-Host "[-] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "[+] Opening Python download page..." -ForegroundColor Yellow
    Start-Process "https://www.python.org/downloads/"
    Write-Host "Please install Python (ensure you check 'Add Python to PATH') and restart this script." -ForegroundColor Yellow
    Pause
    exit 1
}

# Install dependencies
Write-Host "[*] Installing Python dependencies (rich, pyfiglet)..." -ForegroundColor Cyan
python -m pip install rich pyfiglet

# Check if script exists, if not download it
if (-not (Test-Path "ansh9boss.py")) {
    Write-Host "[*] Downloading latest ansh9boss.py from GitHub..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ANSH9BOSS/ansh9boss/main/ansh9boss.py" -OutFile "ansh9boss.py"
}

# Run the script with any passed arguments
python ansh9boss.py $args

Write-Host "Press any key to exit..."
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
