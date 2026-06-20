import socket
import subprocess
import urllib.request
import urllib.error

_si = subprocess.STARTUPINFO()
_si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

_cached_names: list[str] = []


def _run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd, capture_output=True, startupinfo=_si,
    )
    stdout = proc.stdout.decode('utf-8', errors='replace') if proc.stdout else ''
    stderr = proc.stderr.decode('utf-8', errors='replace') if proc.stderr else ''
    return proc.returncode, stdout.strip(), stderr.strip()


def _run_async(cmd: list[str]) -> subprocess.Popen:
    return subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=_si,
    )


def get_active_adapters() -> list[dict]:
    global _cached_names
    rc, out, _ = _run(['netsh', 'interface', 'show', 'interface'])
    if rc != 0 or not out:
        return []
    adapters = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[1] in ('Подключен', 'Connected'):
            name = ' '.join(parts[3:])
            adapters.append({'Name': name})
    _cached_names = [a['Name'] for a in adapters]
    return adapters


# Ключевые слова виртуальных адаптеров — только для фильтрации в уведомлениях
_VIRTUAL_KEYWORDS = (
    'tun', 'tap', 'vpn', 'virtual', 'loopback', 'pseudo', 'hamachi',
    'vmware', 'vbox', 'hyper-v', 'docker', 'wsl', 'nordvpn', 'openvpn',
    'wireguard', 'cisco', 'fortinet', 'npcap', 'miniport',
)


def filter_display_names(names: list[str]) -> list[str]:
    """Возвращает только реальные адаптеры для показа в уведомлениях."""
    filtered = [n for n in names if not any(kw in n.lower() for kw in _VIRTUAL_KEYWORDS)]
    return filtered if filtered else names  # если всё отфильтровалось — показываем всё


def disable_adapters(adapter_names: list[str]) -> list[str]:
    if not adapter_names:
        return []

    procs = []
    for name in adapter_names:
        procs.append((name, _run_async(['netsh', 'interface', 'set', 'interface', f'name={name}', 'admin=disable'])))

    errors = []
    for name, proc in procs:
        proc.wait()
        if proc.returncode != 0:
            errors.append(f'{name} — disable failed')
    return errors


def enable_adapters(adapter_names: list[str]) -> list[str]:
    if not adapter_names:
        return []
    global _cached_names

    procs = []
    for name in adapter_names:
        procs.append((name, _run_async(['netsh', 'interface', 'set', 'interface', f'name={name}', 'admin=enable'])))

    errors = []
    for name, proc in procs:
        proc.wait()
        if proc.returncode != 0:
            errors.append(f'{name} — enable failed')
    if not errors:
        _cached_names = []
    return errors


def check_internet() -> bool:
    """Проверка через HTTP HEAD запрос к Cloudflare — самый надёжный способ."""
    try:
        req = urllib.request.Request('http://1.1.1.1', method='HEAD')
        urllib.request.urlopen(req, timeout=0.5)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        pass
    
    # Fallback — сырой TCP на порт 80
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(('1.1.1.1', 80))
        sock.close()
        return result == 0
    except Exception:
        pass
    
    return False
