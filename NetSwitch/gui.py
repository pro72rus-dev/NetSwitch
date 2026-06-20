import os
import threading
import tkinter as tk
import ctypes

from strings import t, get_lang

_user32 = ctypes.windll.user32

GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080

_root = None
_on_rebind = None
_on_cancel_capture = None
_on_confirm = None
_on_exit = None
_on_minimize = None
_on_lang = None
_q_started = threading.Event()

_title_bar = None
_status_label = None
_hotkey_label = None
_rebind_btn = None
_confirm_btn = None
_rebind_hint = None
_lang_btn = None
_status_section_label = None
_hotkey_section_label = None
_is_capturing = False
_status_dot = None
_version_label = None
_made_by_label = None
_internet_off = False

BG = '#2b2b2b'
BAR = '#1a1a1a'
ACCENT = '#3a3a3a'
GREEN = '#4caf50'
RED = '#f44336'
DIM = '#666666'
WHITE = '#ffffff'

# ─── colour animation ──────────────────────────────────────────

_anim_job = None

def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(r, g, b) -> str:
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

def _animate_status(from_color: str, to_color: str, steps: int = 24, delay: int = 8):
    """Плавно меняет цвет точки и текста статуса."""
    global _anim_job
    if _anim_job is not None:
        try:
            _root.after_cancel(_anim_job)
        except Exception:
            pass
        _anim_job = None

    fr, fg_c, fb = _hex_to_rgb(from_color)
    tr, tg, tb = _hex_to_rgb(to_color)

    def step(i):
        global _anim_job
        if not _root or not _status_dot or not _status_label:
            return
        t_val = i / steps
        r = fr + (tr - fr) * t_val
        g = fg_c + (tg - fg_c) * t_val
        b = fb + (tb - fb) * t_val
        color = _rgb_to_hex(r, g, b)
        _status_dot.config(fg=color)
        _status_label.config(fg=color)
        if i < steps:
            _anim_job = _root.after(delay, lambda: step(i + 1))

    step(0)


# ─── window callbacks ──────────────────────────────────────────

def _on_minimize_click():
    if _on_minimize and not _is_capturing:
        _on_minimize()


def _on_close_click():
    if _on_exit:
        _on_exit()


def _on_rebind_click():
    if _is_capturing:
        _cancel_capture()
        return
    if _on_rebind:
        threading.Thread(target=_on_rebind, daemon=True).start()


def _on_confirm_click():
    if _on_confirm:
        _on_confirm()


def _on_lang_click():
    if _on_lang:
        _on_lang()
        _refresh_lang()


def _cancel_capture():
    global _is_capturing
    _is_capturing = False
    if _on_cancel_capture:
        _on_cancel_capture()
    if _root:
        _root.after(0, lambda: (_confirm_btn.pack_forget(),
                                 _rebind_btn.config(text=t('change'), bg='#333'),
                                 _rebind_hint.config(text=''),
                                 _hotkey_label.config(fg=WHITE)))


def start_capture_mode():
    global _is_capturing
    _is_capturing = True
    _root.after(0, lambda: (_rebind_btn.config(text=t('cancel'), bg='#4a2020'),
                             _rebind_hint.config(text=t('press_keys')),
                             _hotkey_label.config(text='\u2026', fg=DIM)))


def show_captured_hotkey(hotkey: str):
    global _is_capturing
    _is_capturing = True
    _root.after(0, lambda: (_confirm_btn.pack(side='left', padx=(0, 4)),
                             _rebind_btn.config(text=t('cancel'), bg='#4a2020'),
                             _rebind_hint.config(text=t('click_confirm')),
                             _hotkey_label.config(text=hotkey, fg=WHITE)))


def finish_capture_mode(hotkey: str):
    global _is_capturing
    _is_capturing = False
    _root.after(0, lambda: (_confirm_btn.pack_forget(),
                             _rebind_btn.config(text=t('change'), bg='#333'),
                             _rebind_hint.config(text=''),
                             _hotkey_label.config(text=hotkey if hotkey else '', fg=WHITE)))


def _refresh_lang():
    if not _root:
        return
    def _do():
        _status_section_label.config(text=t('status'))
        _hotkey_section_label.config(text=t('hotkey_label'))
        _rebind_btn.config(text=t('change') if not _is_capturing else t('cancel'))
        _confirm_btn.config(text=t('confirm'))
        _lang_btn.config(text=t('lang_btn'))
        _made_by_label.config(text=f"{t('made_by')} pro72rus")
        if _internet_off:
            _status_label.config(text=t('disconnected'))
            _status_dot.config(fg=RED)
            _status_label.config(fg=RED)
        else:
            _status_label.config(text=t('connected'))
            _status_dot.config(fg=GREEN)
            _status_label.config(fg=GREEN)
    _root.after(0, _do)


