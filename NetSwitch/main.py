import argparse
import atexit
import ctypes
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

import keyboard
import win32api
import win32con
import win32gui

from toggle import get_active_adapters, disable_adapters, enable_adapters, check_internet
from notifier import show_notification
from gui import (set_callbacks, show_window, hide_window, update_status,
                 update_hotkey, start_capture_mode, finish_capture_mode,
                 show_captured_hotkey, update_version, get_root, set_lang_callback)
from strings import set_lang, get_lang, t

VERSION = '1.0.0'
UPDATE_URL = 'https://raw.githubusercontent.com/pro72rus-dev/NetSwitch/main/update.json'

_mutex = None


def _acquire_mutex() -> bool:
    global _mutex
    try:
        _mutex = ctypes.windll.kernel32.CreateMutexW(None, False, 'NetSwitchSingleInstance')
        if ctypes.windll.kernel32.GetLastError() == 183:
            return False
        return True
    except Exception:
        return True

CONFIG_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'NetSwitch')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

_lock = threading.Lock()
_config_lock = threading.Lock()
disabled_adapter_names: list[str] = []
internet_off = False
_last_toggle: float = 0

_exit_flag = False
_hotkey_str = 'end'
_confirm_event = threading.Event()
_confirm_accepted = False

_ru_to_en = {
    'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y',
    'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']',
    'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h',
    'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';', 'э': '\'',
    'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n',
    'ь': 'm', 'б': ',', 'ю': '.', 'ё': '`',
}

_key_aliases = {
    'pb': 'pause', 'ps': 'print screen', 'pu': 'page up', 'pd': 'page down',
    'st': 'scroll lock', 'del': 'delete', 'ins': 'insert', 'sp': 'space',
    'ca': 'caps lock', 'nl': 'num lock', 'bs': 'backspace', 'ent': 'enter',
    'hm': 'home', 'ed': 'end', 'pgup': 'page up', 'pgdn': 'page down',
    'prtsc': 'print screen', 'scrlk': 'scroll lock',
}


def _fix_keyboard_layout(hotkey: str) -> str:
    parts = hotkey.split('+')
    fixed = []
    for p in parts:
        if len(p) == 1 and p.lower() in _ru_to_en:
            en = _ru_to_en[p.lower()]
            fixed.append(en.upper() if p.isupper() else en)
        else:
            fixed.append(p)
    return '+'.join(fixed)


def resolve_hotkey(hotkey: str) -> str:
    hotkey = _fix_keyboard_layout(hotkey)
    parts = hotkey.lower().split('+')
    resolved = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if p == 'pg':
            if i + 1 < len(parts) and parts[i + 1] in ('u', 'd', 'up', 'down'):
                i += 1
                resolved.append('page up' if parts[i] in ('u', 'up') else 'page down')
            else:
                resolved.append(p)
        else:
            resolved.append(_key_aliases.get(p, p))
        i += 1
    return '+'.join(resolved)


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate() -> None:
    skip = {'--bind', '--detect'}
    args = []
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] in skip:
            i += 1
            continue
        args.append(sys.argv[i])
        i += 1
    exe = sys.executable.replace('python.exe', 'pythonw.exe')
    if not os.path.exists(exe):
        exe = sys.executable
    cmd = subprocess.list2cmdline(args)
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', exe, cmd, None, 0)
    sys.exit(0)


def load_config() -> dict:
    default = {'hotkey': 'end', 'lang': 'en'}
    with _config_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    default.update(data)
            except Exception:
                pass
    return default


def save_config(cfg: dict) -> None:
    with _config_lock:
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def cleanup() -> None:
    global internet_off, disabled_adapter_names
    with _lock:
        if internet_off and disabled_adapter_names:
            enable_adapters(disabled_adapter_names)
            disabled_adapter_names = []
            internet_off = False


def _wait_internet(names: list[str]) -> None:
    for _ in range(30):
        time.sleep(0.3)
        if check_internet():
            show_notification(t('enabled'), '\n'.join(names))
            return
    show_notification(t('enabled'), '\n'.join(names))


