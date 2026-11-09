# 📋 Auto Clipboard

**A skill for Claude Code and Claude Desktop: Claude copies to your clipboard whatever it gives you to paste.**

Commands to run, code snippets, emails, messages, texts for a website, paths, URLs, config blocks, SQL queries. Claude shows the text and puts it on your clipboard at the same time. Generated passwords are created on your machine and never appear in the chat.

[English](#why) · [Español](#-en-español)

## Why

The Claude Code terminal wraps long lines with real line breaks and indentation. Copy a long command by hand and it breaks: a stray newline runs half of it, an indent splits a flag, an accent turns into `Ã±`. Emails and texts pasted from the terminal come out with broken lines too.

Auto Clipboard fixes it at the source: you never copy from the terminal again.

## What it does

- **Copies without asking** whenever a reply hands you something to paste somewhere else, and adds one line: `📋 Copied to clipboard`.
- **Copies the exact text**: no Markdown fences, no indentation, no `$ ` prompts, no typographic quotes in commands, no trailing newline that would run a command the moment you paste it.
- **Generates passwords locally**: `clip.py --password` creates the password with Python's `secrets`, copies it, and never prints it. The password never passes through the model or the chat history.
- **Keeps secrets out of clipboard history**: on Windows, passwords and keys copied with `--sensitive` stay out of the Win+V history and cloud clipboard sync.
- **Keeps accents and emoji intact** on Windows, where `clip.exe` and PowerShell pipes break them.
- **Skips what you don't need**: illustrative examples, code already written to files, long logs.

## Install

### Claude Code

As a plugin:

```text
/plugin marketplace add agenciaRSE/auto-clipboard
/plugin install auto-clipboard@auto-clipboard
```

Or copy `skills/auto-clipboard` into `~/.claude/skills/`.

For the skill to apply on every reply, add one line to your `~/.claude/CLAUDE.md`:

```text
Whenever you give me something to paste elsewhere, use the auto-clipboard skill to copy it.
```

### Claude Desktop

Download `auto-clipboard.zip` from the [latest release](https://github.com/agenciaRSE/auto-clipboard/releases/latest) and upload it in **Settings → Capabilities → Skills**.

Chats in Claude Desktop and claude.ai run skills in a cloud sandbox with no access to your clipboard. There, the skill puts each paste-ready piece alone in its own code block, so the copy button gives you exactly that text, and it gives you a command to generate passwords on your own machine. In Claude Desktop's **Code** tab, Claude Code runs locally and the clipboard works fully.

## Requirements

- **Windows**: Python 3 is recommended. Without it, Claude uses PowerShell's `Set-Clipboard`.
- **macOS**: Python 3 or nothing at all (`pbcopy`).
- **Linux**: Python 3 and `wl-clipboard` (Wayland), `xclip` or `xsel` (X11).
- **WSL**: Python 3; it uses `clip.exe`. Secrets copied from WSL still show up in Win+V history.

`clip.py` uses the standard library only. No network, no files written.

## The script

```text
python clip.py [FILE]                  copy FILE or stdin
python clip.py --sensitive [FILE]      same, kept out of clipboard history
python clip.py --password [-n 24] [--no-symbols]
```

Run `python skills/auto-clipboard/scripts/test_clip.py` to check it. On Windows it also does a real clipboard round trip with accents and emoji.

## Replaces AI Terminal Code Cleaner

This skill replaces [AI Terminal Code Cleaner](https://github.com/agenciaRSE/ai-terminal-code-cleaner), a desktop app that cleaned AI snippets after you copied them. Auto Clipboard avoids the mess before it happens.

## 🇪🇸 En español

**Una skill para Claude Code y Claude Desktop: Claude copia en tu portapapeles todo lo que te da para pegar.**

Comandos, fragmentos de código, emails, mensajes, textos para la web, rutas, URLs, bloques de configuración o consultas SQL. Claude muestra el texto y lo deja en el portapapeles a la vez. Las contraseñas se generan en tu equipo y nunca aparecen en el chat.

**Por qué.** La terminal de Claude Code parte las líneas largas con saltos y sangría reales. Al copiar a mano, un comando largo se rompe y los acentos de un email salen como `Ã±`. Con Auto Clipboard ya no copias nada desde la terminal.

**Qué hace:**

- Copia sin preguntar cada vez que te da algo para pegar en otro sitio, y lo avisa con una línea: `📋 Copiado al portapapeles`.
- Copia el texto exacto: sin bloques de Markdown, sin sangría, sin comillas tipográficas en los comandos y sin salto final que ejecute el comando al pegarlo.
- Genera las contraseñas en local: no pasan por el modelo ni quedan en la conversación.
- En Windows, las contraseñas y claves no quedan en el historial del portapapeles (Win+V) ni se sincronizan en la nube.
- Respeta acentos, ñ y emoji en Windows.

**Instalación en Claude Code:** `/plugin marketplace add agenciaRSE/auto-clipboard` y después `/plugin install auto-clipboard@auto-clipboard`. También puedes copiar `skills/auto-clipboard` en `~/.claude/skills/`.

**Instalación en Claude Desktop:** descarga `auto-clipboard.zip` de la [última versión](https://github.com/agenciaRSE/auto-clipboard/releases/latest) y súbelo en **Ajustes → Capacidades → Skills**. En los chats de Claude Desktop y claude.ai la skill se ejecuta en la nube, sin acceso a tu portapapeles. Ahí pone cada texto en su propio bloque de código, con su botón de copiar. En la pestaña **Code** de Claude Desktop funciona completa.

**Sustituye a AI Terminal Code Cleaner**, la app que limpiaba los snippets después de copiarlos. Auto Clipboard evita el problema antes de que ocurra.

Hecho por [AGENCIA RSE](https://agenciarse.com). Licencia MIT.
