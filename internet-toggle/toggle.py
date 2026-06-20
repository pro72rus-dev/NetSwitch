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


def get_active_adapters() -> list[dict]:
    global _cached_names
    if _cached_names:
        return [{'Name': n} for n in _cached_names]
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
    global _cached_names
    if not _cached_names:
        _cached_names = list(adapter_names)

    errors = []
    for name in adapter_names:
        rc, _, err = _run(['netsh', 'interface', 'set', 'interface', f'name={name}', 'admin=disable'])
        if rc != 0:
            errors.append(f'{name} — {err or "error"}')
    return errors


def enable_adapters(adapter_names: list[str]) -> list[str]:
    if not adapter_names:
        return []
    global _cached_names

    errors = []
    for name in adapter_names:
        rc, _, err = _run(['netsh', 'interface', 'set', 'interface', f'name={name}', 'admin=enable'])
        if rc != 0:
            errors.append(f'{name} — {err or "error"}')
    _cached_names = []
    return errors


def check_internet() -> bool:
    try:
        rc, _, _ = _run(['ping', '-n', '1', '-w', '1000', '8.8.8.8'])
        return rc == 0
    except Exception:
        return False
