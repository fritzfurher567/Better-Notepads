"""
Notepad Lite
-------------
A minimal, fast text editor with a modern dark UI, built with Python/Tkinter.

Copyright 2026 Fritz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
"""

import tkinter as tk
from tkinter import filedialog as fd, messagebox as mb, simpledialog as sd

APP_NAME = "Notepad Lite"
BG = "#1e1e1e"
FG = "#d4d4d4"
TOOLBAR_BG = "#252526"
BTN_BG = "#2d2d2d"
BTN_HOVER = "#3c3c3c"
ACCENT = "#007acc"
TAB_BG = "#2d2d2d"

file_path = None


def new_file():
    global file_path
    if not confirm_discard():
        return
    text.delete("1.0", tk.END)
    file_path = None
    set_title("Untitled")
    text.edit_modified(False)


def open_file():
    global file_path
    if not confirm_discard():
        return
    path = fd.askopenfilename()
    if not path:
        return
    file_path = path
    text.delete("1.0", tk.END)
    text.insert("1.0", open(path, encoding="utf-8", errors="replace").read())
    set_title(path.split("/")[-1])
    text.edit_modified(False)


def write_to(path):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.get("1.0", "end-1c"))
    text.edit_modified(False)


def save_file():
    if file_path:
        write_to(file_path)
    else:
        save_file_as()


def save_file_as():
    global file_path
    path = fd.asksaveasfilename(defaultextension=".txt")
    if path:
        file_path = path
        write_to(path)
        set_title(path.split("/")[-1])


def confirm_discard():
    if not text.edit_modified():
        return True
    answer = mb.askyesnocancel(APP_NAME, "Save changes?")
    if answer is None:
        return False
    if answer:
        save_file()
    return True


def find_replace():
    find = sd.askstring("Find", "Find:")
    repl = sd.askstring("Replace", "Replace with:")
    if find:
        content = text.get("1.0", "end-1c").replace(find, repl or "")
        text.delete("1.0", tk.END)
        text.insert("1.0", content)


def choose_font():
    name = sd.askstring("Font", "Font name:")
    if name:
        text.config(font=(name, 11))


def toggle_wrap():
    text.config(wrap="word" if wrap_var.get() else "none")


def exit_app():
    if confirm_discard():
        root.destroy()


def set_title(name):
    root.title(f"{name} - {APP_NAME}")
    tab_label.config(text=("\u25cf " if text.edit_modified() else "") + name)


def on_edit(event=None):
    title = root.title()
    name = title.replace(f" - {APP_NAME}", "").lstrip("*")
    tab_label.config(text=("\u25cf " if text.edit_modified() else "") + name)


root = tk.Tk()
root.title(f"Untitled - {APP_NAME}")
root.geometry("800x600")
root.configure(bg=BG)

# ---- menu ----
menubar = tk.Menu(root, tearoff=0, bg=BTN_BG, fg="#cccccc",
                   activebackground=ACCENT, activeforeground="white", bd=0)


def make_menu():
    return tk.Menu(menubar, tearoff=0, bg=BTN_BG, fg="#cccccc",
                    activebackground=ACCENT, activeforeground="white", bd=0)


file_menu = make_menu()
for label, cmd in [("New", new_file), ("Open...", open_file), ("Save", save_file),
                    ("Save As...", save_file_as), ("Print...", lambda: mb.showinfo(APP_NAME, "No printer configured.")),
                    ("Exit", exit_app)]:
    file_menu.add_command(label=label, command=cmd)
menubar.add_cascade(label="File", menu=file_menu)

edit_menu = make_menu()
edit_menu.add_command(label="Undo", command=lambda: text.edit_undo())
edit_menu.add_command(label="Cut", command=lambda: text.event_generate("<<Cut>>"))
edit_menu.add_command(label="Copy", command=lambda: text.event_generate("<<Copy>>"))
edit_menu.add_command(label="Paste", command=lambda: text.event_generate("<<Paste>>"))
edit_menu.add_command(label="Find & Replace...", command=find_replace)
menubar.add_cascade(label="Edit", menu=edit_menu)

format_menu = make_menu()
wrap_var = tk.BooleanVar(value=True)
format_menu.add_checkbutton(label="Word Wrap", variable=wrap_var, command=toggle_wrap)
format_menu.add_command(label="Font...", command=choose_font)
menubar.add_cascade(label="Format", menu=format_menu)

root.config(menu=menubar)

# ---- tab strip (single, visual only) ----
tabstrip = tk.Frame(root, bg=TAB_BG, height=32)
tabstrip.pack(fill="x", side="top")
tab_label = tk.Label(tabstrip, text="Untitled", bg=BG, fg="#ffffff",
                      font=("Segoe UI", 9), padx=14, pady=6)
tab_label.pack(side="left", padx=(6, 0), pady=4)

# ---- toolbar ----
toolbar = tk.Frame(root, bg=TOOLBAR_BG, height=36)
toolbar.pack(fill="x", side="top")


def toolbtn(parent, text_, command):
    b = tk.Button(parent, text=text_, command=command, bg=TOOLBAR_BG, fg="#e0e0e0",
                  activebackground=BTN_HOVER, activeforeground="white", bd=0,
                  relief="flat", font=("Segoe UI", 10), padx=10, pady=5, cursor="hand2")
    b.pack(side="left", padx=2, pady=3)
    return b


toolbtn(toolbar, "New", new_file)
toolbtn(toolbar, "Open", open_file)
toolbtn(toolbar, "Save", save_file)
toolbtn(toolbar, "Find", find_replace)

# ---- text area ----
text = tk.Text(root, undo=True, wrap="word", font=("Segoe UI", 11),
               bg=BG, fg=FG, insertbackground=FG,
               selectbackground="#264f78", selectforeground="white",
               relief="flat", highlightthickness=0, padx=16, pady=12)
text.pack(fill="both", expand=True)
text.bind("<<Modified>>", on_edit)

# ---- status bar ----
status = tk.Label(root, text="Ln 1, Col 1", anchor="e", bg=ACCENT, fg="white",
                   font=("Segoe UI", 9), padx=10, pady=3)
status.pack(fill="x", side="bottom")


def update_status(event=None):
    line, col = text.index(tk.INSERT).split(".")
    status.config(text=f"Ln {line}, Col {int(col) + 1}")


text.bind("<KeyRelease>", update_status)
text.bind("<ButtonRelease>", update_status)

root.bind("<Control-n>", lambda e: new_file())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-h>", lambda e: find_replace())
root.protocol("WM_DELETE_WINDOW", exit_app)

root.mainloop()
