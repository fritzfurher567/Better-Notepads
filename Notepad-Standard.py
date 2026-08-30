"""
Notepad Standard
-----------------
A modern tabbed text editor with a formatting toolbar (headings, lists,
bold/italic/strikethrough, links, tables), built with Python/Tkinter.

Copyright 2026 Fritz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font as tkfont
import os
import webbrowser

APP_NAME = "Notepad Standard"

BG = "#1e1e1e"
FG = "#d4d4d4"
TOOLBAR_BG = "#252526"
BTN_BG = "#2d2d2d"
BTN_HOVER = "#3c3c3c"
ACCENT = "#007acc"
SELECT_BG = "#264f78"
LINK_FG = "#3794ff"
TAB_BG = "#2d2d2d"
TAB_ACTIVE = "#1e1e1e"


class EditorTab(ttk.Frame):
    _link_counter = 0

    def __init__(self, master, app, path=None):
        super().__init__(master)
        self.app = app
        self.path = path

        self.text = tk.Text(self, wrap="word", undo=True, font=("Segoe UI", 11),
                             bg=BG, fg=FG, insertbackground=FG,
                             selectbackground=SELECT_BG, selectforeground="#ffffff",
                             relief="flat", highlightthickness=0, padx=16, pady=12,
                             spacing3=4)
        yscroll = tk.Scrollbar(self, command=self.text.yview, bg=TOOLBAR_BG,
                                troughcolor=BG, bd=0, activebackground=BTN_HOVER)
        self.text.config(yscrollcommand=yscroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        self.text.tag_config("bold", font=("Segoe UI", 11, "bold"))
        self.text.tag_config("italic", font=("Segoe UI", 11, "italic"))
        self.text.tag_config("strike", font=("Segoe UI", 11, "overstrike"))
        self.text.tag_config("h1", font=("Segoe UI", 22, "bold"))
        self.text.tag_config("h2", font=("Segoe UI", 18, "bold"))
        self.text.tag_config("h3", font=("Segoe UI", 15, "bold"))

        self.text.bind("<KeyRelease>", lambda e: self.app.on_edit())
        self.text.bind("<ButtonRelease>", lambda e: self.app.on_edit())

        if path:
            self.load_file(path)

    def is_modified(self):
        return self.text.edit_modified()

    def display_name(self):
        base = os.path.basename(self.path) if self.path else "Untitled"
        return ("\u25cf " if self.is_modified() else "") + base

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
        self.text.tag_config(tag, foreground=LINK_FG, underline=True)
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


class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Untitled - {APP_NAME}")
        self.root.geometry("1000x680")
        self.root.configure(bg=BG)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=[2, 4, 0, 0])
        style.configure("TNotebook.Tab", background=TAB_BG, foreground="#cccccc",
                         padding=[14, 6], borderwidth=0, font=("Segoe UI", 9))
        style.map("TNotebook.Tab", background=[("selected", TAB_ACTIVE)],
                  foreground=[("selected", "#ffffff")])

        self.build_menu()
        self.build_toolbar()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.on_edit())

        self.status = tk.Label(root, text="Ln 1, Col 1", anchor="e", bg=ACCENT, fg="white",
                                font=("Segoe UI", 9), padx=10, pady=3)
        self.status.pack(fill="x", side="bottom")

        self.word_wrap = tk.BooleanVar(value=True)
        self.status_bar_on = tk.BooleanVar(value=True)
        self.zoom = 100

        self.bind_shortcuts()
        self.new_tab()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.after(200, self.status_loop)

    # ---- chrome ----
    def _menu(self, parent):
        return tk.Menu(parent, tearoff=0, bg=BTN_BG, fg="#cccccc",
                        activebackground=ACCENT, activeforeground="white",
                        bd=0, relief="flat", font=("Segoe UI", 10))

    def build_menu(self):
        menubar = self._menu(self.root)

        file_menu = self._menu(menubar)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+N", command=lambda: self.new_tab())
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_tab)
        file_menu.add_command(label="Page Setup...", command=lambda: messagebox.showinfo(
            "Page Setup", "Margins: 0.75\" all sides\nPaper: Letter\nOrientation: Portrait"))
        file_menu.add_command(label="Print...", accelerator="Ctrl+P", command=lambda: messagebox.showinfo(
            APP_NAME, "Printing needs an OS-level print driver, not available in this build."))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = self._menu(menubar)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self._undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self._ev("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self._ev("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self._ev("<<Paste>>"))
        edit_menu.add_command(label="Delete", accelerator="Del", command=self._delete_sel)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", accelerator="Ctrl+F", command=self.find_dialog)
        edit_menu.add_command(label="Replace...", accelerator="Ctrl+H", command=self.replace_dialog)
        edit_menu.add_command(label="Go To Line...", accelerator="Ctrl+G", command=self.goto_line)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = self._menu(menubar)
        self.wrap_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Word Wrap", variable=self.wrap_var, command=self.toggle_wrap)
        view_menu.add_command(label="Font...", command=self.choose_font)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", accelerator="Ctrl+=", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", accelerator="Ctrl+-", command=self.zoom_out)
        view_menu.add_command(label="Restore Default Zoom", accelerator="Ctrl+0", command=self.zoom_reset)
        self.status_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Status Bar", variable=self.status_var, command=self.toggle_status_bar)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

    def _toolbtn(self, parent, text, command, width=3):
        b = tk.Button(parent, text=text, command=command, bg=TOOLBAR_BG, fg="#e0e0e0",
                      activebackground=BTN_HOVER, activeforeground="white", bd=0,
                      relief="flat", font=("Segoe UI", 11), width=width, padx=4, pady=4,
                      cursor="hand2")
        b.pack(side="left", padx=2, pady=4)
        return b

    def build_toolbar(self):
        bar = tk.Frame(self.root, bg=TOOLBAR_BG, height=40)
        bar.pack(fill="x", side="top")

        left = tk.Frame(bar, bg=TOOLBAR_BG)
        left.pack(side="left", padx=8)

        self.heading_var = tk.StringVar(value="Normal")
        heading_menu = tk.OptionMenu(left, self.heading_var, "Normal", "H1", "H2", "H3",
                                      command=lambda v: self._cur().apply_heading(
                                          {"Normal": "normal", "H1": "h1", "H2": "h2", "H3": "h3"}[v]))
        heading_menu.config(bg=TOOLBAR_BG, fg="#e0e0e0", bd=0, relief="flat",
                             highlightthickness=0, font=("Segoe UI", 10), width=7)
        heading_menu.pack(side="left", padx=(0, 6), pady=4)

        self._toolbtn(left, "\u2261", lambda: self._cur().toggle_bullet())
        self._toolbtn(left, "B", lambda: self._cur()._toggle_tag("bold"))
        self._toolbtn(left, "I", lambda: self._cur()._toggle_tag("italic"))
        self._toolbtn(left, "S", lambda: self._cur()._toggle_tag("strike"))
        self._toolbtn(left, "\U0001f517", lambda: self._cur().insert_link())
        self._toolbtn(left, "\u25a6", lambda: self._cur().insert_table())
        self._toolbtn(left, "Aa\u2715", lambda: self._cur().clear_formatting(), width=4)

        right = tk.Frame(bar, bg=TOOLBAR_BG)
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
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_reset())

    # ---- tabs ----
    def _cur(self):
        sel = self.notebook.select()
        return self.notebook.nametowidget(sel) if sel else None

    def new_tab(self, path=None):
        tab = EditorTab(self.notebook, self, path)
        self.notebook.add(tab, text=tab.display_name())
        self.notebook.select(tab)
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

    def confirm_discard_all(self):
        for tab_id in list(self.notebook.tabs()):
            tab = self.notebook.nametowidget(tab_id)
            if tab.is_modified():
                self.notebook.select(tab)
                res = messagebox.askyesnocancel(APP_NAME, f"Save changes to {tab.display_name().lstrip(chr(0x25cf)+' ')}?")
                if res is None:
                    return False
                if res:
                    self.save_file()
        return True

    # ---- file ops ----
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if path:
            self.new_tab(path)

    def save_file(self):
        tab = self._cur()
        if not tab:
            return
        if tab.path:
            tab.save()
            self.on_edit()
        else:
            self.save_file_as()

    def save_file_as(self):
        tab = self._cur()
        if not tab:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if path and tab.save(path):
            self.on_edit()

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

    def _delete_sel(self):
        tab = self._cur()
        if tab:
            try:
                tab.text.delete("sel.first", "sel.last")
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
        wrap = "word" if self.wrap_var.get() else "none"
        for tab_id in self.notebook.tabs():
            self.notebook.nametowidget(tab_id).text.config(wrap=wrap)

    def choose_font(self):
        win = tk.Toplevel(self.root)
        win.title("Font")
        win.configure(bg=BG)
        families = ["Segoe UI", "Consolas", "Arial", "Courier New", "Times New Roman"]
        tab = self._cur()
        cur = tkfont.Font(font=tab.text["font"]) if tab else tkfont.Font(family="Segoe UI", size=11)
        fam_var = tk.StringVar(value=cur.actual("family"))
        size_var = tk.IntVar(value=cur.actual("size"))
        tk.Label(win, text="Font:", bg=BG, fg=FG).grid(row=0, column=0, padx=5, pady=5)
        tk.OptionMenu(win, fam_var, *families).grid(row=0, column=1)
        tk.Label(win, text="Size:", bg=BG, fg=FG).grid(row=1, column=0, padx=5, pady=5)
        tk.Spinbox(win, from_=8, to=72, textvariable=size_var, width=5,
                   bg=BTN_BG, fg=FG, relief="flat").grid(row=1, column=1)

        def apply_font():
            for tab_id in self.notebook.tabs():
                self.notebook.nametowidget(tab_id).text.config(font=(fam_var.get(), size_var.get()))
            win.destroy()

        tk.Button(win, text="OK", command=apply_font, bg=ACCENT, fg="white",
                  relief="flat").grid(row=2, column=0, columnspan=2, pady=8)

    def zoom_in(self):
        self.zoom = min(500, self.zoom + 10)
        self._apply_zoom()

    def zoom_out(self):
        self.zoom = max(10, self.zoom - 10)
        self._apply_zoom()

    def zoom_reset(self):
        self.zoom = 100
        self._apply_zoom()

    def _apply_zoom(self):
        size = max(1, int(11 * self.zoom / 100))
        for tab_id in self.notebook.tabs():
            t = self.notebook.nametowidget(tab_id).text
            cur = tkfont.Font(font=t["font"])
            t.config(font=(cur.actual("family"), size))

    def toggle_status_bar(self):
        if self.status_var.get():
            self.status.pack(fill="x", side="bottom")
        else:
            self.status.pack_forget()

    # ---- settings / about ----
    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=BG)
        tk.Checkbutton(win, text="Word Wrap", variable=self.wrap_var, command=self.toggle_wrap,
                       bg=BG, fg=FG, selectcolor=BTN_BG, activebackground=BG,
                       activeforeground=FG).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Button(win, text="Choose Font...", command=self.choose_font, bg=BTN_BG, fg=FG,
                  relief="flat").pack(anchor="w", padx=12, pady=4)
        tk.Button(win, text="Close", command=win.destroy, bg=ACCENT, fg="white",
                  relief="flat").pack(anchor="e", padx=12, pady=12)

    def show_about(self):
        messagebox.showinfo("About " + APP_NAME,
                             f"{APP_NAME}\nMade by Fritz\nApache License 2.0\n\n"
                             "Tabs, formatting toolbar, find & replace, and more, "
                             "built with Python & Tkinter.")

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
            self.status.config(text=f"Ln {line}, Col {int(col)+1}   |   {chars} characters   |   {self.zoom}%   |   UTF-8")
        self.root.after(200, self.status_loop)

    def exit_app(self):
        if self.confirm_discard_all():
            self.root.destroy()


def main():
    root = tk.Tk()
    Notepad(root)
    root.mainloop()


if __name__ == "__main__":
    main()
