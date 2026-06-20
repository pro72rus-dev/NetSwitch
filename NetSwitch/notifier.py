import threading
import tkinter as tk
import ctypes

_root = None
_fade_job = None
_q_started = threading.Event()

HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_FRAMECHANGED = 0x0020
GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080

_user32 = ctypes.windll.user32


def _force_topmost(hwnd):
    try:
        h = _user32.GetParent(hwnd)
        if not h:
            h = hwnd
        style = _user32.GetWindowLongW(h, GWL_EXSTYLE)
        _user32.SetWindowLongW(h, GWL_EXSTYLE,
                               style | WS_EX_TOPMOST | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        _user32.SetWindowPos(h, HWND_TOPMOST, 0, 0, 0, 0,
                             SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_FRAMECHANGED)
    except Exception:
        pass


def _loop():
    global _root
    _root = tk.Tk()
    _root.withdraw()
    _root.overrideredirect(True)
    _root.attributes('-topmost', True)
    _root.attributes('-alpha', 0.0)
    _root.configure(bg='#2b2b2b')
    _root.after(100, lambda: _q_started.set())
    _root.mainloop()


def _ensure():
    if _root is None:
        _q_started.clear()
        th = threading.Thread(target=_loop, daemon=True)
        th.start()
        _q_started.wait(timeout=5)


def _cancel_fade():
    global _fade_job
    if _fade_job is not None and _root:
        try:
            _root.after_cancel(_fade_job)
        except Exception:
            pass
        _fade_job = None


def show_notification(title, message):
    _ensure()
    if not _root:
        return
    sw = _root.winfo_screenwidth()
    sh = _root.winfo_screenheight()
    ww, wh = 260, 52
    x = sw - ww - 16
    y = sh - wh - 80
    _root.after(0, lambda: _do_show(title, message, x, y, ww, wh))


def _do_show(title, message, x, y, ww, wh):
    global _fade_job
    _cancel_fade()
    for w in _root.winfo_children():
        w.destroy()

    _root.geometry(f'{ww}x{wh}+{x}+{y}')
    _root.attributes('-alpha', 0.0)

    tk.Label(_root, text=title, font=('Segoe UI', 9, 'bold'),
             bg='#2b2b2b', fg='white', anchor='w'
             ).pack(fill='x', padx=10, pady=(8, 0))

    tk.Label(_root, text=message, font=('Segoe UI', 8),
             bg='#2b2b2b', fg='#a0a0a0', anchor='w', justify='left'
             ).pack(fill='x', padx=10, pady=(1, 7))

    _root.deiconify()
    _force_topmost(_root.winfo_id())
    _fade(0.0, 0.9, 12, 15)
    _fade_job = _root.after(2500, lambda: _fade(0.9, 0.0, 12, 15))


def _fade(start, end, steps, delay_ms=15):
    global _fade_job
    if not _root:
        return
    vals = [start + (end - start) * (i + 1) / steps for i in range(steps)]
    vals.append(end)

    def apply(i):
        global _fade_job
        if not _root:
            return
        if i < len(vals):
            _root.attributes('-alpha', vals[i])
            _fade_job = _root.after(delay_ms, lambda: apply(i + 1))
        elif end == 0.0:
            _root.withdraw()

    apply(0)


def hide_notification():
    _ensure()
    if _root:
        _cancel_fade()
        _root.after(0, lambda: _fade(0.9, 0.0, 8, 15))