def toggle_internet() -> None:
    global disabled_adapter_names, internet_off, _last_toggle

    now = time.time()
    if now - _last_toggle < 1.0:
        return
    _last_toggle = now

    with _lock:
        if not internet_off:
            adapters = get_active_adapters()
            if not adapters:
                show_notification(t('no_internet'),
                                  t('no_adapters'))
                return
            names = [a['Name'] for a in adapters]
            errs = disable_adapters(names)
            if errs:
                show_notification(t('error'), errs[0])
                return
            disabled_adapter_names = names
            internet_off = True
            show_notification(t('disabled'), '\n'.join(names))
        else:
            names = list(disabled_adapter_names)
            errs = enable_adapters(names)
            if errs:
                show_notification(t('error'), errs[0])
                return
            internet_off = False
            disabled_adapter_names = []
            show_notification(t('enabling'), '\n'.join(names))
            threading.Thread(target=_wait_internet, args=(names,), daemon=True).start()

    update_status(internet_off)
    _update_tray()


# ─── Hotkey validation and registration ─────────────────────────

_modifiers = {'ctrl', 'control', 'alt', 'shift', 'win', 'windows'}
_allowed_single = {
    'end', 'home', 'delete', 'insert', 'page up', 'page down',
    'pause', 'print screen', 'scroll lock', 'space', 'enter',
    'backspace', 'tab', 'caps lock', 'num lock',
}
_allowed_single.update({f'f{i}' for i in range(1, 25)})


def _validate_hotkey(hotkey: str) -> tuple[bool, str]:
    hotkey = _fix_keyboard_layout(hotkey)
    parts = hotkey.lower().split('+')
    if not parts or not all(parts):
        return False, 'Empty combination'

    for p in parts:
        if len(p) == 1 and ord(p) > 127:
            return False, f'Non-English key "{p}"'

    if len(parts) == 1:
        key = parts[0]
        if key in _modifiers:
            return False, 'Raw modifier not allowed'
        if key in _allowed_single:
            return True, ''
        if len(key) == 1 and (key.isalpha() or key.isdigit()):
            return False, f'Single key "{key}" not allowed'
        return False, f'Invalid key "{key}"'

    if not any(p in _modifiers for p in parts):
        return False, 'Modifier required (Ctrl/Alt/Shift/Win)'

    non_modifiers = [p for p in parts if p not in _modifiers]
    for k in non_modifiers:
        if len(k) == 1 and k.isalpha():
            continue
        if k in _allowed_single:
            continue
        return False, f'Invalid key "{k}"'

    return True, ''


def _register_hotkey(hotkey: str) -> bool:
    if not hotkey:
        return True
    try:
        keyboard.add_hotkey(hotkey, toggle_internet, suppress=True)
        return True
    except Exception:
        return False


# ─── Hotkey apply / rebind / confirm ────────────────────────────

def _release_modifier_keys():
    user32 = ctypes.windll.user32
    for vk in (0x10, 0x11, 0x12, 0x5B, 0x5C):
        if user32.GetAsyncKeyState(vk) & 0x8000:
            user32.keybd_event(vk, 0, 2, 0)


def _apply_hotkey(raw_hotkey: str) -> bool:
    global _hotkey_str
    fixed = _fix_keyboard_layout(raw_hotkey)
    resolved = resolve_hotkey(fixed)
    if not _register_hotkey(resolved):
        return False
    _hotkey_str = resolved
    config = load_config()
    config['hotkey'] = fixed
    save_config(config)
    update_hotkey(resolved)
    return True


def _restore_hotkey(old_hotkey: str):
    global _hotkey_str
    try:
        keyboard.remove_all_hotkeys()
    except Exception:
        pass
    if _register_hotkey(old_hotkey):
        _hotkey_str = old_hotkey
        finish_capture_mode(old_hotkey)
        show_notification(t('cancelled'), old_hotkey)
    else:
        _hotkey_str = 'end'
        _register_hotkey('end')
        update_hotkey('end')
        cfg = load_config()
        cfg['hotkey'] = 'end'
        save_config(cfg)
        finish_capture_mode('end')
        show_notification(t('hotkey_reset'), 'end')


