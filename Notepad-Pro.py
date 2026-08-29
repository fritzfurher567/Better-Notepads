"""
Notepad Pro
------------
The jam-packed tier: everything in the Extended edition, plus multi-document
tabs, a recent-files list, autosave, syntax highlighting with line numbers,
and switchable themes.

MIT License
Copyright (c) 2026 Fritz
Made by Fritz
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font as tkfont
import os
import re
import json

APP_NAME = "Notepad Pro"
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".notepadpro_config.json")
AUTOSAVE_INTERVAL_MS = 30000

THEMES = {
    "Light": dict(bg="#ffffff", fg="#000000", insert="#000000", select_bg="#3399ff",
                  select_fg="#ffffff", linebg="#f0f0f0", linefg="#888888", menubg="#f0f0f0"),
    "Dark": dict(bg="#1e1e1e", fg="#d4d4d4", insert="#ffffff", select_bg="#264f78",
                 select_fg="#ffffff", linebg="#252526", linefg="#858585", menubg="#2d2d2d"),
    "Solarized": dict(bg="#fdf6e3", fg="#657b83", insert="#657b83", select_bg="#eee8d5",
                       select_fg="#657b83", linebg="#eee8d5", linefg="#93a1a1", menubg="#eee8d5"),
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
    return {"recent": [], "theme": "Light"}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as fh:
            json.dump(cfg, fh)
    except Exception:
        pass


class EditorTab(ttk.Frame):
    def __init__(self, master, app, path=None):
        super().__init__(master)
        self.app = app
        self.path = path
        self._highlight_job = None

        self.linenumbers = tk.Canvas(self, width=44, highlightthickness=0)
        self.linenumbers.pack(side="left", fill="y")

        yscroll = tk.Scrollbar(self)
        yscroll.pack(side="right", fill="y")

        self.text = tk.Text(self, wrap="none", undo=True, font=("Consolas", 11),
                             yscrollcommand=self._on_scroll, bd=0, padx=4)
        self.text.pack(side="left", fill="both", expand=True)
        yscroll.config(command=self._yview)

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
        self.app.update_title()
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
        return ("*" if self.is_modified() else "") + base


class NotepadPro:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1000x700")

        self.cfg = load_config()
        self.theme_name = self.cfg.get("theme", "Light")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_title())

        self.status = tk.Label(root, text="Ln 1, Col 1", anchor="e", bd=1, relief="sunken")
        self.status.pack(fill="x", side="bottom")

        self.build_menu()
        self.bind_shortcuts()
        self.new_tab()
        self.apply_theme(self.theme_name)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.after(AUTOSAVE_INTERVAL_MS, self.autosave_all)
        self.root.after(200, self.update_status_loop)

    # ---- tabs ----
    def current_tab(self):
        sel = self.notebook.select()
        return self.notebook.nametowidget(sel) if sel else None

    def new_tab(self, path=None):
        tab = EditorTab(self.notebook, self, path)
        self.notebook.add(tab, text=tab.display_name())
        self.notebook.select(tab)
        tab.apply_theme(self.theme())
        self.update_title()
        return tab

    def close_tab(self, tab=None):
        tab = tab or self.current_tab()
        if not tab:
            return
        if tab.is_modified():
            res = messagebox.askyesnocancel(APP_NAME, f"Save changes to {tab.display_name().lstrip('*')}?")
            if res is None:
                return
            if res:
                self.save_file(tab)
        self.notebook.forget(tab)
        if not self.notebook.tabs():
            self.new_tab()
        self.update_title()

    # ---- file ops ----
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        self.new_tab(path)
        self.add_recent(path)

    def save_file(self, tab=None):
        tab = tab or self.current_tab()
        if not tab:
            return
        if tab.path:
            if tab.save():
                self.update_title()
        else:
            self.save_file_as(tab)

    def save_file_as(self, tab=None):
        tab = tab or self.current_tab()
        if not tab:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        if tab.save(path):
            idx = self.notebook.index(tab)
            self.notebook.tab(idx, text=tab.display_name())
            self.add_recent(path)
            self.update_title()

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

    # ---- menu ----
    def build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+N", command=lambda: self.new_tab())
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=lambda: self.save_file())
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=lambda: self.save_file_as())
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=lambda: self.close_tab())
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
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

        format_menu = tk.Menu(menubar, tearoff=0)
        self.wrap_var = tk.BooleanVar(value=False)
        format_menu.add_checkbutton(label="Word Wrap", variable=self.wrap_var, command=self.toggle_wrap)
        format_menu.add_command(label="Font...", command=self.choose_font)
        menubar.add_cascade(label="Format", menu=format_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        self.theme_var = tk.StringVar(value=self.theme_name)
        for name in THEMES:
            theme_menu.add_radiobutton(label=name, variable=self.theme_var, value=name,
                                        command=lambda n=name: self.apply_theme(n))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)
        self.rebuild_recent_menu()

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

    # ---- edit helpers ----
    def _ev(self, name):
        tab = self.current_tab()
        if tab:
            tab.text.event_generate(name)

    def _undo(self):
        tab = self.current_tab()
        if tab:
            try:
                tab.text.edit_undo()
            except tk.TclError:
                pass

    def _redo(self):
        tab = self.current_tab()
        if tab:
            try:
                tab.text.edit_redo()
            except tk.TclError:
                pass

    def select_all(self):
        tab = self.current_tab()
        if tab:
            tab.text.tag_add("sel", "1.0", "end-1c")
        return "break"

    def find_dialog(self):
        tab = self.current_tab()
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
            tab.text.tag_config("found", background="#3399ff", foreground="white")
            tab.text.see(pos)
        else:
            messagebox.showinfo(APP_NAME, f'Cannot find "{term}"')

    def replace_dialog(self):
        tab = self.current_tab()
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
        tab = self.current_tab()
        if not tab:
            return
        line = simpledialog.askinteger("Go To Line", "Line number:")
        if line:
            tab.text.mark_set("insert", f"{line}.0")
            tab.text.see(f"{line}.0")

    # ---- format ----
    def toggle_wrap(self):
        wrap = "word" if self.wrap_var.get() else "none"
        for tab_id in self.notebook.tabs():
            self.notebook.nametowidget(tab_id).text.config(wrap=wrap)

    def choose_font(self):
        win = tk.Toplevel(self.root)
        win.title("Font")
        families = ["Consolas", "Arial", "Courier New", "Segoe UI", "Times New Roman"]
        tab = self.current_tab()
        cur = tkfont.Font(font=tab.text["font"]) if tab else tkfont.Font(family="Consolas", size=11)
        fam_var = tk.StringVar(value=cur.actual("family"))
        size_var = tk.IntVar(value=cur.actual("size"))
        tk.Label(win, text="Font:").grid(row=0, column=0, padx=5, pady=5)
        tk.OptionMenu(win, fam_var, *families).grid(row=0, column=1)
        tk.Label(win, text="Size:").grid(row=1, column=0, padx=5, pady=5)
        tk.Spinbox(win, from_=8, to=48, textvariable=size_var, width=5).grid(row=1, column=1)

        def apply_font():
            for tab_id in self.notebook.tabs():
                self.notebook.nametowidget(tab_id).text.config(font=(fam_var.get(), size_var.get()))
            win.destroy()

        tk.Button(win, text="OK", command=apply_font).grid(row=2, column=0, columnspan=2, pady=8)

    # ---- theme ----
    def theme(self):
        return THEMES[self.theme_name]

    def apply_theme(self, name):
        self.theme_name = name
        self.cfg["theme"] = name
        save_config(self.cfg)
        th = THEMES[name]
        for tab_id in self.notebook.tabs():
            self.notebook.nametowidget(tab_id).apply_theme(th)
        self.status.config(bg=th["menubg"], fg=th["fg"])

    # ---- misc ----
    def update_title(self):
        tab = self.current_tab()
        if tab:
            idx = self.notebook.index(tab)
            self.notebook.tab(idx, text=tab.display_name())
            self.root.title(f"{tab.display_name()} - {APP_NAME}")

    def update_status_loop(self):
        tab = self.current_tab()
        if tab:
            line, col = tab.text.index("insert").split(".")
            self.status.config(text=f"Ln {line}, Col {int(col)+1}  |  {self.theme_name}")
        self.root.after(200, self.update_status_loop)

    def show_about(self):
        messagebox.showinfo("About " + APP_NAME,
                             f"{APP_NAME}\nMade by Fritz\nMIT License\n\n"
                             "Tabs, recent files, autosave, syntax highlighting, "
                             "line numbers, and theming, built on Python & Tkinter.")

    def exit_app(self):
        for tab_id in list(self.notebook.tabs()):
            tab = self.notebook.nametowidget(tab_id)
            if tab.is_modified():
                self.notebook.select(tab)
                res = messagebox.askyesnocancel(APP_NAME, f"Save changes to {tab.display_name().lstrip('*')}?")
                if res is None:
                    return
                if res:
                    self.save_file(tab)
        save_config(self.cfg)
        self.root.destroy()


def main():
    root = tk.Tk()
    NotepadPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