# ─── main window ───────────────────────────────────────────────

def _loop():
    global _root, _title_bar, _status_label, _hotkey_label, _rebind_btn, _rebind_hint
    global _confirm_btn, _status_dot, _version_label, _made_by_label, _lang_btn
    global _hotkey_section_label, _status_section_label

    _root = tk.Tk()
    _root.title('NetSwitch')
    _root.configure(bg=BG)
    _root.resizable(False, False)
    _root.overrideredirect(True)
    _root.attributes('-topmost', True)

    ww, wh = 320, 230
    sw = _root.winfo_screenwidth()
    sh = _root.winfo_screenheight()
    x = (sw - ww) // 2
    y = sh // 4
    _root.geometry(f'{ww}x{wh}+{x}+{y}')

    _title_bar = tk.Frame(_root, bg=BAR, height=32)
    _title_bar.pack(fill='x')
    _title_bar.pack_propagate(False)

    tk.Label(_title_bar, text=' NetSwitch', font=('Segoe UI', 10, 'bold'),
             bg=BAR, fg=WHITE).pack(side='left', padx=(8, 0))

    close_btn = tk.Label(_title_bar, text=' \u2715 ', font=('Segoe UI', 10),
                         bg=BAR, fg=DIM, cursor='hand2')
    close_btn.pack(side='right')
    close_btn.bind('<Button-1>', lambda e: _on_close_click())
    close_btn.bind('<Enter>', lambda e: close_btn.config(fg=RED))
    close_btn.bind('<Leave>', lambda e: close_btn.config(fg=DIM))

    min_btn = tk.Label(_title_bar, text=' \u2500 ', font=('Segoe UI', 10),
                       bg=BAR, fg=DIM, cursor='hand2')
    min_btn.pack(side='right')
    min_btn.bind('<Button-1>', lambda e: _on_minimize_click())
    min_btn.bind('<Enter>', lambda e: min_btn.config(fg=WHITE))
    min_btn.bind('<Leave>', lambda e: min_btn.config(fg=DIM))

    _lang_btn = tk.Label(_title_bar, text=t('lang_btn'), font=('Segoe UI', 8, 'bold'),
                         bg=BAR, fg=DIM, cursor='hand2', padx=6)
    _lang_btn.pack(side='right')
    _lang_btn.bind('<Button-1>', lambda e: _on_lang_click())
    _lang_btn.bind('<Enter>', lambda e: _lang_btn.config(fg=WHITE))
    _lang_btn.bind('<Leave>', lambda e: _lang_btn.config(fg=DIM))

    content = tk.Frame(_root, bg=BG)
    content.pack(fill='both', expand=True, padx=14, pady=(10, 12))

    section_status = tk.Frame(content, bg=BG)
    section_status.pack(fill='x', pady=(0, 8))

    _status_section_label = tk.Label(section_status, text=t('status'), font=('Segoe UI', 8),
             bg=BG, fg=DIM, anchor='w')
    _status_section_label.pack(fill='x')

    status_row = tk.Frame(section_status, bg=BG)
    status_row.pack(fill='x', pady=(2, 0))

    _status_dot = tk.Label(status_row, text='\u25cf', font=('Segoe UI', 14),
                           bg=BG, fg=GREEN)
    _status_dot.pack(side='left', padx=(0, 6))

    _status_label = tk.Label(status_row, text=t('connected'), font=('Segoe UI', 11, 'bold'),
                             bg=BG, fg=GREEN, anchor='w')
    _status_label.pack(side='left')

    sep = tk.Frame(content, bg=ACCENT, height=1)
    sep.pack(fill='x', pady=(0, 8))

    section_hotkey = tk.Frame(content, bg=BG)
    section_hotkey.pack(fill='x', pady=(0, 8))

    _hotkey_section_label = tk.Label(section_hotkey, text=t('hotkey_label'), font=('Segoe UI', 8),
                                     bg=BG, fg=DIM, anchor='w')
    _hotkey_section_label.pack(fill='x')

    hotkey_row = tk.Frame(section_hotkey, bg=BG)
    hotkey_row.pack(fill='x', pady=(2, 0))

    _hotkey_label = tk.Label(hotkey_row, text='end', font=('Segoe UI', 11),
                             bg=BG, fg=WHITE, anchor='w')
    _hotkey_label.pack(side='left')

    _btn_frame = tk.Frame(hotkey_row, bg=BG)
    _btn_frame.pack(side='right')

    _confirm_btn = tk.Button(_btn_frame, text=t('confirm'), font=('Segoe UI', 8),
                             bg='#1a4a1a', fg='#8f8', activebackground='#2a5a2a',
                             activeforeground=WHITE, relief='flat', bd=0,
                             cursor='hand2', command=_on_confirm_click,
                             padx=8, pady=2)

    _rebind_btn = tk.Button(_btn_frame, text=t('change'), font=('Segoe UI', 8),
                            bg='#333', fg='#aaa', activebackground='#444',
                            activeforeground=WHITE, relief='flat', bd=0,
                            cursor='hand2', command=_on_rebind_click,
                            padx=10, pady=2)
    _rebind_btn.pack(side='right')

    _rebind_hint = tk.Label(section_hotkey, text='', font=('Segoe UI', 8),
                            bg=BG, fg=DIM, anchor='w')
    _rebind_hint.pack(fill='x', pady=(4, 0))

    dev_frame = tk.Frame(content, bg=BG)
    dev_frame.pack(fill='x', pady=(8, 0))
    _made_by_label = tk.Label(dev_frame, text=f"{t('made_by')} pro72rus",
                              font=('Segoe UI', 7, 'bold'), bg=BG, fg='#aaa')
    _made_by_label.pack(side='left')
    _version_label = tk.Label(dev_frame, text='', font=('Segoe UI', 7),
                              bg=BG, fg='#666')
    _version_label.pack(side='right')

    def start_move(e):
        _root._x = e.x
        _root._y = e.y

    def do_move(e):
        nx = _root.winfo_x() + e.x - _root._x
        ny = _root.winfo_y() + e.y - _root._y
        _root.geometry(f'+{nx}+{ny}')

    _title_bar.bind('<Button-1>', start_move)
    _title_bar.bind('<B1-Motion>', do_move)

    _root.protocol('WM_DELETE_WINDOW', _on_close_click)

    def _apply_toolwindow():
        try:
            hwnd = _user32.GetParent(_root.winfo_id())
            if not hwnd:
                hwnd = _root.winfo_id()
            style = _user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            _user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                                   style | WS_EX_TOPMOST | WS_EX_TOOLWINDOW)
        except Exception:
            pass

    _root.after(200, _apply_toolwindow)
    _root.after(100, lambda: _q_started.set())
    _root.mainloop()


