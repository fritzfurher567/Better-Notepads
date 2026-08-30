# Better Notepads — by Fritz

A modern, tabbed text editor with a formatting toolbar, in three tiers.

| File | Tier | What it is |
|---|---|---|
| `Notepad-Lite.py` | Lite | Minimal and fast — the same modern look, core editing only |
| `Notepad-Standard.py` | Standard | Tabs, formatting toolbar (headings, lists, bold/italic/strikethrough, links, tables), find & replace, zoom, and more |
| `Notepad-Pro.py` | Pro | Standard + recent files, autosave, syntax highlighting with line numbers, and switchable themes (Dark/Light/Solarized) |

**License:** Apache License 2.0 for all three — see `LICENSE` in this repo, and the header comment in each file. Made by Fritz.

---

## One installer, pick your edition

Instead of three separate installers, this repo now builds **one setup
wizard** that lets the person installing it choose which edition(s) they
want, right there in the wizard:

- **Notepad Lite** — minimal and fast
- **Notepad Standard** — tabs, formatting toolbar, full features
- **Notepad Pro** — Standard + recent files, autosave, syntax highlighting, themes
- **Custom** — install more than one at once

The wizard also shows the Apache 2.0 license, lets you pick the install
folder, optionally adds a desktop shortcut, creates Start Menu entries per
edition installed, and registers a proper uninstaller.

**To get it:**
1. Push this repo to GitHub with the layout below.
2. Either:
   - Go to **Releases** → download `BetterNotepads-Setup.exe` directly from
     the latest release's Assets, **or**
   - Go to **Actions** → open the latest green run → **Artifacts** →
     download `notepad-installer` and unzip it
3. Double-click `BetterNotepads-Setup.exe`
4. If Windows shows **"Windows protected your PC"**, click **More info** →
   **Run anyway** (normal for unsigned/free software, not a sign of a problem)
5. Accept the license → pick your edition(s) → choose install folder →
   optional desktop shortcut → **Install** → **Finish**

Each installed app is roughly 10–20 MB (PyInstaller bundles a full Python +
Tkinter runtime into every `.exe`) — that's expected, not a bug.

---

## The interface

All three tiers share the same modern dark UI:
- A slim **toolbar** with heading styles (Normal/H1/H2/H3), bullet list,
  **B**old, *Italic*, ~~Strikethrough~~, link insertion, table insertion,
  and clear-formatting
- A **status bar** (bottom) showing cursor position, character count, and
  encoding
- Standard and Pro also have a **tab strip** for multiple open documents
- Top-right icons: ⚙ Settings, 👤 About, 📤 Export (Save As), and ✨ (a
  placeholder — AI features aren't implemented in this build, the icon is
  there for consistency with the reference design but currently just shows
  an informational message)

Formatting (bold, italic, headings, etc.) is applied live in the editor via
text tags — note that saving still writes plain `.txt`, so rich formatting
isn't preserved between sessions. Links are clickable and open in your
default browser. Tables insert a plain-text/Markdown-style grid you can
edit by hand.

---

## 1. `Notepad-Lite.py`

Same visual language as Standard/Pro (dark theme, tab-strip header,
toolbar row) but with the original lightweight feature set:

- Menus: File, Edit, Format
- File: New, Open, Save, Save As, Print (placeholder), Exit
- Edit: Undo, Cut, Copy, Paste, Find & Replace
- Format: Word Wrap, Font
- No tabs (single document), no recent files, no autosave

---

## 2. `Notepad-Standard.py`

- Tabs — open multiple documents, close with Ctrl+W
- Formatting toolbar — headings, bullet list, bold, italic, strikethrough,
  clickable links, table insertion, clear formatting
- Menus: File, Edit, View
- File: New Tab, Open, Save, Save As, Close Tab, Page Setup, Print, Exit
- Edit: Undo, Redo, Cut, Copy, Paste, Delete, Find, Replace, Go To Line,
  Select All
- View: Word Wrap, Font picker, Zoom In/Out/Reset, Status Bar toggle
- ⚙ Settings popup (Word Wrap + Font, quick access)
- 👤 About popup

---

## 3. `Notepad-Pro.py`

Everything in Standard, plus:

- **Recent Files** — File → Open Recent, remembers your last 8 files
  across restarts (`~/.notepadpro_config.json`)
- **Autosave** — every 30 seconds, modified tabs with a file path get
  backed up to `<filename>.bak`
- **Syntax highlighting + line numbers** — keywords, strings, comments,
  and numbers are colored for common languages; a line-number gutter
  scrolls with the text
- **Themes** — Dark (default), Light, and Solarized, switchable from the
  ⚙ Settings popup or View → Theme; remembered across restarts

---

## Running from source

```
python Notepad-Lite.py
python Notepad-Standard.py
python Notepad-Pro.py
```
Requires Python 3 — tkinter comes bundled with the standard Windows/Mac
installer. On Linux: `sudo apt install python3-tk`

---

## Repo layout

```
Notepad-Lite.py
Notepad-Standard.py
Notepad-Pro.py
LICENSE                          (Apache 2.0 — shown in the installer wizard)
installer/
  Setup.iss                      (Inno Setup script — one installer, pick your edition)
.github/workflows/build-exe.yml  (builds all three exes + the unified installer)
```

---

## Notes

- All three apps save/open plain `.txt` files.
- Pro remembers theme + recent files via its config file; Lite and
  Standard reset those on each launch, kept simple on purpose.
- The installer registers a proper uninstaller in Windows — remove
  installed editions later from Settings → Apps, or the Start Menu.
