"""
Notepad Pro
------------
The jam-packed tier: tabs, a modern formatting toolbar (headings, lists,
bold/italic/strikethrough, links, tables), recent files, autosave, syntax
highlighting with line numbers, and switchable themes.

Copyright 2026 Fritz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import re
import json
import webbrowser

APP_NAME = "Notepad Pro"
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".notepadpro_config.json")
AUTOSAVE_INTERVAL_MS = 30000

THEMES = {
    "Dark": dict(bg="#1e1e1e", fg="#d4d4d4", insert="#ffffff", select_bg="#264f78",
                 select_fg="#ffffff", linebg="#252526", linefg="#858585",
                 toolbar="#252526", btn="#2d2d2d", accent="#007acc"),
    "Light": dict(bg="#ffffff", fg="#1e1e1e", insert="#000000", select_bg="#add6ff",
                  select_fg="#000000", linebg="#f3f3f3", linefg="#8a8a8a",
                  toolbar="#f3f3f3", btn="#e8e8e8", accent="#005fb8"),
    "Solarized": dict(bg="#fdf6e3", fg="#657b83", insert="#657b83", select_bg="#eee8d5",
                       select_fg="#657b83", linebg="#eee8d5", linefg="#93a1a1",
                       toolbar="#eee8d5", btn="#e4ddc6", accent="#268bd2"),
}

KEYWORDS = (r"\b(def|class|return|import|from|as|if|elif|else|for|while|try|except|"
            r"finally|with|lambda|pass|break|continue|in|is|not|and|or|None|True|False|"
            r"function|var|let|const|new|this|public|private|static|void|int|float|"
            r"string|include|namespace|using)\b")
STRING_RE = r"(\".*?\"|'.*?')"
COMMENT_RE = r"(#.*$|//.*$)"
NUMBER_RE = r"\b\d+(\.\d+)?\b"


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as fh:
                return json.load(fh)
        except Exception:
            pass
    return {"recent": [], "theme": "Dark"}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as fh:
            json.dump(cfg, fh)
    except Exception:
        pass


class EditorTab(ttk.Frame):
    _link_counter = 0

    def __init__(self, master, app, path=None):
        super().__init__(master)
        self.app = app
        self.path = path
        self._highlight_job = None

        self.linenumbers = tk.Canvas(self, width=44, highlightthickness=0)
        self.linenumbers.pack(side="left", fill="y")

        yscroll = tk.Scrollbar(self)
        yscroll.pack(side="right", fill="y")

        self.text = tk.Text(self, wrap="word", undo=True, font=("Segoe UI", 11),
                             yscrollcommand=self._on_scroll, bd=0, padx=12, pady=10,
                             highlightthickness=0, spacing3=3)
        self.text.pack(side="left", fill="both", expand=True)
        yscroll.config(command=self._yview)

        self.text.tag_config("bold", font=("Segoe UI", 11, "bold"))
        self.text.tag_config("italic", font=("Segoe UI", 11, "italic"))
        self.text.tag_config("strike", font=("Segoe UI", 11, "overstrike"))
        self.text.tag_config("h1", font=("Segoe UI", 22, "bold"))
        self.text.tag_config("h2", font=("Segoe UI", 18, "bold"))
        self.text.tag_config("h3", font=("Segoe UI", 15, "bold"))

        self.text.bind("<KeyRelease>", self._on_key)
        self.text.bind("<Configure>", lambda e: self.update_linenumbers())

        self.update_linenumbers()
        if path:
            self.load_file(path)

    def _yview(self, *args):
        self.text.yview(*args)
        self.update_linenumbers()

    def _on_scroll(self, *args):
        self.app.root.after_idle(self.update_linenumbers)

    def update_linenumbers(self):
        self.linenumbers.delete("all")
        i = self.text.index("@0,0")
        th = self.app.theme()
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.linenumbers.create_text(4, y, anchor="nw", text=linenum,
                                          fill=th["linefg"], font=("Consolas", 9))
            i = self.text.index(f"{i}+1line")

    def _on_key(self, event=None):
        self.app.on_edit()
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(300, self.highlight)
        self.update_linenumbers()

    def is_modified(self):
        return self.text.edit_modified()

    def highlight(self):
        content = self.text.get("1.0", "end-1c")
        for tag in ("kw", "str", "cmt", "num"):
            self.text.tag_remove(tag, "1.0", "end")
        for m in re.finditer(KEYWORDS, content):
            self._tag_range("kw", m.start(), m.end())
        for m in re.finditer(STRING_RE, content):
            self._tag_range("str", m.start(), m.end())
        for m in re.finditer(COMMENT_RE, content, re.MULTILINE):
            self._tag_range("cmt", m.start(), m.end())
        for m in re.finditer(NUMBER_RE, content):
            self._tag_range("num", m.start(), m.end())

    def _tag_range(self, tag, start, end):
        self.text.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

    def apply_theme(self, th):
        self.text.config(bg=th["bg"], fg=th["fg"], insertbackground=th["insert"],
                          selectbackground=th["select_bg"], selectforeground=th["select_fg"])
        self.linenumbers.config(bg=th["linebg"])
        self.text.tag_config("kw", foreground="#c586c0")
        self.text.tag_config("str", foreground="#ce9178")
        self.text.tag_config("cmt", foreground="#6a9955")
        self.text.tag_config("num", foreground="#b5cea8")
        self.update_linenumbers()

    def load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not open file:\n{e}")
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.path = path
        self.text.edit_modified(False)
        self.highlight()
        self.update_linenumbers()

    def save(self, path=None):
        p = path or self.path
        if not p:
            return False
        try:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(self.text.get("1.0", "end-1c"))
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not save file:\n{e}")
            return False
        self.path = p
        self.text.edit_modified(False)
        return True

    def autosave(self):
        if self.path and self.is_modified():
            try:
                with open(self.path + ".bak", "w", encoding="utf-8") as fh:
                    fh.write(self.text.get("1.0", "end-1c"))
            except Exception:
                pass

    def display_name(self):
        base = os.path.basename(self.path) if self.path else "Untitled"
        return ("\u25cf " if self.is_modified() else "") + base

    # ---- formatting ----
    def _toggle_tag(self, tag):
        try:
            s, e = "sel.first", "sel.last"
            self.text.index(s)
        except tk.TclError:
            messagebox.showinfo(APP_NAME, "Select some text first.")
            return
        ranges = self.text.tag_ranges(tag)
        already = False
        for i in range(0, len(ranges), 2):
            if self.text.compare(ranges[i], "<=", s) and self.text.compare(ranges[i + 1], ">=", e):
                already = True
        if already:
            self.text.tag_remove(tag, s, e)
        else:
            self.text.tag_add(tag, s, e)

    def apply_heading(self, level):
        try:
            line_start = self.text.index("insert linestart")
            line_end = self.text.index("insert lineend")
        except tk.TclError:
            return
        for t in ("h1", "h2", "h3"):
            self.text.tag_remove(t, line_start, line_end)
        if level != "normal":
            self.text.tag_add(level, line_start, line_end)

    def toggle_bullet(self):
        try:
            start = int(self.text.index("sel.first").split(".")[0])
            end = int(self.text.index("sel.last").split(".")[0])
        except tk.TclError:
            start = end = int(self.text.index("insert").split(".")[0])
        for ln in range(start, end + 1):
            line_text = self.text.get(f"{ln}.0", f"{ln}.end")
            if line_text.startswith("\u2022 "):
                self.text.delete(f"{ln}.0", f"{ln}.2")
            else:
                self.text.insert(f"{ln}.0", "\u2022 ")

    def insert_link(self):
        try:
            s, e = self.text.index("sel.first"), self.text.index("sel.last")
            self.text.get(s, e)
        except tk.TclError:
            messagebox.showinfo(APP_NAME, "Select the text you want to turn into a link first.")
            return
        url = simpledialog.askstring(APP_NAME, "Link URL:")
        if not url:
            return
        EditorTab._link_counter += 1
        tag = f"link{EditorTab._link_counter}"
        self.text.tag_config(tag, foreground=self.app.theme()["accent"], underline=True)
        self.text.tag_add(tag, s, e)
        self.text.tag_bind(tag, "<Button-1>", lambda ev, u=url: webbrowser.open(u))
        self.text.tag_bind(tag, "<Enter>", lambda ev: self.text.config(cursor="hand2"))
        self.text.tag_bind(tag, "<Leave>", lambda ev: self.text.config(cursor=""))

    def insert_table(self):
        table = ("| Header | Header | Header |\n"
                 "| --- | --- | --- |\n"
                 "| Cell | Cell | Cell |\n"
                 "| Cell | Cell | Cell |\n")
        self.text.insert("insert", table)

    def clear_formatting(self):
        try:
            s, e = "sel.first", "sel.last"
            self.text.index(s)
        except tk.TclError:
            messagebox.showinfo(APP_NAME, "Select some text first.")
            return
        for t in ("bold", "italic", "strike", "h1", "h2", "h3"):
            self.text.tag_remove(t, s, e)


class NotepadPro:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1100x720")

        self.cfg = load_config()
        self.theme_name = self.cfg.get("theme", "Dark")
        self.zoom = 100

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self._style = style

        self.build_menu()
        self.build_toolbar()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.on_edit())

        self.status = tk.Label(root, text="Ln 1, Col 1", anchor="e", font=("Segoe UI", 9),
                                padx=10, pady=3)
        self.status.pack(fill="x", side="bottom")

        self.wrap_var = tk.BooleanVar(value=False)
        self.status_var = tk.BooleanVar(value=True)

        self.bind_shortcuts()
        self.new_tab()
        self.apply_theme(self.theme_name)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.after(AUTOSAVE_INTERVAL_MS, self.autosave_all)
        self.root.after(200, self.status_loop)

    # ---- theme ----
    def theme(self):
        return THEMES[self.theme_name]

    def apply_theme(self, name):
        self.theme_name = name
        self.cfg["theme"] = name
        save_config(self.cfg)
        th = THEMES[name]

        self.root.configure(bg=th["bg"])
        self._style.configure("TNotebook", background=th["bg"], borderwidth=0, tabmargins=[2, 4, 0, 0])
        self._style.configure("TNotebook.Tab", background=th["btn"], foreground=th["fg"],
                               padding=[14, 6], borderwidth=0, font=("Segoe UI", 9))
        self._style.map("TNotebook.Tab", background=[("selected", th["bg"])],
                         foreground=[("selected", th["fg"])])

        for tab_id in self.notebook.tabs():
            self.notebook.nametowidget(tab_id).apply_theme(th)

        self.toolbar.config(bg=th["toolbar"])
        for w in self.toolbar.winfo_children():
            w.config(bg=th["toolbar"])
            for c in w.winfo_children():
                try:
                    c.config(bg=th["toolbar"], fg=th["fg"],
                             activebackground=th["btn"], activeforeground=th["fg"])
                except tk.TclError:
                    pass
        self.status.config(bg=th["accent"], fg="#ffffff")

    # ---- chrome ----
    def _menu(self, parent):
        th = self.theme()
        return tk.Menu(parent, tearoff=0, bg=th["btn"], fg=th["fg"],
                        activebackground=th["accent"], activeforeground="white",
                        bd=0, relief="flat", font=("Segoe UI", 10))

    def build_menu(self):
        menubar = self._menu(self.root)

        file_menu = self._menu(menubar)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+N", command=lambda: self.new_tab())
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        self.recent_menu = self._menu(file_menu)
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_tab)
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = self._menu(menubar)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self._undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self._ev("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self._ev("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self._ev("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", accelerator="Ctrl+F", command=self.find_dialog)
        edit_menu.add_command(label="Replace...", accelerator="Ctrl+H", command=self.replace_dialog)
        edit_menu.add_command(label="Go To Line...", accelerator="Ctrl+G", command=self.goto_line)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = self._menu(menubar)
        view_menu.add_checkbutton(label="Word Wrap", variable=tk.BooleanVar(value=False), command=self.toggle_wrap)
        theme_menu = self._menu(view_menu)
        self.theme_var = tk.StringVar(value=self.theme_name)
        for name in THEMES:
            theme_menu.add_radiobutton(label=name, variable=self.theme_var, value=name,
                                        command=lambda n=name: self.apply_theme(n))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)
        self.rebuild_recent_menu()

    def _toolbtn(self, parent, text, command, width=3):
        th = self.theme()
        b = tk.Button(parent, text=text, command=command, bg=th["toolbar"], fg=th["fg"],
                      activebackground=th["btn"], activeforeground=th["fg"], bd=0,
                      relief="flat", font=("Segoe UI", 11), width=width, padx=4, pady=4,
                      cursor="hand2")
        b.pack(side="left", padx=2, pady=4)
        return b

    def build_toolbar(self):
        th = self.theme()
        self.toolbar = tk.Frame(self.root, bg=th["toolbar"], height=40)
        self.toolbar.pack(fill="x", side="top")

        left = tk.Frame(self.toolbar, bg=th["toolbar"])
        left.pack(side="left", padx=8)

        self.heading_var = tk.StringVar(value="Normal")
        heading_menu = tk.OptionMenu(left, self.heading_var, "Normal", "H1", "H2", "H3",
                                      command=lambda v: self._cur().apply_heading(
                                          {"Normal": "normal", "H1": "h1", "H2": "h2", "H3": "h3"}[v]))
        heading_menu.config(bg=th["toolbar"], fg=th["fg"], bd=0, relief="flat",
                             highlightthickness=0, font=("Segoe UI", 10), width=7)
        heading_menu.pack(side="left", padx=(0, 6), pady=4)

        self._toolbtn(left, "\u2261", lambda: self._cur().toggle_bullet())
        self._toolbtn(left, "B", lambda: self._cur()._toggle_tag("bold"))
        self._toolbtn(left, "I", lambda: self._cur()._toggle_tag("italic"))
        self._toolbtn(left, "S", lambda: self._cur()._toggle_tag("strike"))
        self._toolbtn(left, "\U0001f517", lambda: self._cur().insert_link())
        self._toolbtn(left, "\u25a6", lambda: self._cur().insert_table())
        self._toolbtn(left, "Aa\u2715", lambda: self._cur().clear_formatting(), width=4)

        right = tk.Frame(self.toolbar, bg=th["toolbar"])
        right.pack(side="right", padx=8)
        self._toolbtn(right, "\u2699", self.open_settings)
        self._toolbtn(right, "\U0001f464", self.show_about)
        self._toolbtn(right, "\U0001f4e4", self.save_file_as)
        self._toolbtn(right, "\u2728", lambda: messagebox.showinfo(
            APP_NAME, "AI features aren't available in this build."))

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_tab())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_file_as())
        self.root.bind("<Control-w>", lambda e: self.close_tab())
        self.root.bind("<Control-f>", lambda e: self.find_dialog())
        self.root.bind("<Control-h>", lambda e: self.replace_dialog())
        self.root.bind("<Control-g>", lambda e: self.goto_line())
        self.root.bind("<Control-a>", lambda e: self.select_all())

    # ---- tabs ----
    def _cur(self):
        sel = self.notebook.select()
        return self.notebook.nametowidget(sel) if sel else None

    def new_tab(self, path=None):
        tab = EditorTab(self.notebook, self, path)
        self.notebook.add(tab, text=tab.display_name())
        self.notebook.select(tab)
        tab.apply_theme(self.theme())
        self.on_edit()
        return tab

    def close_tab(self):
        tab = self._cur()
        if not tab:
            return
        if tab.is_modified():
            res = messagebox.askyesnocancel(APP_NAME, f"Save changes to {tab.display_name().lstrip(chr(0x25cf)+' ')}?")
            if res is None:
                return
            if res:
                self.save_file()
        self.notebook.forget(tab)
        if not self.notebook.tabs():
            self.new_tab()

    # ---- file ops ----
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        self.new_tab(path)
        self.add_recent(path)

    def save_file(self):
        tab = self._cur()
        if not tab:
            return
        if tab.path:
            if tab.save():
                self.on_edit()
        else:
            self.save_file_as()

    def save_file_as(self):
        tab = self._cur()
        if not tab:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        if tab.save(path):
            self.add_recent(path)
            self.on_edit()

    def add_recent(self, path):
        recent = self.cfg.setdefault("recent", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.cfg["recent"] = recent[:8]
        save_config(self.cfg)
        self.rebuild_recent_menu()

    def rebuild_recent_menu(self):
        self.recent_menu.delete(0, "end")
        recent = self.cfg.get("recent", [])
        if not recent:
            self.recent_menu.add_command(label="(empty)", state="disabled")
        for p in recent:
            self.recent_menu.add_command(label=os.path.basename(p), command=lambda p=p: self.new_tab(p))

    def autosave_all(self):
        for tab_id in self.notebook.tabs():
            self.notebook.nametowidget(tab_id).autosave()
        self.root.after(AUTOSAVE_INTERVAL_MS, self.autosave_all)

    # ---- edit helpers ----
    def _ev(self, name):
        tab = self._cur()
        if tab:
            tab.text.event_generate(name)

    def _undo(self):
        tab = self._cur()
        if tab:
            try:
                tab.text.edit_undo()
            except tk.TclError:
                pass

    def _redo(self):
        tab = self._cur()
        if tab:
            try:
                tab.text.edit_redo()
            except tk.TclError:
                pass

    def select_all(self):
        tab = self._cur()
        if tab:
            tab.text.tag_add("sel", "1.0", "end-1c")
        return "break"

    def find_dialog(self):
        tab = self._cur()
        if not tab:
            return
        term = simpledialog.askstring("Find", "Find what:")
        if not term:
            return
        tab.text.tag_remove("found", "1.0", "end")
        pos = tab.text.search(term, "1.0", stopindex="end")
        if pos:
            end = f"{pos}+{len(term)}c"
            tab.text.tag_add("found", pos, end)
            tab.text.tag_config("found", background="#515c6a", foreground="white")
            tab.text.see(pos)
        else:
            messagebox.showinfo(APP_NAME, f'Cannot find "{term}"')

    def replace_dialog(self):
        tab = self._cur()
        if not tab:
            return
        find = simpledialog.askstring("Replace", "Find:")
        if not find:
            return
        repl = simpledialog.askstring("Replace", "Replace with:") or ""
        content = tab.text.get("1.0", "end-1c")
        count = content.count(find)
        content = content.replace(find, repl)
        tab.text.delete("1.0", "end")
        tab.text.insert("1.0", content)
        tab.highlight()
        messagebox.showinfo(APP_NAME, f"Replaced {count} occurrence(s).")

    def goto_line(self):
        tab = self._cur()
        if not tab:
            return
        line = simpledialog.askinteger("Go To Line", "Line number:")
        if line:
            tab.text.mark_set("insert", f"{line}.0")
            tab.text.see(f"{line}.0")

    # ---- format ----
    def toggle_wrap(self):
        self.wrap_var.set(not self.wrap_var.get())
        wrap = "word" if self.wrap_var.get() else "none"
        for tab_id in self.notebook.tabs():
            self.notebook.nametowidget(tab_id).text.config(wrap=wrap)

    # ---- settings / about ----
    def open_settings(self):
        th = self.theme()
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=th["bg"])
        tk.Label(win, text="Theme:", bg=th["bg"], fg=th["fg"]).pack(anchor="w", padx=12, pady=(12, 0))
        for name in THEMES:
            tk.Radiobutton(win, text=name, variable=self.theme_var, value=name,
                           command=lambda n=name: self.apply_theme(n),
                           bg=th["bg"], fg=th["fg"], selectcolor=th["btn"],
                           activebackground=th["bg"], activeforeground=th["fg"]
                           ).pack(anchor="w", padx=20)
        tk.Checkbutton(win, text="Word Wrap", variable=self.wrap_var, command=self.toggle_wrap,
                       bg=th["bg"], fg=th["fg"], selectcolor=th["btn"],
                       activebackground=th["bg"], activeforeground=th["fg"]
                       ).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Button(win, text="Close", command=win.destroy, bg=th["accent"], fg="white",
                  relief="flat").pack(anchor="e", padx=12, pady=12)

    def show_about(self):
        messagebox.showinfo("About " + APP_NAME,
                             f"{APP_NAME}\nMade by Fritz\nApache License 2.0\n\n"
                             "Tabs, formatting toolbar, recent files, autosave, syntax "
                             "highlighting, and themes, built with Python & Tkinter.")

    # ---- status ----
    def on_edit(self):
        tab = self._cur()
        if tab:
            idx = self.notebook.index(tab)
            self.notebook.tab(idx, text=tab.display_name())
            self.root.title(f"{tab.display_name().lstrip(chr(0x25cf)+' ')} - {APP_NAME}")

    def status_loop(self):
        tab = self._cur()
        if tab and self.status_var.get():
            line, col = tab.text.index("insert").split(".")
            chars = len(tab.text.get("1.0", "end-1c"))
            self.status.config(text=f"Ln {line}, Col {int(col)+1}   |   {chars} characters   |   "
                                     f"{self.theme_name}   |   UTF-8")
        self.root.after(200, self.status_loop)

    def exit_app(self):
        for tab_id in list(self.notebook.tabs()):
            tab = self.notebook.nametowidget(tab_id)
            if tab.is_modified():
                self.notebook.select(tab)
                res = messagebox.askyesnocancel(APP_NAME, f"Save changes to {tab.display_name().lstrip(chr(0x25cf)+' ')}?")
                if res is None:
                    return
                if res:
                    self.save_file()
        save_config(self.cfg)
        self.root.destroy()


def main():
    root = tk.Tk()
    NotepadPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
