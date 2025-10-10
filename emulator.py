import tkinter as tk
import os
import sys


def load_vfs(path):
    if not os.path.exists(path) or not os.path.isdir(path):
        raise FileNotFoundError(f"VFS path '{path}' не найден или не папка")

    vfs = {}
    for root_dir, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root_dir, path)
        vfs[rel_root] = {"dirs": dirs, "files": files}
    return vfs



current_dir = "."  # текущая директория в VFS
vfs = {}


def process_command(command=None):
    global current_dir
    if command is None:
        command = entry.get().strip()
        entry.delete(0, tk.END)

    output_text.insert(tk.END, f"> {command}\n")

    command = os.path.expandvars(command)
    parts = command.split()

    if not parts:
        return

    cmd = parts[0]
    args = parts[1:]

    if cmd == "ls":
        files = vfs.get(current_dir, {"dirs": [], "files": []})
        output_text.insert(tk.END, f"Dirs: {files['dirs']}, Files: {files['files']}\n")
    elif cmd == "cd":
        if not args:
            output_text.insert(tk.END, "Error: cd requires an argument\n")
            return
        target = args[0]
        new_dir = os.path.normpath(os.path.join(current_dir, target))
        if new_dir in vfs:
            current_dir = new_dir
        else:
            output_text.insert(tk.END, f"Error: directory '{target}' not found in VFS\n")
    elif cmd == "exit":
        root.destroy()
    else:
        output_text.insert(tk.END, f"Error: unknown command '{cmd}'\n")

    output_text.see(tk.END)


root = tk.Tk()
root.title("VFS Emulator - Configurable")
root.geometry("600x400")

output_text = tk.Text(root, height=20, width=80)
output_text.pack(pady=10)

entry = tk.Entry(root, width=80)
entry.pack(pady=5)
entry.bind("<Return>", lambda event: process_command())


# Читаем аргументы командной строки
# python emulator.py <vfs_path> <script_path>
vfs_path = sys.argv[1] if len(sys.argv) > 1 else "./vfs_root"
script_path = sys.argv[2] if len(sys.argv) > 2 else None

output_text.insert(tk.END, f"VFS path: {vfs_path}\n")
output_text.insert(tk.END, f"Script path: {script_path}\n")

try:
    vfs = load_vfs(vfs_path)
    output_text.insert(tk.END, f"VFS загружена. Корень: {list(vfs.keys())}\n")
except FileNotFoundError as e:
    output_text.insert(tk.END, f"{e}\n")


if script_path and os.path.exists(script_path):
    try:
        with open(script_path, "r") as f:
            for line in f:
                line = line.strip()
                if line == "" or line.startswith("#"):
                    continue
                process_command(line)
    except Exception as e:
        output_text.insert(tk.END, f"Error executing script: {e}\n")
elif script_path:
    output_text.insert(tk.END, f"Script '{script_path}' not found\n")

root.mainloop()
