# Notepad — by Fritz

Three tiers of a Windows Notepad clone, built with Python/Tkinter.

| File | Size | Tier | What it is |
|---|---|---|---|
| `Notepad-Lite.py` | ~1.85 KB* | Lite | Full menu set, file ops, edit ops, font/wrap, unsaved-changes warning |
| `Notepad-Standard.py` | ~16 KB | Standard | Every classic Windows Notepad feature |
| `Notepad-Pro.py` | ~19 KB | Pro | Standard + tabs, recent files, autosave, syntax highlighting, themes |

**License:** Apache License 2.0 for all three — see `LICENSE` in this repo, and the header comment in each file. Made by Fritz.

*\*Lite is built to be as small as possible. Apache 2.0's required header text is long enough that it may push this file above the original 1.90 KB target — check the file size on your end if that budget matters to you.*

---

## Getting a real installer (setup wizard)

These `.py` files aren't runnable on their own — they need to be compiled.
This repo's GitHub Actions workflow (`.github/workflows/build-exe.yml`) does
that automatically and produces an actual **setup wizard** for each tier,
not just a bare `.exe`:

1. It compiles each `.py` file into a standalone `.exe` with PyInstaller.
2. It then wraps that `.exe` with **Inno Setup** (a standard Windows
   installer builder, pre-installed on GitHub's Windows runners) using the
   `.iss` scripts in the `installer/` folder.
3. The result is a proper installer — `NotepadLite-Setup.exe`,
   `NotepadStandard-Setup.exe`, `NotepadPro-Setup.exe` — that walks the
   person installing it through:
   - A license agreement page (showing the Apache 2.0 text from `LICENSE`)
   - A "choose install folder" page (defaults to Program Files)
   - An option to add a desktop shortcut
   - Installing files + creating Start Menu shortcuts
   - A "Launch now" checkbox on the finish page
   - A proper uninstaller registered in Windows (shows up in
     Settings → Apps, not just a leftover file)

**To get the installers, pick whichever applies:**

**If a version has been released** (someone ran `git tag v1.0.0` and pushed it):
1. Go to your repo's **Releases** tab (right sidebar on the repo homepage, or `github.com/yourname/yourrepo/releases`)
2. Click the latest release
3. Under **Assets**, click to download whichever file you want directly: `NotepadLite-Setup.exe`, `NotepadStandard-Setup.exe`, or `NotepadPro-Setup.exe`
4. Done — no zip, no extra folders. Double-click the one you downloaded to install it.

**If no release exists yet** (only plain pushes to `main` so far):
1. Go to the **Actions** tab
2. Click the most recent run with a green checkmark
3. Scroll down to **Artifacts** → click `notepad-installers` to download a `.zip`
4. Unzip it — inside are the same three `.exe` files
5. Double-click whichever one you want to install

---

## 1. `Notepad-Lite.py` — the compact core

Every line earns its place — this is heavily condensed Python (short names,
packed statements) to stay as small as possible while still shipping a real
menu bar. It's not meant to be pretty to read; `Notepad-Standard.py` is the
readable version.

**Includes:**
- Full menu set: File, Edit, Format, View, Help
- File: New, Open, Save, Save As
- Edit: Cut, Copy, Paste, Undo, Find & Replace (combined dialog)
- Format: Font selection, Word Wrap toggle
- Print menu entry (stub — see note below)
- Unsaved-changes warning before New / Open / Exit
- Keyboard shortcuts: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+H
- No network calls, no telemetry, no AI calls — opens instantly

**Note on Print:** actually sending to a printer needs an OS-level print
driver, which can't fit (or make sense) in a small script. The Print menu
item is wired up but shows a placeholder — the *infrastructure* (menu item,
handler function) is there for you to hook a real print call into later.

---

## 2. `Notepad-Standard.py` — the full clone

Same look and feel, but with (almost) everything the real Windows Notepad has.

**Includes:**
- File: New, New Window, Open, Save, Save As, Page Setup, Print, Exit
- Edit: Undo, Redo, Cut, Copy, Paste, Delete, Find, Find Next, Replace, Go To, Select All, Time/Date (F5)
- Format: Word Wrap toggle, Font picker
- View: Zoom In/Out/Reset, Status Bar toggle
- Help: About
- Full keyboard shortcuts matching real Notepad (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+F, F3, Ctrl+H, Ctrl+G, F5, Ctrl+= / Ctrl+- for zoom, etc.)

**Not included:** actual printer output (Print shows a placeholder dialog — hooking up a real printer driver is OS-specific and outside what a single script can do), spell check, encoding-format selection.

---

## 3. `Notepad-Pro.py` — jam-packed

Everything in Standard, plus:

- **Multi-document tabs** — open several files at once, `Ctrl+W` closes the
  current tab (with a save prompt if it has unsaved changes)
- **Recent Files** — File → Open Recent remembers your last 8 files across
  restarts (saved to `~/.notepadpro_config.json`)
- **Autosave** — every 30 seconds, any modified tab with a file path gets
  backed up to `<filename>.bak` (your real file is only touched when you
  explicitly Save — this is a safety-net copy, not silent overwriting)
- **Syntax highlighting + line numbers** — a lightweight highlighter
  (keywords, strings, comments, numbers) covers common languages like
  Python, JS, and C-style code, with a line-number gutter that scrolls
  with the text
- **Themes** — Light, Dark, and Solarized, switchable from View → Theme;
  your choice is remembered for next time
- Everything from Standard: Find, Replace, Go To Line, Undo/Redo,
  Cut/Copy/Paste, Font picker, Word Wrap, unsaved-changes warnings

Requires `ttk` (bundled with standard Tkinter — no extra installs).

---

## Running from source (without an installer)

If you just want to run a tier directly with Python instead of installing
the compiled version:
```
python Notepad-Lite.py
python Notepad-Standard.py
python Notepad-Pro.py
```
Requires Python 3 — tkinter comes bundled with the standard Windows/Mac
installer. On Linux, if tkinter isn't already installed:
`sudo apt install python3-tk`

---

## Repo layout

```
Notepad-Lite.py
Notepad-Standard.py
Notepad-Pro.py
LICENSE                          (Apache 2.0 — shown in the installer wizard)
installer/
  Lite.iss                       (Inno Setup script for Lite)
  Standard.iss                   (Inno Setup script for Standard)
  Pro.iss                        (Inno Setup script for Pro)
.github/workflows/build-exe.yml  (builds + packages all three installers)
```

---

## Notes

- All three apps save/open plain `.txt` files, same as real Notepad.
- Settings (zoom, word wrap, font) reset each time you reopen Lite or
  Standard — there's no saved preferences file for those two, kept simple
  on purpose. Pro remembers theme and recent files via its config file.
- Each installer registers a proper uninstaller in Windows — the app can
  be removed later from Settings → Apps, or via the Start Menu shortcut.
