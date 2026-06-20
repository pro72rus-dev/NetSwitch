pyinstaller --onefile --noconsole --uac-admin --clean --name "NetSwitch" main.py
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
