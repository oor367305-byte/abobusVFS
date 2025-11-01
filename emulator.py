import tkinter as tk
import os
import argparse
import shlex

if "HOME" not in os.environ and "USERPROFILE" in os.environ:
    os.environ["HOME"] = os.environ["USERPROFILE"]

parser = argparse.ArgumentParser(description="VFS Emulator - Stage 4/5")
parser.add_argument("--vfs", type=str, help="Путь к директории VFS", default="./vfs_root")
parser.add_argument("--script", type=str, help="Путь к стартовому скрипту", default=None)
args = parser.parse_args()

app_running = True
current_dir = "."
vfs = {}
vfs_path = args.vfs
script_path = args.script

def load_vfs(path):
    if not os.path.exists(path) or not os.path.isdir(path):
        raise FileNotFoundError(f"VFS путь '{path}' не найден или не папка")
    vfs_dict = {}
    for root_dir, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        files[:] = [f for f in files if not f.startswith(".")]
        rel_root = os.path.relpath(root_dir, path)
        vfs_dict[rel_root.replace("\\","/")] = {"dirs": list(dirs), "files": list(files), "perm": "rwx"}
    return vfs_dict

def write_output(text):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, text)
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)
    entry.delete(0, tk.END)

def expand_arg(arg):
    return os.path.expandvars(arg)

def arg_to_vfs_rel(path_arg):
    if os.path.isabs(path_arg):
        try:
            common = os.path.commonpath([os.path.abspath(vfs_path), os.path.abspath(path_arg)])
        except Exception:
            return None
        if os.path.abspath(common) != os.path.abspath(vfs_path):
            return None
        rel = os.path.relpath(path_arg, vfs_path)
        if rel == ".":
            return "."
        return rel.replace("\\", "/")
    else:
        combined = os.path.normpath(os.path.join(current_dir, path_arg))
        if combined == "":
            combined = "."
        return combined.replace("\\", "/")

def process_command(command):
    global current_dir, app_running
    if not app_running:
        return
    command = command.strip()
    if not command:
        return
    try:
        parts = shlex.split(command)
    except Exception:
        parts = command.split()
    if not parts:
        return

    cmd = parts[0]
    args = parts[1:]
    if cmd.startswith("$") and len(parts) == 1:
        val = os.path.expandvars(cmd)
        write_output(f"> {command}\n{val}\n")
        return

    write_output(f"> {command}\n")

    if cmd == "ls":
        if len(args) != 0:
            write_output("Ошибка: команда 'ls' не принимает аргументы\n")
            return
        files = vfs.get(current_dir, {"dirs": [], "files": [], "perm": "rwx"})
        write_output(f"Dirs: {files['dirs']}\nFiles: {files['files']}\n")
        return

    if cmd == "cd":
        if len(args) > 1:
            write_output("Ошибка: команда 'cd' принимает не более одного аргумента\n")
            return
        if len(args) == 0 or args[0] in [".", "/"]:
            current_dir = "."
            return
        raw = args[0]
        if raw == "$HOME":
            target_rel = "."
        else:
            raw_expanded = expand_arg(raw)
            target_rel = arg_to_vfs_rel(raw_expanded)
        if target_rel in vfs:
            current_dir = target_rel
        else:
            write_output(f"Ошибка: директория '{raw}' не найдена в VFS\n")
        return

    if cmd == "head":
        if len(args) != 1:
            write_output("Ошибка: команда 'head' требует ровно один аргумент\n")
            return
        raw = args[0]
        raw_expanded = expand_arg(raw)
        rel = arg_to_vfs_rel(raw_expanded)
        if rel is None:
            write_output(f"Ошибка: файл '{raw}' не найден в VFS\n")
            return
        dirpart, fname = os.path.split(rel)
        dirpart = dirpart if dirpart != "" else "."
        files = vfs.get(dirpart, {"dirs": [], "files": []})["files"]
        if fname not in files:
            write_output(f"Ошибка: файл '{fname}' не найден\n")
            return
        real_path = os.path.join(vfs_path, rel)
        try:
            with open(real_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 10:
                        break
                    write_output(line)
        except Exception as e:
            write_output(f"Ошибка чтения файла: {e}\n")
        return

    if cmd == "echo":
        expanded_args = [os.path.expandvars(a) for a in args]
        write_output(" ".join(expanded_args) + "\n")
        return

    if cmd == "mkdir":
        if len(args) != 1:
            write_output("Ошибка: команда 'mkdir' требует ровно один аргумент\n")
            return
        rel = arg_to_vfs_rel(expand_arg(args[0]))
        if rel in vfs:
            write_output(f"Ошибка: директория '{args[0]}' уже существует\n")
            return
        vfs[rel] = {"dirs": [], "files": [], "perm": "rwx"}
        parent = os.path.dirname(rel) if os.path.dirname(rel) != "" else "."
        if parent in vfs:
            vfs[parent]["dirs"].append(os.path.basename(rel))
        write_output(f"Директория '{args[0]}' создана\n")
        return

    if cmd == "chmod":
        if len(args) != 2:
            write_output("Ошибка: команда 'chmod' требует два аргумента\n")
            return
        rel = arg_to_vfs_rel(expand_arg(args[0]))
        if rel not in vfs:
            write_output(f"Ошибка: файл или директория '{args[0]}' не найден\n")
            return
        perm = args[1]
        if perm not in ["r", "w", "x"]:
            write_output("Ошибка: допустимые права только 'r', 'w', 'x'\n")
            return
        vfs[rel]["perm"] = perm
        write_output(f"Права для '{args[0]}' установлены: {perm}\n")
        return

    if cmd == "exit":
        write_output("Выход из эмулятора...\n")
        app_running = False
        root.destroy()
        return

    write_output(f"Ошибка: неизвестная команда '{cmd}'\n")

root = tk.Tk()
root.title("VFS Emulator - Stage 4/5")
root.geometry("800x500")
root.resizable(False, False)

output_text = tk.Text(root, wrap="word")
output_text.pack(fill="both", expand=True, padx=6, pady=6)
output_text.config(state=tk.DISABLED)

entry = tk.Entry(root)
entry.pack(fill="x", padx=6, pady=(0,6))
entry.bind("<Return>", lambda event: process_command(entry.get()))
entry.focus_set()

write_output(f"VFS path: {vfs_path}\n")
write_output(f"Script path: {script_path}\n")

try:
    vfs = load_vfs(vfs_path)
    write_output(f"VFS загружена. Корень: {list(vfs.keys())}\n")
except FileNotFoundError as e:
    write_output(f"{e}\n")

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
                write_output(f"Ошибка при выполнении скрипта: {e}\n")
    else:
        if script_path:
            write_output(f"Script '{script_path}' не найден\n")

root.after(100, run_script)
root.mainloop()
