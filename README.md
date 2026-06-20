<div align="center">

<img src="https://cdn-icons-png.flaticon.com/128/3899/3899864.png" height=64 />

# NetSwitch

### Отключение и включение интернета одной клавишей

![Version](https://img.shields.io/badge/version-1.1.0-0078D4?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-4CAF50?style=for-the-badge)

<br>

[**⬇️ Скачать NetSwitch.exe**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe) · [**📄 Релизы**](https://github.com/pro72rus-dev/NetSwitch/releases) · [**🐛 Сообщить об ошибке**](https://github.com/pro72rus-dev/NetSwitch/issues)

<br>

</div>

---

> [!IMPORTANT]
> ### 🖥️ Как это работает
> NetSwitch физически отключает/включает **все сетевые адаптеры** через `netsh`.  
> Это **не** обход блокировок, **не** прокси, **не** VPN — это мгновенное обесточивание ПК от интернета одной клавишей.  
> Идеально для быстрого отключения сети во время игр, стримов или по требованию.

---

<div align="center">

## Быстрый старт

</div>

### 1️⃣ Скачать

[**NetSwitch.exe**](https://github.com/pro72rus-dev/NetSwitch/releases/latest/download/NetSwitch.exe) (~12 MB)

### 2️⃣ Запустить

Дважды кликните по файлу — установка происходит автоматически

### 3️⃣ Пользоваться

Нажмите `Ctrl + End` — интернет выключен. Нажмите ещё раз — включён.

---

## ⚙️Использование

| Действие | Как |
|:---------|:----|
| 🔌 Вкл/Выкл интернет | `Ctrl + End` (или настроенная комбинация) |
| 🪟 Открыть окно | Двойной клик по иконке в трее |
| 📌 Скрыть в трей | Кнопка `─` в заголовке окна |
| 🔑 Сменить горячую клавишу | **Change** → нажать комбинацию → **Confirm** |
| 🌐 Сменить язык | Кнопка `EN` / `RU` в заголовке |
| 🗑️ Полностью удалить | `NetSwitch.exe --uninstall` |

---

## 🔑Горячие клавиши

<table>
<tr>
<td>

**По умолчанию:** `Ctrl + End`

</td>
<td>

**Модификаторы:** `Ctrl` `Alt` `Shift` `Win`

**Специальные:** `F1`–`F24` `End` `Home` `Delete` `Insert` `Page Up/Down`

**Системные:** `Space` `Enter` `Tab` `Backspace` `Caps Lock` `Num Lock`

</td>
</tr>
</table>

> [!NOTE]
> Одиночные буквы и цифры запрещены — защита от случайного срабатывания.  
> 🇷🇺 Русская раскладка поддерживается автоматически — клавиши распознаются по физическому расположению.

---

## 📁Структура проекта

<table>
<tr><td><code>main.py</code></td><td>Точка входа, глобальные горячие клавиши, системный трей, автоустановка, самообновление</td></tr>
<tr><td><code>gui.py</code></td><td>Тёмный графический интерфейс (tkinter), привязка горячих клавиш</td></tr>
<tr><td><code>toggle.py</code></td><td>Управление адаптерами через <code>netsh</code>, параллельное включение/отключение</td></tr>
<tr><td><code>notifier.py</code></td><td>Оверлей-уведомления поверх полноэкранных игр (topmost, fade-in/out)</td></tr>
<tr><td><code>strings.py</code></td><td>Локализация интерфейса и уведомлений (EN / RU)</td></tr>
<tr><td><code>build.ps1</code></td><td>Скрипт сборки exe через PyInstaller</td></tr>
<tr><td><code>requirements.txt</code></td><td>Зависимости: <code>keyboard</code>, <code>pywin32</code></td></tr>
<tr><td><code>start.bat</code></td><td>Запуск из исходников без сборки</td></tr>
</table>

---

## ☑️Частые вопросы

<details>
<summary><b>❌ Ничего не происходит при нажатии горячей клавиши</b></summary>

<br>

- Убедитесь, что NetSwitch запущен — проверьте иконку в системном трее (справа внизу, рядом с часами)
- Горячая клавиша работает глобально — из любого приложения, включая игры
- Если иконки нет в трее, запустите `NetSwitch.exe` заново

</details>

<details>
<summary><b>🖥️ Уведомления не отображаются поверх игры</b></summary>

<br>

- NetSwitch использует `WS_EX_TOPMOST` для отображения поверх окон
- Если игра использует **эксклюзивный полный экран** — переключите её в **оконный** или **безрамочный** режим
- Уведомления появляются в правом нижнем углу и исчезают через 2.5 секунды

</details>

<details>
<summary><b>🔑 Как сменить горячую клавишу?</b></summary>

<br>

1. Дважды кликните по иконке NetSwitch в трее — откроется окно
2. Нажмите кнопку **Change**
3. Нажмите нужную комбинацию клавиш (например `Ctrl+K`)
4. Нажмите зелёную кнопку **Confirm** для подтверждения

> [!CAUTION]
> Если нажать **Cancel** или не подтвердить в течение 30 секунд — старая клавиша восстановится автоматически.

</details>

<details>
<summary><b>🇷🇺 В интерфейсе русские буквы вместо английских</b></summary>

<br>

- Это исправлено в текущей версии
- Все клавиши автоматически конвертируются в английскую раскладку
- `alt+у` отображается как `alt+e` — это нормально

</details>

<details>
<summary><b>🔐 Программа требует права администратора</b></summary>

<br>

- NetSwitch управляет адаптерами через `netsh` — для этого нужны права администратора
- При запуске Windows запросит повышение прав (UAC)
- Это необходимо для отключения/включения адаптеров

</details>

<details>
<summary><b>🌐 Интерфейс на английском, но я хочу русский</b></summary>

<br>

- Нажмите кнопку `EN` в заголовке окна — переключится на `RU`
- Язык сохраняется в конфиге и запоминается между запусками

</details>

<details>
<summary><b>🗑️ Как полностью удалить NetSwitch?</b></summary>

<br>

```
NetSwitch.exe --uninstall
```

Это удалит:
- Файл `NetSwitch.exe` из `%LOCALAPPDATA%\NetSwitch`
- Папку конфига `%APPDATA%\NetSwitch`
- Записи из реестра Windows

</details>

<details>
<summary><b>❓ Не нашли свою проблему?</b></summary>

<br>

Создайте [**Issue**](https://github.com/pro72rus-dev/NetSwitch/issues) в репозитории — мы поможем!

</details>

---

## 🗒️Сборка из исходников

### Требования

- Python 3.11+
- Windows 10/11
- PyInstaller

### Установка и сборка

```bash
git clone https://github.com/pro72rus-dev/NetSwitch.git
cd NetSwitch
pip install -r requirements.txt
pip install pyinstaller
.\build.ps1
```

Готовый файл: `NetSwitch/release/NetSwitch.exe`

> [!NOTE]
> Собранный exe автоматически устанавливается при первом запуске. Отдельный установщик не требуется.

---

## ⚖️Лицензирование

Проект распространяется на условиях лицензии [MIT](LICENSE)

## 🩷Автор

**pro72rus** — разработка и поддержка

[![Contributors](https://contrib.rocks/image?repo=pro72rus-dev/NetSwitch)](https://github.com/pro72rus-dev/NetSwitch/graphs/contributors)
