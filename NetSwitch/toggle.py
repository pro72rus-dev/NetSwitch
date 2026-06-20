import socket
import subprocess

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


_PING_TARGETS = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
_DNS_HOSTS = ['google.com', 'cloudflare.com', 'ya.ru']


def check_internet() -> bool:
    for host in _DNS_HOSTS:
        try:
            socket.create_connection((host, 53), timeout=0.3)
            return True
        except (OSError, socket.timeout):
            continue
    for target in _PING_TARGETS:
        try:
            rc, _, _ = _run(['ping', '-n', '1', '-w', '300', target])
            if rc == 0:
                return True
        except Exception:
            continue
    return False
