#!/usr/bin/env python3
"""Copy text to the system clipboard, or generate a password straight into it.

Standard library only. Windows, macOS, Linux (Wayland/X11) and WSL.

  python clip.py [FILE]                 copy FILE, or stdin, as UTF-8 text
  python clip.py --sensitive [FILE]     same, kept out of clipboard history and cloud sync
  python clip.py --steps [FILE]         several pieces separated by a line "---8<---":
                                        step 1 ends on the clipboard and, on Windows,
                                        the rest follow it in order in Win+V history
  python clip.py --password [-n 24] [--no-symbols]
                                        generate a password, copy it as sensitive,
                                        never print it
"""
import argparse
import os
import secrets
import shutil
import string
import subprocess
import sys
import time

SYMBOLS = "!#%+-.:=?@_~"  # shell-safe in quotes and accepted by most password rules
STEP_SEPARATOR = "---8<---"
HISTORY_GAP = 0.7  # seconds between copies so Win+V history keeps each one as its own entry


def split_steps(text):
    """Pieces separated by a line that is exactly STEP_SEPARATOR, empty pieces dropped."""
    steps, cur = [], []
    for line in text.split("\n"):
        if line.strip() == STEP_SEPARATOR:
            steps.append("\n".join(cur).strip("\n"))
            cur = []
        else:
            cur.append(line)
    steps.append("\n".join(cur).strip("\n"))
    return [st for st in steps if st.strip()]


def make_password(length=24, symbols=True):
    if length < 8:
        raise ValueError("length must be at least 8")
    classes = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        classes.append(SYMBOLS)
    alphabet = "".join(classes)
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(c in cls for c in pw) for cls in classes):
            return pw


def _copy_windows(text, sensitive):
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.restype = wintypes.BOOL
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
    user32.RegisterClipboardFormatW.restype = wintypes.UINT
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]

    def put(fmt, data):
        h = kernel32.GlobalAlloc(0x0002, len(data))  # GMEM_MOVEABLE
        if not h:
            raise OSError("GlobalAlloc failed")
        ptr = kernel32.GlobalLock(h)
        ctypes.memmove(ptr, data, len(data))
        kernel32.GlobalUnlock(h)
        if not user32.SetClipboardData(fmt, h):
            kernel32.GlobalFree(h)  # on success the clipboard owns h
            raise OSError("SetClipboardData failed")

    for _ in range(20):  # another app may hold the clipboard for a moment
        if user32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        raise OSError("clipboard is busy")
    try:
        user32.EmptyClipboard()
        put(13, text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-16-le") + b"\0\0")  # CF_UNICODETEXT
        if sensitive:
            zero = (0).to_bytes(4, "little")
            for name in ("ExcludeClipboardContentFromMonitorProcessing",
                         "CanIncludeInClipboardHistory", "CanUploadToCloudClipboard"):
                put(user32.RegisterClipboardFormatW(name), zero)
    finally:
        user32.CloseClipboard()


def _is_wsl():
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def _copy_command(text):
    """Return (command, input bytes) for the non-Windows clipboard tool."""
    if sys.platform == "darwin":
        return ["pbcopy"], text.encode("utf-8")
    if _is_wsl() and shutil.which("clip.exe"):
        # shortcut: clip.exe has no history/cloud opt-out, so --sensitive still lands in Win+V history on WSL
        return ["clip.exe"], b"\xff\xfe" + text.replace("\n", "\r\n").encode("utf-16-le")
    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
        return ["wl-copy"], text.encode("utf-8")
    if shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard"], text.encode("utf-8")
    if shutil.which("xsel"):
        return ["xsel", "--clipboard", "--input"], text.encode("utf-8")
    raise OSError("no clipboard tool found: install wl-clipboard, xclip or xsel")


def copy(text, sensitive=False):
    if sys.platform == "win32":
        _copy_windows(text, sensitive)
        return
    cmd, data = _copy_command(text)
    env = dict(os.environ, LANG=os.environ.get("LANG") or "en_US.UTF-8")
    subprocess.run(cmd, input=data, check=True, env=env)


def main(argv=None):
    p = argparse.ArgumentParser(description="Copy text to the clipboard.")
    p.add_argument("file", nargs="?", help="file to copy (default: stdin)")
    p.add_argument("--sensitive", action="store_true", help="keep out of clipboard history and cloud sync")
    p.add_argument("--steps", action="store_true", help=f"copy pieces separated by a '{STEP_SEPARATOR}' line, step 1 last")
    p.add_argument("--password", action="store_true", help="generate a password and copy it, never print it")
    p.add_argument("-n", "--length", type=int, default=24, help="password length (default 24)")
    p.add_argument("--no-symbols", action="store_true", help="password with letters and digits only")
    a = p.parse_args(argv)

    if a.password:
        copy(make_password(a.length, not a.no_symbols), sensitive=True)
        print(f"Copied a {a.length}-character password. Not shown; kept out of clipboard history.")
        return 0

    if a.file:
        with open(a.file, "rb") as f:
            raw = f.read()
    else:
        raw = sys.stdin.buffer.read()  # bytes: the console code page would mangle accents
    text = raw.decode("utf-8-sig").rstrip("\r\n")  # a trailing newline would run a pasted command at once
    if not text:
        print("Nothing to copy: input is empty.", file=sys.stderr)
        return 1
    if a.steps:
        steps = split_steps(text)
        # Last copied = current clipboard and top of Win+V, so copy in reverse: step 1 ends on top.
        for i, st in enumerate(reversed(steps)):
            if i:
                time.sleep(HISTORY_GAP)
            copy(st, a.sensitive)
        where = "the others follow it in Win+V history" if sys.platform == "win32" else "only step 1 is kept (no clipboard history)"
        print(f"Copied {len(steps)} steps: step 1 is on the clipboard, {where}.")
        return 0
    copy(text, a.sensitive)
    print(f"Copied {len(text)} characters" + (" (kept out of clipboard history)." if a.sensitive else "."))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as e:
        print(f"Could not copy: {e}", file=sys.stderr)
        sys.exit(2)