def _rebind_hotkey() -> None:
    global _hotkey_str, _confirm_accepted
    old_hotkey = _hotkey_str
    _confirm_accepted = False
    _confirm_event.clear()

    try:
        keyboard.remove_all_hotkeys()
    except Exception:
        pass
    start_capture_mode()

    try:
        root = get_root()
        if root:
            root.after(0, lambda: root.focus_force())
    except Exception:
        pass

    hotkey = ''
    try:
        hotkey = keyboard.read_hotkey(suppress=False)
    except Exception:
        pass
    finally:
        keyboard.unhook_all()
        _release_modifier_keys()

    if not hotkey or hotkey.lower() == 'esc':
        _restore_hotkey(old_hotkey)
        return

    valid, reason = _validate_hotkey(hotkey)
    if not valid:
        _restore_hotkey(old_hotkey)
        show_notification(t('invalid_hotkey'), reason)
        return

    show_captured_hotkey(_fix_keyboard_layout(hotkey))
    _confirm_event.wait(timeout=30)

    if _confirm_accepted:
        if _apply_hotkey(hotkey):
            finish_capture_mode(_hotkey_str)
            show_notification(t('hotkey_changed'), _hotkey_str)
        else:
            _restore_hotkey(old_hotkey)
            show_notification(t('error'), t('failed_register'))
    else:
        _restore_hotkey(old_hotkey)


def _cancel_rebind():
    global _confirm_accepted
    _confirm_accepted = False
    _confirm_event.set()
    keyboard.unhook_all()


def _on_lang_change():
    config = load_config()
    config['lang'] = get_lang()
    save_config(config)
    _update_tray()


def _toggle_lang():
    new = 'ru' if get_lang() == 'en' else 'en'
    set_lang(new)
    _on_lang_change()


def _on_confirm():
    global _confirm_accepted
    _confirm_accepted = True
    _confirm_event.set()


# ─── Install / Self-update ──────────────────────────────────────

INSTALL_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
                           'NetSwitch')
_UNINSTALL_KEY = r'Software\Microsoft\Windows\CurrentVersion\Uninstall\NetSwitch'


def _is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def _is_running_from_install_dir() -> bool:
    expected = os.path.join(INSTALL_DIR, 'NetSwitch.exe')
    return os.path.abspath(sys.argv[0]).lower() == expected.lower()


def _is_installed() -> bool:
    return os.path.exists(os.path.join(INSTALL_DIR, 'NetSwitch.exe'))


def _register_uninstall():
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY)
        winreg.SetValueEx(key, 'DisplayName', 0, winreg.REG_SZ, 'NetSwitch')
        winreg.SetValueEx(key, 'DisplayVersion', 0, winreg.REG_SZ, VERSION)
        winreg.SetValueEx(key, 'Publisher', 0, winreg.REG_SZ, 'pro72rus')
        winreg.SetValueEx(key, 'InstallLocation', 0, winreg.REG_SZ, INSTALL_DIR)
        uninstall_cmd = os.path.join(INSTALL_DIR, 'NetSwitch.exe') + ' --uninstall'
        winreg.SetValueEx(key, 'UninstallString', 0, winreg.REG_SZ, uninstall_cmd)
        winreg.SetValueEx(key, 'NoModify', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'NoRepair', 0, winreg.REG_DWORD, 1)
        try:
            exe_path = os.path.join(INSTALL_DIR, 'NetSwitch.exe')
            exe_size = os.path.getsize(exe_path) // 1024
            winreg.SetValueEx(key, 'EstimatedSize', 0, winreg.REG_DWORD, exe_size)
        except Exception:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass


def _unregister_uninstall():
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY)
    except Exception:
        pass


def _do_install() -> None:
    src = os.path.abspath(sys.argv[0])
    os.makedirs(INSTALL_DIR, exist_ok=True)
    dest = os.path.join(INSTALL_DIR, 'NetSwitch.exe')
    tmp = dest + '.tmp'
    try:
        shutil.copy2(src, tmp)
        if os.path.exists(dest):
            for attempt in range(3):
                try:
                    os.remove(dest)
                    break
                except PermissionError:
                    time.sleep(1)
        if os.path.exists(dest):
            raise OSError(f'Cannot remove old exe after {3} attempts')
        os.rename(tmp, dest)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
        shutil.copy2(src, dest)
    for _ in range(10):
        if os.path.exists(dest) and os.path.getsize(dest) > 100000:
            break
        time.sleep(0.5)
    _register_uninstall()
    subprocess.Popen([dest], start_new_session=True)
    sys.exit(0)


