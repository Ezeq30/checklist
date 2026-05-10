import tkinter as tk

root = tk.Tk()
root.title("Simple Test with Lock")

f = tk.Frame(root, bg="gray")
f.pack(fill="both", expand=True)

cv = {}
_render_locked = False

def render():
    global _render_locked
    if _render_locked:
        print("render SKIPPED due to lock", flush=True)
        return
    print("render ACTUAL", flush=True)
    for w in f.winfo_children():
        w.destroy()
    cv.clear()
    for idx, item in enumerate(["A", "B", "C", "D"]):
        hf = tk.Frame(f, bg="lightgray")
        hf.grid(row=0, column=idx)
        v = tk.BooleanVar(value=False)
        cv[item] = v
        tk.Checkbutton(hf, text=item, variable=v, bg="lightgray").pack()

def force_render():
    global _render_locked
    _render_locked = True
    print("force render", flush=True)
    render()
    _render_locked = False

tk.Button(root, text="Re-render (force)", command=force_render).pack()
tk.Button(root, text="Print vars", command=lambda: print(f"cv={[(k,v.get()) for k,v in cv.items()]}", flush=True)).pack()

render()
root.mainloop()
