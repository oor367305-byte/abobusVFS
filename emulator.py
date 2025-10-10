import tkinter as tk
import os


def execute_command(command):
    command = os.path.expandvars(command.strip())
    if not command:
        return f""
    parts = command.split()
    cmd, args = parts[0], parts[1:]

    if cmd == "ls":
        return f"Команда: {cmd}, аргументы: {args}\n"
    elif cmd == "cd":
        return f"Команда: {cmd}, аргументы: {args}\n"
    elif cmd == "exit":
        root.destroy()
        return ""
    else:
        return f"Ошибка: неизвестная команда '{cmd}'\n"

def process_command(event=None):
    cmd = entry.get()
    output_text.insert(tk.END, f"> {cmd}\n")
    result = execute_command(cmd)
    output_text.insert(tk.END, result)
    output_text.see(tk.END)
    entry.delete(0, tk.END)


root = tk.Tk()
root.title("VFS Emulator - Этап 1")
root.geometry("600x400")

output_text = tk.Text(root, height=20, width=80)
output_text.pack(pady=10)

entry = tk.Entry(root, width=80)
entry.pack(pady=5)
entry.bind("<Return>", process_command)

output_text.insert(tk.END, "Добро пожаловать в VFS Emulator (Этап 1)\n")
output_text.insert(tk.END, "Доступные команды: ls, cd, exit\n")

root.mainloop()
