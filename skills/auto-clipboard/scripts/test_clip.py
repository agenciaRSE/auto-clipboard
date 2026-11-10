"""Self-check: python test_clip.py  (round trip needs a desktop session)."""
import os
import string
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clip  # noqa: E402

for n in (8, 24, 64):
    pw = clip.make_password(n)
    assert len(pw) == n
    assert set(pw) <= set(string.ascii_letters + string.digits + clip.SYMBOLS)
    assert any(c.islower() for c in pw) and any(c.isupper() for c in pw)
    assert any(c.isdigit() for c in pw) and any(c in clip.SYMBOLS for c in pw)
assert all(c.isalnum() for c in clip.make_password(32, symbols=False))
try:
    clip.make_password(4)
    raise AssertionError("short password accepted")
except ValueError:
    pass

assert clip.split_steps("a\n---8<---\n\nb c\n  ---8<---  \n\n---8<---\nd") == ["a", "b c", "d"]
assert clip.split_steps("solo") == ["solo"]

if sys.platform == "win32":
    sample = 'git commit -m "año ñ €"\nsecond line ✓'
    clip.copy(sample)
    got = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"],
                         capture_output=True).stdout.decode("utf-8").rstrip("\r\n")
    assert got.replace("\r\n", "\n") == sample, repr(got)

print("ok")
