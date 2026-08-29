# Notepad — by Fritz

Two versions of a Windows Notepad clone, built with Python/Tkinter.

| File | Size | What it is |
|---|---|---|
| `notepad.py` | 1.85 KB | Core app — full menu set, file ops, edit ops, font/wrap, unsaved-changes warning |
| `notepad_extended.py` | ~16 KB | Full version — every classic Notepad feature, Apache License 2.0 licensed |

---

## 1. `notepad.py` — the compact core (under 1.90 KB)

Every line earns its place — this is heavily condensed Python (short names,
packed statements) to hit the size target while still shipping a real menu
bar. It's not meant to be pretty to read; `notepad_extended.py` is the
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
driver, which can't fit (or make sense) in a 2 KB script. The Print menu
item is wired up but shows a placeholder — the *infrastructure* (menu item,
handler function) is there for you to hook a real print call into later.

**Run it:**
```
python notepad.py
```

---

## 2. `notepad_extended.py` — the full clone

Same look and feel, but with (almost) everything the real Windows Notepad has.

**Includes:**
- File: New, New Window, Open, Save, Save As, Page Setup, Print, Exit
- Edit: Undo, Redo, Cut, Copy, Paste, Delete, Find, Find Next, Replace, Go To, Select All, Time/Date (F5)
- Format: Word Wrap toggle, Font picker
- View: Zoom In/Out/Reset, Status Bar toggle
- Help: About
- Full keyboard shortcuts matching real Notepad (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+F, F3, Ctrl+H, Ctrl+G, F5, Ctrl+= / Ctrl+- for zoom, etc.)

**Not included:** actual printer output (Print shows a placeholder dialog — hooking up a real printer driver is OS-specific and outside what a single script can do), spell check, encoding-format selection.

**License:** Apache License 2.0 — see the header comment in the file. Made by Fritz.

**Run it:**
```
python notepad_extended.py
```

---

## Requirements

- Python 3 (tkinter comes bundled with the standard Windows/Mac installer — no extra installs needed on those platforms)
- On Linux, if tkinter isn't already installed: `sudo apt install python3-tk`

---

## Turning either one into a Windows .exe

This has to be done **on a Windows machine** — an `.exe` can only be built on Windows.

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
2. From the folder with the script:
   ```
   pyinstaller --onefile --windowed --name Notepad notepad_extended.py
   ```
3. Find your finished app at:
   ```
   dist\Notepad.exe
   ```
   That one file runs standalone — no Python required on the target machine.

Add `--icon=youricon.ico` to the command if you want a custom icon.

---

## Notes

- Both apps save/open plain `.txt` files, same as real Notepad.
- Settings (zoom, word wrap, font) reset each time you reopen the app — there's no saved preferences file, kept simple on purpose.
