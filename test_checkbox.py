import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Checkbox Test")

var = tk.BooleanVar(value=False)

def on_toggle():
    print(f"[TEST] on_toggle called, var.get()={var.get()}", flush=True)

cb = tk.Checkbutton(root, text="Test Checkbox", variable=var, command=on_toggle)
cb.pack(padx=20, pady=20)

btn = tk.Button(root, text="Print var", command=lambda: print(f"[TEST] button: var.get()={var.get()}", flush=True))
btn.pack()

root.mainloop()
