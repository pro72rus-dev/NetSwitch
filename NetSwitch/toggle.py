import subprocess
import threading

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
    _cached_names = []
    return errors


def check_internet() -> bool:
    try:
        rc, _, _ = _run(['ping', '-n', '1', '-w', '200', '8.8.8.8'])
        return rc == 0
    except Exception:
        return False
