import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess, ctypes, requests, tempfile, winreg

API = "https://DEIN_RENDER_SERVER.onrender.com"
APPS = "https://app.netlify.com/projects/sme-launcher/overview/apps/"

BG="#1e1e1e"; FG="#fff"; BTN="#2d2d2d"
ADMIN_PASSWORD="admin123"

# Taskbar
def hide_taskbar():
    ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd",None),0)

def show_taskbar():
    ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd",None),5)

# Taskmanager
def block_taskmanager():
    try:
        key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key,"DisableTaskMgr",0,winreg.REG_DWORD,1)
    except: pass

def unblock_taskmanager():
    try:
        key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key,"DisableTaskMgr",0,winreg.REG_DWORD,0)
    except: pass

# Apps starten
def start_program(name):
    url = APPS + name
    r = requests.get(url, stream=True)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".exe")
    for c in r.iter_content(1024):
        tmp.write(c)
    tmp.close()
    subprocess.Popen(tmp.name)

# API
def get_users():
    return requests.get(API+"/users").json()

def get_user_apps(user):
    return requests.get(API+f"/apps/{user}").json()

def save_user_apps(user,data):
    requests.post(API+f"/apps/{user}",json=data)

def get_pinned(user):
    return requests.get(API+f"/pinned/{user}").json()

def save_pinned(user,data):
    requests.post(API+f"/pinned/{user}",json=data)

users = get_users()

current_user=None

def load_apps():
    for w in apps_frame.winfo_children(): w.destroy()

    pinned = get_pinned(current_user)
    row=0

    if pinned:
        tk.Label(apps_frame,text="⭐ Favoriten",bg=BG,fg=FG).grid(row=row)
        row+=1
        for p in pinned:
            tk.Button(apps_frame,text=p,bg=BTN,fg=FG,
                command=lambda x=p:start_program(x)).grid(row=row)
            row+=1

    apps = get_user_apps(current_user)
    tk.Label(apps_frame,text="Apps",bg=BG,fg=FG).grid(row=row)
    row+=1
    for a in apps:
        tk.Button(apps_frame,text=a,bg=BTN,fg=FG,
            command=lambda x=a:start_program(x)).grid(row=row)
        row+=1

def select_user(u):
    global current_user
    pw = simpledialog.askstring("Passwort",f"{u}",show="*")
    if pw == users[u]:
        current_user=u
        login_frame.pack_forget()
        main_frame.pack(fill="both",expand=True)
        load_apps()
    else:
        messagebox.showerror("Fehler","Falsch")

def open_admin():
    pw=simpledialog.askstring("Admin","Passwort",show="*")
    if pw!=ADMIN_PASSWORD: return

    win=tk.Toplevel(root)
    tk.Button(win,text="Reload",command=load_apps).pack()
    tk.Button(win,text="Exit",command=root.destroy).pack()

# GUI
root=tk.Tk()
root.attributes("-fullscreen",True)
root.configure(bg=BG)
root.protocol("WM_DELETE_WINDOW", lambda: None)

hide_taskbar()
block_taskmanager()

login_frame=tk.Frame(root,bg=BG); login_frame.pack(fill="both",expand=True)
uf=tk.Frame(login_frame,bg=BG); uf.pack(side="bottom",anchor="se")

for u in users:
    tk.Button(uf,text=u,bg=BTN,fg=FG,command=lambda x=u:select_user(x)).pack(side="right")

main_frame=tk.Frame(root,bg=BG)
apps_frame=tk.Frame(main_frame,bg=BG); apps_frame.pack()

tk.Button(root,text="⚙",command=open_admin).place(x=20,y=20)

root.mainloop()
show_taskbar(); unblock_taskmanager()
