import tkinter as tk
from datetime import datetime, timedelta

root = tk.Tk()
root.title("Checkbox Test")

panel_frame = tk.Frame(root, bg="gray")
panel_frame.pack(fill="both", expand=True)

checklist_frame = tk.Frame(panel_frame, bg="gray")
checklist_frame.pack(fill="both", expand=True)

check_vars = {}

def render():
    print("[TEST] render called", flush=True)
    for w in checklist_frame.winfo_children():
        w.destroy()
    check_vars.clear()

    items = ["Item A", "Item B", "Item C", "Item D"]
    cols = 2
    row_count = 2

    for idx, item in enumerate(items):
        row = idx % row_count
        col = idx // row_count

        frame_item = tk.Frame(checklist_frame, bg="lightgray", pady=3, padx=5)
        frame_item.grid(row=row, column=col, sticky="nsew", pady=1, padx=1)

        var = tk.BooleanVar(value=False)
        check_vars[item] = var

        tk.Checkbutton(
            frame_item,
            text=item,
            variable=var,
            bg="lightgray",
            fg="black",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
            justify="left",
            command=lambda it=item, v=var: on_toggle(it, v),
        ).pack(fill="x", expand=True)

    checklist_frame.columnconfigure(0, weight=1)
    checklist_frame.columnconfigure(1, weight=1)

def on_toggle(item, var):
    print(f"[TEST] on_toggle item={item} var.get()={var.get()}", flush=True)

btn_render = tk.Button(root, text="Re-render", command=render)
btn_render.pack()

btn_save = tk.Button(root, text="Print check_vars", command=lambda: print(f"[TEST] check_vars={[(k,v.get()) for k,v in check_vars.items()]}", flush=True))
btn_save.pack()

render()
root.mainloop()
