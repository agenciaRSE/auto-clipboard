---
name: auto-clipboard
description: Copies to the user's clipboard, without asking, anything Claude hands over to be pasted or used somewhere else - commands to run, code snippets, emails, messages, texts for a website, file paths, URLs, generated passwords, API keys, config blocks, SQL queries. Use it every time a reply contains a piece the user will paste into a terminal, another app, a form or a message, and whenever the user asks to copy something, says "cópialo", "pásamelo al portapapeles", "copy that", or asks for a password. Generates passwords locally so they never appear in the chat. Not for code Claude already wrote into files.
---

# Auto clipboard

The terminal wraps long lines with real line breaks and indentation, and chat copy buttons are easy to miss. Copying a piece by hand breaks commands, emails and texts. So whenever you hand the user something to paste, put it on their clipboard yourself.

## When to copy

Copy, without asking, whenever the reply gives the user something to take somewhere else:

- a command to run, or a `!` command for the Claude Code prompt
- code to paste into a file, console, admin panel or another app
- an email, message, post, or text for a website or a form
- a path, URL, identifier, config block, SQL query, regex
- a password, token or key you generate (see Secrets)

Do not copy:

- illustrative examples the user is not meant to run
- code you already wrote into files with your own tools
- long output the user only reads (logs, reports, explanations)

Several pieces in one reply: copy the one the user will use first and say which. Copy the others when asked.

## How to copy

Copy the exact text, ready to paste:

- no Markdown fences, no added indentation, no `$ ` or `>` prompt
- keep a leading `!` when the text is for the Claude Code prompt
- straight ASCII quotes and dashes in commands and code (`"` `'` `--`), never typographic ones
- no trailing newline, so a pasted command does not run before the user reviews it

Then still show the text in the reply, and add one line in the user's language, for example `📋 Copied to clipboard` or `📋 Copiado al portapapeles`.

Use the first method that your tools allow:

1. **Script** (any OS with Python 3). Pass the text on stdin with a quoted heredoc, so the shell expands nothing. Pick a delimiter that does not appear in the text:

   ```bash
   python "<this skill's directory>/scripts/clip.py" <<'CLIP_END'
   exact text here
   CLIP_END
   ```

   Use `python3` or `py` when `python` is not found. For a long text, write it to a temporary file and run `clip.py <file>`.

2. **PowerShell tool on Windows** (no Python needed). Use a single-quoted here-string; the closing `'@` must be at column 0:

   ```powershell
   Set-Clipboard -Value @'
   exact text here
   '@
   ```

   Never pipe text into `clip.exe` or into Python from PowerShell 5.1: the console code page breaks accents such as á and ñ.

3. **Native tool** from a shell: `pbcopy` on macOS, `wl-copy` on Wayland, `xclip -selection clipboard` on X11. Feed it with a quoted heredoc.

If copying fails, say so in one line with the error, and keep the text in its own code block so the user can copy it by hand.

## Secrets

**Generated passwords never go through the chat.** Generate them on the user's machine:

```bash
python "<this skill's directory>/scripts/clip.py" --password            # 24 characters
python "<this skill's directory>/scripts/clip.py" --password -n 32 --no-symbols
```

The script copies the password, never prints it, and on Windows keeps it out of clipboard history (Win+V) and cloud clipboard sync. Tell the user it is on the clipboard and that it is not shown. Do not read the clipboard back afterwards.

Symbols used: `! # % + - . : = ? @ _ ~`. Use `--no-symbols` when the target site rejects symbols, and `-n` for the length it requires.

For an existing secret the user gives you (an API key, a token), copy it with `--sensitive` so it also stays out of clipboard history.

Without Python, generate it in PowerShell and copy it in the same command, without printing it:

```powershell
$c = [char[]]'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!#%+-.:=?@_~'; $b = [byte[]]::new(24); [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); Set-Clipboard -Value (-join ($b | ForEach-Object { $c[$_ % $c.Length] }))
```

This fallback does not exclude the password from clipboard history. Say so.

## When there is no clipboard

Claude Desktop and claude.ai chats run skills in a cloud sandbox. It has no access to the user's clipboard, so copying there is impossible. In that case:

- put each paste-ready piece alone in its own code block, with nothing else inside, so the block's copy button gives exactly that text
- do not claim you copied anything
- do not generate passwords in the chat; give the user the PowerShell or `clip.py --password` command to run on their machine instead

In Claude Desktop's Code tab, Claude Code runs on the user's machine, so the methods above work.
