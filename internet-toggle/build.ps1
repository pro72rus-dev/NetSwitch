# Сборка NetSwitch.exe
# Запускать: .\build.ps1

pyinstaller --onefile --noconsole --uac-admin --clean --name "NetSwitch" main.py
if ($?) {
    Copy-Item -Force "dist\NetSwitch.exe" "release\NetSwitch.exe"
    Write-Host "NetSwitch.exe -> release\" -ForegroundColor Green
} else {
    Write-Host "Ошибка сборки NetSwitch!" -ForegroundColor Red
    exit 1
}

Remove-Item -Recurse -Force "build", "dist" -ErrorAction SilentlyContinue
Remove-Item -Force "*.spec" -ErrorAction SilentlyContinue
Write-Host "Готово!" -ForegroundColor Green
