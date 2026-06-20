<div align="center">

# <img src="https://cdn-icons-png.flaticon.com/128/3899/3899864.png" height=28 /> NetSwitch

**Отключение и включение интернета одной клавишей** | **Toggle internet with a single hotkey**

[**Скачать / Download**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe) · [**Релизы / Releases**](https://github.com/pro72rus-dev/NetSwitch/releases)

[English](#english) · [Русский](#русский)

</div>

---

# English

## ⚡Features

- **Instant toggle** — disable/enable all network adapters with one hotkey
- **Works over games** — notifications appear above fullscreen/borderless applications
- **System tray** — runs in background, doesn't clutter your taskbar
- **Dark GUI** — minimal interface with hotkey configuration
- **EN/RU** — full language support for interface and notifications
- **Russian keyboard** — auto-detects keys from Russian layout
- **Auto-install** — first run installs to `%LOCALAPPDATA%\NetSwitch`
- **Self-update** — checks for updates on startup
- **Clean uninstall** — `NetSwitch.exe --uninstall`

## ⚙️Installation

1. Download [**NetSwitch.exe**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe)
2. Run it — installation is automatic
3. Done! Press `Ctrl + End` to toggle internet

> [!TIP]
> NetSwitch installs itself to `%LOCALAPPDATA%\NetSwitch` and registers in Windows "Add or Remove Programs".

## 🖱️Usage

| Action | How |
|--------|-----|
| Toggle internet | `Ctrl + End` |
| Open window | Double-click tray icon |
| Minimize to tray | `─` button in title bar |
| Change hotkey | **Change** → press keys → **Confirm** |
| Switch language | `EN` / `RU` button in title bar |
| Uninstall | `NetSwitch.exe --uninstall` |

## 🔑Hotkeys

Default: `Ctrl + End`

Supported combinations:
- `Ctrl`, `Alt`, `Shift`, `Win` + any key
- `F1`–`F24`, `End`, `Home`, `Delete`, `Insert`, `Page Up/Down`
- `Space`, `Enter`, `Tab`, `Backspace`, `Caps Lock`, `Num Lock`

> [!NOTE]
> Single letters and digits are not allowed as hotkeys to avoid accidental triggers.

## 🛠️Building from source

### Requirements

- Python 3.11+
- Windows 10/11

### Setup

```bash
git clone https://github.com/pro72rus-dev/NetSwitch.git
cd NetSwitch
pip install -r requirements.txt
```

### Build exe

```bash
pip install pyinstaller
.\build.ps1
```

Output: `NetSwitch/release/NetSwitch.exe`

## 📁Project structure

```
NetSwitch/
├── main.py          # Entry point, hotkeys, tray, auto-install, self-update
├── gui.py           # Dark GUI (tkinter), hotkey binding
├── toggle.py        # Adapter management (netsh), parallel toggle
├── notifier.py      # Overlay notifications (topmost, fade-in/out)
├── strings.py       # Localization (EN/RU)
├── build.ps1        # Build script
├── requirements.txt # Dependencies
└── start.bat        # Run from source
```

## ❓FAQ

### Nothing happens when I press the hotkey

Make sure NetSwitch is running (check the system tray). The hotkey is global and works from any application.

### Notifications don't appear over my game

NetSwitch uses `WS_EX_TOPMOST` to stay above fullscreen windows. If your game uses exclusive fullscreen, try switching to borderless windowed mode.

### How to change the hotkey?

1. Open the NetSwitch window (double-click tray icon)
2. Click **Change**
3. Press your desired key combination
4. Click **Confirm**

### The hotkey shows Russian letters

This is fixed — all keys are automatically converted to English layout regardless of your current keyboard layout.

### How to completely remove NetSwitch?

Run `NetSwitch.exe --uninstall` — this removes the executable, config folder, and registry entries.

## ⚖️License

[MIT](LICENSE) © [pro72rus](https://github.com/pro72rus-dev)

---

# Русский

## ⚡Возможности

- **Мгновенное переключение** — отключение и включение всех адаптеров одной клавишей
- **Работает поверх игр** — уведомления отображаются поверх полноэкранных приложений
- **Системный трей** — работает в фоне, не засоряет панель задач
- **Тёмный интерфейс** — минималистичный GUI с настройкой клавиши
- **EN/RU** — полная поддержка языков для интерфейса и уведомлений
- **Русская клавиатура** — автоматическое распознавание клавиш с русской раскладки
- **Автоустановка** — при первом запуске устанавливается в `%LOCALAPPDATA%\NetSwitch`
- **Самообновление** — проверка обновлений при запуске
- **Чистая деинсталляция** — `NetSwitch.exe --uninstall`

## ⚙️Установка

1. Скачайте [**NetSwitch.exe**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe)
2. Запустите файл — установка происходит автоматически
3. Готово! Нажмите `Ctrl + End` для отключения интернета

> [!TIP]
> NetSwitch устанавливается в `%LOCALAPPDATA%\NetSwitch` и регистрируется в «Установка и удаление программ» Windows.

## 🖱️Использование

| Действие | Как |
|----------|-----|
| Вкл/Выкл интернет | `Ctrl + End` |
| Открыть окно | Двойной клик по иконке в трее |
| Скрыть в трей | Кнопка `─` в заголовке |
| Сменить клавишу | **Change** → нажать комбинацию → **Confirm** |
| Сменить язык | Кнопка `EN` / `RU` в заголовке |
| Удалить | `NetSwitch.exe --uninstall` |

## 🔑Горячие клавиши

По умолчанию: `Ctrl + End`

Поддерживаются комбинации:
- `Ctrl`, `Alt`, `Shift`, `Win` + любая клавиша
- `F1`–`F24`, `End`, `Home`, `Delete`, `Insert`, `Page Up/Down`
- `Space`, `Enter`, `Tab`, `Backspace`, `Caps Lock`, `Num Lock`

> [!NOTE]
> Одиночные буквы и цифры запрещены в качестве горячих клавиш для защиты от случайного срабатывания.

## 🛠️Сборка из исходников

### Требования

- Python 3.11+
- Windows 10/11

### Установка

```bash
git clone https://github.com/pro72rus-dev/NetSwitch.git
cd NetSwitch
pip install -r requirements.txt
```

### Сборка exe

```bash
pip install pyinstaller
.\build.ps1
```

Результат: `NetSwitch/release/NetSwitch.exe`

## 📁Структура проекта

```
NetSwitch/
├── main.py          # Точка входа, горячие клавиши, трей, автоустановка
├── gui.py           # Тёмный GUI (tkinter), привязка клавиш
├── toggle.py        # Управление адаптерами (netsh), параллельный toggle
├── notifier.py      # Оверлей-уведомления (topmost, fade-in/out)
├── strings.py       # Локализация (EN/RU)
├── build.ps1        # Скрипт сборки
├── requirements.txt # Зависимости
└── start.bat        # Запуск из исходников
```

## ❓Частые вопросы

### Ничего не происходит при нажатии горячей клавиши

Убедитесь, что NetSwitch запущен (проверьте системный трей). Горячая клавиша глобальная и работает из любого приложения.

### Уведомления не отображаются поверх игры

NetSwitch использует `WS_EX_TOPMOST` для отображения поверх окон. Если игра использует эксклюзивный полный экран, переключите её в оконный или безрамочный режим.

### Как сменить горячую клавишу?

1. Откройте окно NetSwitch (двойной клик по иконке в трее)
2. Нажмите **Change**
3. Нажмите нужную комбинацию клавиш
4. Нажмите **Confirm**

### В интерфейсе отображаются русские буквы

Это исправлено — все клавиши автоматически конвертируются в английскую раскладку независимо от текущей раскладки клавиатуры.

### Как полностью удалить NetSwitch?

Запустите `NetSwitch.exe --uninstall` — это удалит exe, папку конфига и записи реестра.

## ⚖️Лицензия

[MIT](LICENSE) © [pro72rus](https://github.com/pro72rus-dev)

---

<div align="center">

⭐ Если проект понравился — поставьте звёздку!

</div>
