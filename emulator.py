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
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        files[:] = [f for f in files if not f.startswith(".")]
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
        output_text.config(state=tk.NORMAL)
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
        elif cmd == "head":
            if not args:
                output_text.insert(tk.END, "Error: head requires a file name\n")
            else:
                filename = args[0]
                files = vfs.get(current_dir, {"dirs": [], "files": []})["files"]
                if filename in files:
                    path = os.path.join(vfs_path, current_dir, filename)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            for i, line in enumerate(f):
                                if i >= 10:  # head выводит первые 10 строк
                                    break
                                output_text.insert(tk.END, line)
                    except Exception as e:
                        output_text.insert(tk.END, f"Error reading file: {e}\n")
                else:
                    output_text.insert(tk.END, f"Error: file '{filename}' not found\n")
        elif cmd == "echo":
            output_text.insert(tk.END, " ".join(args) + "\n")
        elif cmd == "exit":
            output_text.insert(tk.END, "Exiting emulator...\n")
            app_running = False
            root.destroy()
        else:
            output_text.insert(tk.END, f"Error: unknown command '{cmd}'\n")
        output_text.see(tk.END)
        entry.delete(0, tk.END)
        output_text.config(state=tk.DISABLED)
    except Exception as e:
        output_text.config(state=tk.DISABLED)
        output_text.insert(tk.END, f"Error: {e}\n")

root = tk.Tk()
root.title("VFS Emulator - Stage 4")
root.geometry("600x400")

output_text = tk.Text(root, height=20, width=80)
output_text.pack(pady=10)
output_text.config(state=tk.DISABLED)

entry = tk.Entry(root, width=80)
entry.pack(pady=5)
entry.bind("<Return>", lambda event: process_command(entry.get()))

vfs_path = sys.argv[1] if len(sys.argv) > 1 else "./vfs_root"
script_path = sys.argv[2] if len(sys.argv) > 2 else None

output_text.config(state=tk.NORMAL)
output_text.insert(tk.END, f"VFS path: {vfs_path}\n")
output_text.insert(tk.END, f"Script path: {script_path}\n")
output_text.config(state=tk.DISABLED)

try:
    vfs = load_vfs(vfs_path)
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, f"VFS загружена. Корень: {list(vfs.keys())}\n")
    output_text.config(state=tk.DISABLED)
except FileNotFoundError as e:
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, f"{e}\n")
    output_text.config(state=tk.DISABLED)

def run_script():
    global app_running
    if not app_running or not script_path:
        return
    path_to_try = script_path
    if not os.path.exists(path_to_try):
        path_to_try = os.path.join(vfs_path, script_path)
    if os.path.exists(path_to_try):
        try:
            with open(path_to_try, "r", encoding="utf-8") as f:
                for line in f:
                    if not app_running:
                        break
                    line = line.strip()
                    if line == "" or line.startswith("#"):
                        continue
                    process_command(line)
        except Exception as e:
            if app_running:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"Error executing script: {e}\n")
                output_text.config(state=tk.DISABLED)
    else:
        if script_path:
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"Script '{script_path}' not found\n")
            output_text.config(state=tk.DISABLED)

root.after(100, run_script)
root.mainloop()
