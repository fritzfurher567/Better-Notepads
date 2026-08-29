#Fritz Notepad - Apache
import tkinter as tk
from tkinter import filedialog as fd,messagebox as mb,simpledialog as sd
f=None
S,E,D="1.0","end-1c",tk.END
r=tk.Tk();r.title("Untitled")
t=tk.Text(r,undo=1,wrap="word",font=("Consolas",11));t.pack(fill="both",expand=1)
def L(p):t.delete(S,D);t.insert(S,open(p).read())
def T(p):r.title(p.split("/")[-1])
def ak():
 if not t.edit_modified():return 1
 a=mb.askyesnocancel("N","Save?")
 if a:sv()
 return a is not None
def n():
 global f
 if ak():t.delete(S,D);f=None;r.title("Untitled");t.edit_modified(0)
def o():
 global f
 if ak() and(p:=fd.askopenfilename()):f=p;L(p);T(p);t.edit_modified(0)
def w(p):open(p,"w").write(t.get(S,E));t.edit_modified(0)
def sv():w(f) if f else sa()
def sa():
 global f
 if p:=fd.asksaveasfilename():f=p;w(p);T(p)
def rp():
 a=sd.askstring("F","Find");b=sd.askstring("R","Replace")
 if a:t.delete(S,D);t.insert(S,t.get(S,E).replace(a,b or ""))
def ft():
 if a:=sd.askstring("F","Font"):t.config(font=(a,11))
def wr():t.config(wrap="word" if wv.get() else "none")
def ex():
 if ak():r.destroy()
ev=lambda s:lambda:t.event_generate(s)
m=tk.Menu(r);r.config(menu=m)
ms=[]
for nm in "File","Edit","Format","View","Help":
 mm=tk.Menu(m,tearoff=0);m.add_cascade(label=nm,menu=mm);ms.append(mm)
fm,em,ftm,vm,hm=ms
for l,c in[("New",n),("Open",o),("Save",sv),("SaveAs",sa),("Print",lambda:mb.showinfo("P","N/A")),("Exit",ex)]:fm.add_command(label=l,command=c)
for l,c in[("Undo",t.edit_undo),("Cut",ev("<<Cut>>")),("Copy",ev("<<Copy>>")),("Paste",ev("<<Paste>>")),("Find",rp)]:em.add_command(label=l,command=c)
wv=tk.BooleanVar(value=1)
ftm.add_checkbutton(label="Wrap",variable=wv,command=wr)
ftm.add_command(label="Font",command=ft)
r.bind("<Control-n>",lambda e:n());r.bind("<Control-o>",lambda e:o())
r.bind("<Control-s>",lambda e:sv());r.bind("<Control-h>",lambda e:rp())
r.protocol("WM_DELETE_WINDOW",ex)
r.mainloop()
