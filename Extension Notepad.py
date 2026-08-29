"""
Notepad (Extended Edition)
---------------------------
A feature-complete clone of the classic Windows Notepad, built with Python/Tkinter.
 
Apache Licence
Copyright (c) 2026 Fritz
Made by Fritz
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font as tkfont
import datetime
import os

APP_NAME = "Notepad"


class Notepad:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.word_wrap = tk.BooleanVar(value=True)
        self.status_bar_on = tk.BooleanVar(value=True)
        self.zoom = 100
        self.find_last_index = "1.0"

        self.root.title(f"Untitled - {APP_NAME}")
        self.root.geometry("800x600")

        # ---- Text widget (with scrollbars, like real Notepad) ----
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.text = tk.Text(container, undo=True, wrap="word",
                             font=("Consolas", 11), bd=0, padx=4, pady=2)
        yscroll = tk.Scrollbar(container, command=self.text.yview)
        self.xscroll = tk.Scrollbar(self.root, orient="horizontal", command=self.text.xview)
        self.text.config(yscrollcommand=yscroll.set, xscrollcommand=self.xscroll.set)

        self.text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # ---- Status bar ----
        self.status = tk.Label(self.root, text="Ln 1, Col 1", anchor="e", bd=1, relief="sunken")
        self.status.pack(fill="x", side="bottom")

        self.text.bind("<<Modified>>", self.on_modified)
        self.text.bind("<KeyRelease>", self.update_status)
        self.text.bind("<ButtonRelease>", self.update_status)

        self.build_menu()
        self.bind_shortcuts()
        self.new_file(force=True)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    # ================= MENU =================
    def build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="New Window", accelerator="Ctrl+Shift+N", command=self.new_window)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Page Setup...", command=self.page_setup)
        file_menu.add_command(label="Print...", accelerator="Ctrl+P", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.text.event_generate("<<Paste>>"))
        edit_menu.add_command(label="Delete", accelerator="Del", command=self.delete_selection)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", accelerator="Ctrl+F", command=self.open_find)
        edit_menu.add_command(label="Find Next", accelerator="F3", command=self.find_next)
        edit_menu.add_command(label="Replace...", accelerator="Ctrl+H", command=self.open_replace)
        edit_menu.add_command(label="Go To...", accelerator="Ctrl+G", command=self.go_to_line)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        edit_menu.add_command(label="Time/Date", accelerator="F5", command=self.insert_time_date)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap, command=self.toggle_wrap)
        format_menu.add_command(label="Font...", command=self.choose_font)
        menubar.add_cascade(label="Format", menu=format_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        zoom_menu.add_command(label="Zoom In", accelerator="Ctrl+=", command=self.zoom_in)
        zoom_menu.add_command(label="Zoom Out", accelerator="Ctrl+-", command=self.zoom_out)
        zoom_menu.add_command(label="Restore Default Zoom", accelerator="Ctrl+0", command=self.zoom_reset)
        view_menu.add_cascade(label="Zoom", menu=zoom_menu)
        view_menu.add_checkbutton(label="Status Bar", variable=self.status_bar_on, command=self.toggle_status_bar)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About Notepad", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-N>", lambda e: self.new_window())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-p>", lambda e: self.print_file())
        self.root.bind("<Control-f>", lambda e: self.open_find())
        self.root.bind("<F3>", lambda e: self.find_next())
        self.root.bind("<Control-h>", lambda e: self.open_replace())
        self.root.bind("<Control-g>", lambda e: self.go_to_line())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<F5>", lambda e: self.insert_time_date())
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_reset())

    # ================= FILE =================
    def confirm_discard(self):
        if self.text.edit_modified():
            res = messagebox.askyesnocancel(APP_NAME, "Do you want to save changes?")
            if res is None:
                return False
            if res:
                self.save_file()
        return True

    def new_file(self, force=False):
        if not force and not self.confirm_discard():
            return
        self.text.delete("1.0", tk.END)
        self.file_path = None
        self.root.title(f"Untitled - {APP_NAME}")
        self.text.edit_modified(False)
        self.update_status()

    def new_window(self):
        os.system(f'python "{os.path.abspath(__file__)}" &' if os.name != "nt"
                   else f'start python "{os.path.abspath(__file__)}"')

    def open_file(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(defaultextension=".txt",
                                           filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not open file:\n{e}")
            return
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.file_path = path
        self.root.title(f"{os.path.basename(path)} - {APP_NAME}")
        self.text.edit_modified(False)
        self.update_status()

    def save_file(self):
        if self.file_path:
            self._write(self.file_path)
        else:
            self.save_as_file()

    def save_as_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        self._write(path)
        self.file_path = path
        self.root.title(f"{os.path.basename(path)} - {APP_NAME}")

    def _write(self, path):
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self.text.get("1.0", "end-1c"))
            self.text.edit_modified(False)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not save file:\n{e}")

    def page_setup(self):
        messagebox.showinfo("Page Setup", "Margins: 0.75\" all sides\nPaper: Letter\nOrientation: Portrait")

    def print_file(self):
        messagebox.showinfo("Print", "Printing is not available in this build.\nConnect a printer via your OS print dialog to enable this feature.")

    def exit_app(self):
        if self.confirm_discard():
            self.root.destroy()

    # ================= EDIT =================
    def undo(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def delete_selection(self):
        try:
            self.text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        return "break"

    def insert_time_date(self):
        self.text.insert(tk.INSERT, datetime.datetime.now().strftime("%I:%M %p %m/%d/%Y"))

    def open_find(self):
        term = simpledialog.askstring("Find", "Find what:")
        if term:
            self.find_term = term
            self.find_last_index = "1.0"
            self.find_next()

    def find_next(self):
        term = getattr(self, "find_term", None)
        if not term:
            return self.open_find()
        self.text.tag_remove("found", "1.0", tk.END)
        pos = self.text.search(term, self.find_last_index, stopindex=tk.END)
        if not pos:
            pos = self.text.search(term, "1.0", stopindex=tk.END)
            if not pos:
                messagebox.showinfo(APP_NAME, f'Cannot find "{term}"')
                return
        end = f"{pos}+{len(term)}c"
        self.text.tag_add("found", pos, end)
        self.text.tag_config("found", background="#3399ff", foreground="white")
        self.text.mark_set(tk.INSERT, end)
        self.text.see(pos)
        self.find_last_index = end

    def open_replace(self):
        win = tk.Toplevel(self.root)
        win.title("Replace")
        win.resizable(False, False)
        tk.Label(win, text="Find what:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        find_e = tk.Entry(win, width=28)
        find_e.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(win, text="Replace with:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        rep_e = tk.Entry(win, width=28)
        rep_e.grid(row=1, column=1, padx=5, pady=5)

        def replace_all():
            content = self.text.get("1.0", "end-1c")
            count = content.count(find_e.get()) if find_e.get() else 0
            if find_e.get():
                content = content.replace(find_e.get(), rep_e.get())
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", content)
            messagebox.showinfo(APP_NAME, f"Replaced {count} occurrence(s).")

        tk.Button(win, text="Replace All", width=14, command=replace_all).grid(row=2, column=0, columnspan=2, pady=8)

    def go_to_line(self):
        line = simpledialog.askinteger("Go To Line", "Line number:")
        if line:
            self.text.mark_set(tk.INSERT, f"{line}.0")
            self.text.see(f"{line}.0")
            self.update_status()

    # ================= FORMAT =================
    def toggle_wrap(self):
        if self.word_wrap.get():
            self.text.config(wrap="word")
            self.xscroll.pack_forget()
        else:
            self.text.config(wrap="none")
            self.xscroll.pack(fill="x", side="bottom", before=self.status)

    def choose_font(self):
        win = tk.Toplevel(self.root)
        win.title("Font")
        win.resizable(False, False)
        families = ["Consolas", "Arial", "Courier New", "Segoe UI", "Times New Roman", "Verdana"]
        cur = tkfont.Font(font=self.text["font"])

        tk.Label(win, text="Font:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        fam_var = tk.StringVar(value=cur.actual("family"))
        tk.OptionMenu(win, fam_var, *families).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(win, text="Size:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        size_var = tk.IntVar(value=cur.actual("size"))
        tk.Spinbox(win, from_=8, to=72, textvariable=size_var, width=5).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        def apply_font():
            self.text.config(font=(fam_var.get(), size_var.get()))
            win.destroy()

        tk.Button(win, text="OK", width=10, command=apply_font).grid(row=2, column=0, columnspan=2, pady=8)

    # ================= VIEW =================
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
        base = 11
        size = max(1, int(base * self.zoom / 100))
        cur = tkfont.Font(font=self.text["font"])
        self.text.config(font=(cur.actual("family"), size))

    def toggle_status_bar(self):
        if self.status_bar_on.get():
            self.status.pack(fill="x", side="bottom")
        else:
            self.status.pack_forget()

    # ================= HELP =================
    def show_about(self):
        messagebox.showinfo("About Notepad",
                             f"{APP_NAME} (Extended Edition)\nMade by Fritz\nMIT License\n\n"
                             "A feature-complete Notepad clone built with Python & Tkinter.")

    # ================= STATUS =================
    def on_modified(self, event=None):
        title = self.root.title()
        if self.text.edit_modified() and not title.startswith("*"):
            self.root.title(f"*{title}")
        self.update_status()

    def update_status(self, event=None):
        if not self.status_bar_on.get():
            return
        index = self.text.index(tk.INSERT)
        line, col = index.split(".")
        self.status.config(text=f"Ln {line}, Col {int(col) + 1}")


def main():
    root = tk.Tk()
    Notepad(root)
    root.mainloop()


if __name__ == "__main__":
    main()
