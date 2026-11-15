#!/usr/bin/env python3
"""Stop hook: do not let Claude end a turn that claims a copy it never made, or that hands over a `!` command
without copying it.

Reads the hook input (JSON on stdin), walks the transcript back to the user's last real message, and checks the
assistant's text and tool calls since then. Blocks once with a reason; on the retry (stop_hook_active) it lets the
turn end, so it can never loop.
"""
import json
import re
import sys

CLAIM = re.compile(r"copiad[oa]s? al portapapeles|copied to (the |your )?clipboard|on (the|your) clipboard", re.I)
# A fenced block whose first line is a `!` command for the Claude Code prompt.
BANG_BLOCK = re.compile(r"```[^\n]*\n\s*!\s*\S", re.M)
COPY_TOOL = re.compile(r"clip\.py|Set-Clipboard|\bpbcopy\b|\bwl-copy\b|\bxclip\b|\bxsel\b")


def blocks(entry):
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def is_real_user(entry):
    if entry.get("type") != "user" or entry.get("isSidechain") or entry.get("isMeta"):
        return False
    return any(b.get("type") == "text" for b in blocks(entry))


def turn(lines):
    """Assistant text and tool-call inputs since the user's last real message."""
    entries = []
    for line in lines:
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    start = max((i for i, e in enumerate(entries) if is_real_user(e)), default=-1)
    text, calls = [], []
    for e in entries[start + 1:]:
        if e.get("type") != "assistant" or e.get("isSidechain"):
            continue
        for b in blocks(e):
            if b.get("type") == "text":
                text.append(b.get("text", ""))
            elif b.get("type") == "tool_use":
                calls.append(json.dumps(b.get("input", {}), ensure_ascii=False))
    return "\n".join(text), calls


def verdict(text, calls):
    copied = any(COPY_TOOL.search(c) for c in calls)
    if copied:
        return None
    if CLAIM.search(text):
        return ("You wrote that something was copied to the clipboard, but no copy command ran in this turn "
                "(clip.py, Set-Clipboard, pbcopy...). Copy it now with the auto-clipboard skill, or remove the "
                "claim and say it was not copied.")
    if BANG_BLOCK.search(text):
        return ("Your reply gives the user a `!` command to paste into the prompt but nothing was copied. Copy it "
                "with the auto-clipboard skill (clip.py) before ending the turn, then confirm the copy.")
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if data.get("stop_hook_active"):
        return
    try:
        with open(data.get("transcript_path", ""), encoding="utf-8") as f:
            text, calls = turn(f)
    except OSError:
        return
    reason = verdict(text, calls)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
