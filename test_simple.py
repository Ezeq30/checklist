import tkinter as tk

root = tk.Tk()
root.title("Simple Test")

f = tk.Frame(root, bg="gray")
f.pack(fill="both", expand=True)

cv = {}

def render():
    for w in f.winfo_children():
        w.destroy()
    cv.clear()
    for idx, item in enumerate(["A", "B", "C", "D"]):
        hf = tk.Frame(f, bg="lightgray")
        hf.grid(row=0, column=idx)
        v = tk.BooleanVar(value=False)
        cv[item] = v
        tk.Checkbutton(hf, text=item, variable=v, bg="lightgray").pack()

def on_toggle():
    print(f"toggle! cv={[(k,v.get()) for k,v in cv.items()]}", flush=True)

def force_render():
    print("force render", flush=True)
    render()

tk.Button(root, text="Re-render", command=force_render).pack()
tk.Button(root, text="Print vars", command=lambda: print(f"cv={[(k,v.get()) for k,v in cv.items()]}", flush=True)).pack()

render()
root.mainloop()
