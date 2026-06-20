$dll = python -c "import pydivert,os; print(os.path.join(os.path.dirname(pydivert.__file__),'windivert_dll'))"
pyinstaller --onefile --noconsole --uac-admin --clean --add-data "$dll\WinDivert64.dll;pydivert\windivert_dll" --add-data "$dll\WinDivert64.sys;pydivert\windivert_dll" --name "NetSwitch" --version "1.0.4" --author "pro72rus" main.py
if ($?) {
    Copy-Item -Force "dist\NetSwitch.exe" "release\NetSwitch.exe"
    Write-Host "Build OK: release\NetSwitch.exe" -ForegroundColor Green
} else {
    Write-Host "Build FAILED" -ForegroundColor Red
    exit 1
}

Remove-Item -Recurse -Force "build", "dist" -ErrorAction SilentlyContinue
Remove-Item -Force "*.spec" -ErrorAction SilentlyContinue
Write-Host "Done" -ForegroundColor Green