def _do_uninstall() -> None:
    _unregister_uninstall()
    try:
        if os.path.exists(CONFIG_DIR):
            shutil.rmtree(CONFIG_DIR, ignore_errors=True)
    except Exception:
        pass
    running_from_install = _is_running_from_install_dir()
    if running_from_install:
        _unregister_uninstall()
        try:
            if os.path.exists(CONFIG_DIR):
                shutil.rmtree(CONFIG_DIR, ignore_errors=True)
        except Exception:
            pass
        bat = os.path.join(tempfile.mkdtemp(), '_uninstall.bat')
        with open(bat, 'w') as f:
            f.write('@echo off\n')
            f.write('timeout /t 2 /nobreak >nul\n')
            f.write(f'rmdir /s /q "{INSTALL_DIR}"\n')
            f.write(f'del "%~f0"\n')
        subprocess.Popen([bat], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        try:
            if os.path.exists(INSTALL_DIR):
                shutil.rmtree(INSTALL_DIR, ignore_errors=True)
        except Exception:
            pass
    sys.exit(0)


def _check_update() -> None:
    try:
        req = urllib.request.Request(UPDATE_URL, headers={'User-Agent': f'NetSwitch/{VERSION}'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        remote_ver = data.get('version', '')
        download_url = data.get('url', '')
        if not remote_ver or not download_url:
            return
        def _parse(v: str) -> tuple[int, ...]:
            return tuple(int(x) for x in v.split('.') if x.isdigit())
        if _parse(remote_ver) <= _parse(VERSION):
            return
        show_notification('Update', f'v{remote_ver} available')
        tmp_dir = tempfile.mkdtemp(prefix='NetSwitchUpdate_')
        tmp = os.path.join(tmp_dir, 'NetSwitch.exe')
        try:
            urllib.request.urlretrieve(download_url, tmp)
            if not os.path.exists(tmp) or os.path.getsize(tmp) < 100000:
                show_notification('Update', t('update_failed'))
                return
        except Exception:
            show_notification('Update', t('update_failed'))
            return
        me = os.path.abspath(sys.argv[0])
        bat = os.path.join(tmp_dir, '_update.bat')
        with open(bat, 'w') as f:
            f.write('@echo off\n')
            f.write('timeout /t 3 /nobreak >nul\n')
            f.write(f'copy /y "{tmp}" "{me}"\n')
            f.write(f'del "{tmp}"\n')
            f.write(f'start "" "{me}"\n')
            f.write(f'rmdir /s /q "{tmp_dir}"\n')
            f.write(f'del "%~f0"\n')
        subprocess.Popen([bat], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0)
    except Exception:
        pass


# ─── Tray ──────────────────────────────────────────────────────

WM_TRAY = win32con.WM_USER + 100
IDC_SHOW = 1001
IDC_EXIT = 1002

_tray_hwnd = None
_tray_nid = None
_tray_hicon = None


def _update_tray() -> None:
    global _tray_nid, _tray_hicon
    flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
    if _tray_hicon is None:
        _tray_hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    tip = 'NetSwitch \u2014 ' + (t('off') if internet_off else t('on'))

    if _tray_nid is None:
        _tray_nid = (_tray_hwnd, 0, flags, WM_TRAY, _tray_hicon, tip)
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, _tray_nid)
    else:
        _tray_nid = (_tray_hwnd, 0, flags, WM_TRAY, _tray_hicon, tip)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, _tray_nid)


def _delete_tray() -> None:
    global _tray_nid, _tray_hicon
    if _tray_nid:
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, _tray_nid)
        except Exception:
            pass
        _tray_nid = None
    if _tray_hicon:
        try:
            win32gui.DestroyIcon(_tray_hicon)
        except Exception:
            pass
        _tray_hicon = None


def _show_menu() -> None:
    menu = win32gui.CreatePopupMenu()
    try:
        win32gui.AppendMenu(menu, win32con.MF_STRING, IDC_SHOW, t('show_window'))
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, '')
        win32gui.AppendMenu(menu, win32con.MF_STRING, IDC_EXIT, t('exit'))
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(_tray_hwnd)
        win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, _tray_hwnd, None)
        win32gui.PostMessage(_tray_hwnd, win32con.WM_NULL, 0, 0)
    finally:
        win32gui.DestroyMenu(menu)


