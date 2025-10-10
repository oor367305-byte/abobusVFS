import tkinter as tk
import os
import sys

app_running = True
current_dir = "."
vfs = {}

def load_vfs(path):
    if not os.path.exists(path) or not os.path.isdir(path):
        raise FileNotFoundError(f"VFS path '{path}' не найден или не папка")
    vfs_dict = {}
    for root_dir, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root_dir, path)
        vfs_dict[rel_root] = {"dirs": dirs, "files": files}
    return vfs_dict

def process_command(command):
    global current_dir, app_running
    if not app_running:
        return
    command = os.path.expandvars(command)
    parts = command.strip().split()
    if not parts:
        return
    cmd = parts[0]
    args = parts[1:]
    try:
        output_text.insert(tk.END, f"> {command}\n")
        if cmd == "ls":
            files = vfs.get(current_dir, {"dirs": [], "files": []})
            output_text.insert(tk.END, f"Dirs: {files['dirs']}\nFiles: {files['files']}\n")
        elif cmd == "cd":
            if not args or args[0] in [".", "/"]:
                current_dir = "."
            else:
                target = " ".join(args)
                new_dir = os.path.normpath(os.path.join(current_dir, target))
                if new_dir == "":
                    new_dir = "."
                if new_dir in vfs:
                    current_dir = new_dir
                else:
                    output_text.insert(tk.END, f"Error: directory '{target}' not found in VFS\n")
        elif cmd == "exit":
            output_text.insert(tk.END, "Exiting emulator...\n")
            app_running = False
            root.destroy()
        else:
            output_text.insert(tk.END, f"Error: unknown command '{cmd}'\n")
        output_text.see(tk.END)
    except Exception as e:
        output_text.insert(tk.END, f"Error: {e}\n")

root = tk.Tk()
root.title("VFS Emulator - Stage 3")
root.geometry("600x400")

output_text = tk.Text(root, height=20, width=80)
output_text.pack(pady=10)

entry = tk.Entry(root, width=80)
entry.pack(pady=5)
entry.bind("<Return>", lambda event: process_command(entry.get()))

vfs_path = sys.argv[1] if len(sys.argv) > 1 else "./vfs_root"
script_path = sys.argv[2] if len(sys.argv) > 2 else None

output_text.insert(tk.END, f"VFS path: {vfs_path}\n")
output_text.insert(tk.END, f"Script path: {script_path}\n")

try:
    vfs = load_vfs(vfs_path)
    output_text.insert(tk.END, f"VFS загружена. Корень: {list(vfs.keys())}\n")
except FileNotFoundError as e:
    output_text.insert(tk.END, f"{e}\n")

def run_script():
    global app_running
    if not app_running or not script_path:
        return
    if os.path.exists(script_path):
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not app_running:
                        break
                    line = line.strip()
                    if line == "" or line.startswith("#"):
                        continue
                    process_command(line)
        except Exception as e:
            if app_running:
                output_text.insert(tk.END, f"Error executing script: {e}\n")
    else:
        if script_path:
            output_text.insert(tk.END, f"Script '{script_path}' not found\n")

root.after(100, run_script)
root.mainloop()