def _ensure():
    if _root is None:
        _q_started.clear()
        th = threading.Thread(target=_loop, daemon=True)
        th.start()
        _q_started.wait(timeout=5)


def set_callbacks(on_rebind=None, on_cancel_capture=None, on_confirm=None,
                  on_exit=None, on_minimize=None, on_lang=None, on_mode=None):
    global _on_rebind, _on_cancel_capture, _on_confirm, _on_exit, _on_minimize, _on_lang
    _on_rebind = on_rebind
    _on_cancel_capture = on_cancel_capture
    _on_confirm = on_confirm
    _on_exit = on_exit
    _on_minimize = on_minimize
    _on_lang = on_lang


def show_window():
    _ensure()
    if _root:
        _root.after(0, lambda: (_root.deiconify(), _root.lift(), _root.focus_force()))


def hide_window():
    _ensure()
    if _root:
        _root.after(0, lambda: _root.withdraw())


def update_status(internet_off: bool):
    global _internet_off
    _internet_off = internet_off
    _ensure()
    if not _status_label or not _status_dot:
        return
    if internet_off:
        current = _status_dot.cget('fg')
        _status_label.config(text=t('disconnected'))
        _root.after(0, lambda: _animate_status(current, RED))
    else:
        current = _status_dot.cget('fg')
        _status_label.config(text=t('connected'))
        _root.after(0, lambda: _animate_status(current, GREEN))


def update_hotkey(hotkey: str):
    _ensure()
    if _hotkey_label:
        _root.after(0, lambda: _hotkey_label.config(text=hotkey, fg=WHITE))


def update_version(version: str):
    _ensure()
    if _version_label:
        _version_label.config(text=version)
        _root.update()


def update_mode(mode: str):
    pass


def get_root():
    _ensure()
    return _root
