<div align="center">

<img src="https://img.shields.io/badge/NetSwitch-v1.0.0-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="NetSwitch">

# NetSwitch

### Мгновенное отключение интернета одной клавишей

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows_10/11-0078D4?style=flat&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Release](https://img.shields.io/github/v/release/pro72rus-dev/NetSwitch?style=flat&color=blue)

<br>

**NetSwitch** — лёгкая утилита для мгновенного отключения/включения всех сетевых адаптеров через горячую клавишу.  
Работает в системном трее, отображает уведомления поверх полноэкранных игр, полностью переведена на EN/RU.

<br>

[**Скачать NetSwitch.exe**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe) · [**Релизы**](https://github.com/pro72rus-dev/NetSwitch/releases) · [**Report Bug**](https://github.com/pro72rus-dev/NetSwitch/issues)

</div>

---

## Возможности

<table>
<tr>
<td width="50%">

#### Переключение
- Все адаптеры отключаются/включаются **параллельно**
- Горячая клавиша работает из любого места
- Защита от повторного срабатывания (debounce 1с)

</td>
<td width="50%">

#### Интерфейс
- Тёмный минималистичный GUI
- Системный трей с双击 для открытия
- Оверлеи **поверх полноэкранных игр**
- Переключение EN/RU одной кнопкой

</td>
</tr>
<tr>
<td>

#### Горячие клавиши
- `Ctrl`, `Alt`, `Shift`, `Win` + любая клавиша
- `F1`–`F24`, `End`, `Home`, `Delete` и др.
- Авто-распознавание русской раскладки

</td>
<td>

#### Система
- Автоустановка при первом запуске
- Самообновление через GitHub
- Регистрация в «Установка и удаление программ»
- Полная деинсталляция: `--uninstall`

</td>
</tr>
</table>

---

## Быстрый старт

### 1. Скачать

[**NetSwitch.exe**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe) (~12 MB)

### 2. Запустить

При первом запуске NetSwitch:
- Автоматически установится в `%LOCALAPPDATA%\NetSwitch`
- Зарегистрируется в системе
- Покажет приветственное уведомление

### 3. Пользоваться

| Действие | Как |
|----------|-----|
| Вкл/Выкл интернет | `Ctrl + End` |
| Открыть окно | Двойной клик по иконке в трее |
| Скрыть в трей | Кнопка `─` в заголовке |
| Сменить клавишу | **Change** → нажать комбинацию → **Confirm** |
| Сменить язык | Кнопка `EN`/`RU` в заголовке |
| Деинсталляция | `NetSwitch.exe --uninstall` |

---

## Сборка из исходников

### Требования

- Python 3.11+
- Windows 10/11

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Сборка exe

```bash
pip install pyinstaller
.\build.ps1
```

Готовый файл: `release/NetSwitch.exe`

### Запуск без сборки

```bash
python main.py
```

Или через `start.bat`.

---

## Структура проекта

```
NetSwitch/
├── internet-toggle/
│   ├── main.py          # Точка входа, горячие клавиши, трей, автоустановка
│   ├── gui.py           # Тёмный GUI (tkinter), привязка клавиш
│   ├── toggle.py        # Управление адаптерами (netsh), параллельный toggle
│   ├── notifier.py      # Оверлей-уведомления поверх игр (topmost)
│   ├── strings.py       # Локализация EN/RU
│   ├── build.ps1        # Скрипт сборки exe
│   ├── requirements.txt # Зависимости
│   └── start.bat        # Запуск из исходников
├── LICENSE
└── README.md
```

---

## Технические детали

| Компонент | Технология |
|-----------|-----------|
| GUI | `tkinter` + `overrideredirect` + `WS_EX_TOPMOST` |
| Трей | `pywin32` (`Shell_NotifyIcon`) |
| Горячие клавиши | `keyboard` (global hooks) |
| Адаптеры | `netsh interface set interface` |
| Уведомления | `tkinter` + `ctypes` topmost overlay |
| Сборка | `PyInstaller --onefile --noconsole --uac-admin` |

---

## Лицензия

[MIT](LICENSE) © [pro72rus](https://github.com/pro72rus-dev)

---

<div align="center">

⭐ Если проект Helpful — поставьте звёздку!

</div>