def _tray_wndproc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
    if msg == WM_TRAY:
        if lparam == win32con.WM_RBUTTONUP:
            _show_menu()
        elif lparam == win32con.WM_LBUTTONDBLCLK:
            show_window()
    elif msg == win32con.WM_COMMAND:
        if wparam == IDC_SHOW:
            show_window()
        elif wparam == IDC_EXIT:
            global _exit_flag
            _exit_flag = True
    elif msg == win32con.WM_DESTROY:
        _delete_tray()
        win32gui.PostQuitMessage(0)
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def setup_tray() -> None:
    global _tray_hwnd
    hinst = win32api.GetModuleHandle(None)
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = _tray_wndproc
    wc.hInstance = hinst
    wc.lpszClassName = 'NetSwitchTrayClass'
    win32gui.RegisterClass(wc)
    _tray_hwnd = win32gui.CreateWindow(wc.lpszClassName, '', 0, 0, 0, 0, 0, 0, 0, hinst, None)
    _update_tray()


def _sigint_handler(sig: int, frame) -> None:
    global _exit_flag
    _exit_flag = True
    cleanup()


# ─── main ──────────────────────────────────────────────────────

def main() -> None:
    global _hotkey_str

    parser = argparse.ArgumentParser(description='NetSwitch')
    parser.add_argument('--key', type=str)
    parser.add_argument('--bind', action='store_true')
    parser.add_argument('--detect', action='store_true')
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()

    os.makedirs(CONFIG_DIR, exist_ok=True)
    config = load_config()
    set_lang(config.get('lang', 'en'))

    if args.uninstall:
        _do_uninstall()
        return

    if args.detect:
        print('Press a key (Esc = exit)')
        try:
            while True:
                hk = keyboard.read_hotkey(suppress=False)
                if hk is None or hk.lower() == 'esc':
                    break
                print(f'  "{_fix_keyboard_layout(hk)}"')
        finally:
            keyboard.unhook_all()
        return

    if args.bind:
        try:
            hk = keyboard.read_hotkey(suppress=False)
            if hk and hk.lower() != 'esc':
                hk = _fix_keyboard_layout(hk)
                config['hotkey'] = hk
                save_config(config)
                print(f'Saved: {hk}')
            else:
                print('Cancelled')
        finally:
            keyboard.unhook_all()
        return

    if args.key:
        config['hotkey'] = args.key
        save_config(config)

    if _is_frozen():
        if _is_running_from_install_dir():
            pass
        elif _is_installed():
            dest = os.path.join(INSTALL_DIR, 'NetSwitch.exe')
            try:
                subprocess.Popen([dest] + sys.argv[1:], start_new_session=True)
                sys.exit(0)
            except OSError:
                _do_install()
        else:
            _do_install()

    if not _acquire_mutex():
        show_notification('NetSwitch', t('already_running'))
        sys.exit(0)

    hwnd_console = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd_console:
        ctypes.windll.user32.ShowWindow(hwnd_console, 0)

    if not is_admin():
        elevate()

    _hotkey_str = resolve_hotkey(config.get('hotkey', 'end'))
    valid, reason = _validate_hotkey(_hotkey_str)
    if not valid:
        _hotkey_str = 'end'

    if not _register_hotkey(_hotkey_str):
        _hotkey_str = 'end'
        if not _register_hotkey('end'):
            print('Critical error: failed to register hotkey')
            sys.exit(1)
        update_hotkey('end')

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, _sigint_handler)

    setup_tray()

    set_callbacks(
        on_rebind=_rebind_hotkey,
        on_cancel_capture=_cancel_rebind,
        on_confirm=_on_confirm,
        on_exit=_exit_app,
        on_minimize=hide_window,
        on_lang=_toggle_lang,
    )
    show_window()
    update_hotkey(_hotkey_str)
    update_status(internet_off)
    update_version(VERSION)

    show_notification('NetSwitch', t('install_hint'))

    threading.Thread(target=_check_update, daemon=True).start()

    while not _exit_flag:
        result = win32gui.PeekMessage(None, 0, 0, win32con.PM_REMOVE)
        if result and result[0]:
            msg = result[1]
            if msg[1] == win32con.WM_QUIT:
                break
            win32gui.TranslateMessage(msg)
            win32gui.DispatchMessage(msg)
        else:
            time.sleep(0.05)

    cleanup()
    _delete_tray()


def _exit_app() -> None:
    global _exit_flag
    _exit_flag = True


if __name__ == '__main__':
    main()
