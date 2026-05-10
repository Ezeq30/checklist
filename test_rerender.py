import tkinter as tk

root = tk.Tk()
root.title("Re-render Bug Test")

check_vars = {}
content_frame = None

def render():
    global content_frame
    if content_frame:
        for w in content_frame.winfo_children():
            w.destroy()

    if not content_frame:
        content_frame = tk.Frame(root, bg="lightgray")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    check_vars.clear()

    items = ["Item A", "Item B", "Item C", "Item D"]
    for idx, item in enumerate(items):
        f = tk.Frame(content_frame, bg="white")
        f.grid(row=0, column=idx, sticky="nsew", padx=2, pady=2)

        var = tk.BooleanVar(value=False)
        check_vars[item] = var

        def toggle(it=item, v=var):
            print(f"TOGGLE: {it} -> {v.get()}", flush=True)

        tk.Checkbutton(f, text=item, variable=var, command=toggle).pack()

    print(f"render() done, check_vars={[(k,v.get()) for k,v in check_vars.items()]}", flush=True)

def force_render():
    print("FORCE RENDER called", flush=True)
    render()

btn_reload = tk.Button(root, text="Reload (force render)", command=force_render)
btn_reload.pack()

btn_print = tk.Button(root, text="Print check_vars", command=lambda: print(f"check_vars={[(k,v.get()) for k,v in check_vars.items()]}", flush=True))
btn_print.pack()

render()
root.mainloop()
