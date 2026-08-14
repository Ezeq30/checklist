import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json
import os
import sys
import tempfile

HIPODROMOS = {
    "San isidro": {"color": "#2E7D32", "nombre": "SAN ISIDRO", "checked": "#4CAF50"},
    "La plata": {"color": "#1565C0", "nombre": "LA PLATA", "checked": "#42A5F5"},
    "Palermo": {"color": "#F9A825", "nombre": "PALERMO", "checked": "#FDD835"},
    "Sin hipodromo": {"color": "#C62828", "nombre": "SIN HIPODROMO", "checked": "#EF4444"},
}

COLORS = {
    "bg": "#080D16",
    "fg": "#F1F5F9",
    "accent": "#38BDF8",
    "card": "#121A26",
    "card_soft": "#1A2433",
    "surface": "#0E1520",
    "border": "#243044",
    "hover_soft": "#1E2A3A",
    "hover_accent": "#0EA5E9",
    "muted": "#94A3B8",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#06B6D4",
    "today_ring": "#F8FAFC",
    "input_border": "#334155",
    "row": "#121A26",
    "row_hover": "#1A2433",
}


def hipo_fg(hipo):
    if hipo == "Palermo":
        return "black"
    if hipo in HIPODROMOS:
        return "white"
    return COLORS["fg"]


def hipo_color(hipo, fallback=None):
    if hipo and hipo in HIPODROMOS:
        return HIPODROMOS[hipo]["color"]
    return COLORS["card"] if fallback is None else fallback


def hipo_checked(hipo):
    if hipo and hipo in HIPODROMOS:
        return HIPODROMOS[hipo].get("checked", COLORS["success"])
    return COLORS["success"]

CHECKLIST_DIA1 = [
    "FECHA Y ESTADO", "MEET Y PERFORMANCE", "CALC PRICES",
    "REGLA DE CALCULO POR CARRERA", "CABALLOS Y APUESTAS POR CARRERA",
    "TABLA DE COMISIONES POR CARRERA", "MONTOS MINIMOS POR APUESTA Y CARRERA",
    "DEFAULT MINIMOS ARG USD PER", "TIM BETTING CONTROL POR ASOCIACION",
    "IMPORT BETTING CONTROL", "LOCAL ASSOC BETTING CONTROL",
    "SALES TAX ASSOCIATION", "PRINTERS", "STATE BETTING CONTROL"
]

CHECKLIST_DIA2_SAN_ISIDRO = [
    "SETEAR CATEGORIA",
    "VOLVER A REVISAR EL PROGRAMA Y POSTING",
    "VER SI HAY BORRADOS AGREGADOS",
    "BLOQUEAR / DESBLOQUEAR AGENTES",
    "PONER TIPS EN SERVICIO",
    "PONER TERMINALES EN SERVICIO",
    "RESETEAR TERMINALES",
    "TELLER VOUCHER LIMIT $500,000",
    "ABRIR LA VENTA A LA HORA INDICADA",
    "CANAL 26 ASIGNACION 29",
    "GENERAR DETALLE",
    "CARGAR EL VIDEO EN LA APP MOBILE",
]

CHECKLIST_DIA2_LA_PLATA = [
    "SETEAR CATEGORIA",
    "VOLVER A REVISAR EL PROGRAMA Y POSTING",
    "CAMBIAR EN LAS VENTANILLAS LOS AGENTES",
    "BLOQUEAR / DESBLOQUEAR AGENTES",
    "PONER TIPS EN SERVICIO",
    "PONER TERMINALES EN SERVICIO",
    "RESETEAR TERMINALES",
    "ABRIR LA VENTA A LA HORA INDICADA",
    "CARGAR EL VIDEO EN LA APP MOBILE",
    "SETEAR VIDEOS POR MEET",
]

CHECKLIST_DIA2_PALERMO = [
    "SETEAR CATEGORIA",
    "VOLVER A REVISAR EL PROGRAMA",
    "BLOQUEAR / DESBLOQUEAR AGENTES",
    "PONER TIPS EN SERVICIO",
    "PONER TERMINALES EN SERVICIO",
    "RESETEAR TERMINALES",
    "SETEAR VIDEOS POR MEET"
]

CHECKLIST_DIA2_POR_HIPODROMO = {
    "San isidro": CHECKLIST_DIA2_SAN_ISIDRO,
    "La plata": CHECKLIST_DIA2_LA_PLATA,
    "Palermo": CHECKLIST_DIA2_PALERMO
}

if getattr(sys, 'frozen', False):
    exec_dir = os.path.dirname(sys.executable)
else:
    exec_dir = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(exec_dir, "data.json")

class StyledButton(tk.Button):
    def __init__(self, master, **kwargs):
        bg = kwargs.pop("bg", COLORS["accent"])
        fg = kwargs.pop("fg", COLORS["fg"])
        hover_bg = kwargs.pop("hover_bg", COLORS["hover_soft"])
        padx = kwargs.pop("padx", 8)
        pady = kwargs.pop("pady", 3)
        font = kwargs.pop("font", ("Segoe UI", 8, "bold"))
        super().__init__(
            master,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=padx,
            pady=pady,
            font=font,
            cursor="hand2",
            **kwargs
        )
        self._base_bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_bg(self, bg, hover_bg=None, fg=None):
        self._base_bg = bg
        if hover_bg is not None:
            self._hover_bg = hover_bg
        if fg is not None:
            self._fg = fg
            self.config(fg=fg, activeforeground=fg)
        self.config(bg=bg, activebackground=bg)

    def _on_enter(self, _event):
        self.config(cursor="hand2", bg=self._hover_bg, activebackground=self._hover_bg)

    def _on_leave(self, _event):
        self.config(bg=self._base_bg, activebackground=self._base_bg)


class SegmentedGroup(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            bg=COLORS["card"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            **kwargs
        )


class SegmentedButton(tk.Button):
    def __init__(self, master, **kwargs):
        hover_bg = kwargs.pop("hover_bg", COLORS["hover_soft"])
        super().__init__(
            master,
            relief="flat",
            bd=0,
            padx=10,
            pady=3,
            font=("Segoe UI", 8, "bold"),
            activeforeground=COLORS["fg"],
            **kwargs
        )
        self._base_bg = self.cget("bg")
        self._hover_bg = hover_bg
        self._enabled = True
        self._accent = COLORS["accent"]
        self._accent_fg = COLORS["fg"]
        self._active = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_accent(self, bg, fg=None):
        self._accent = bg
        self._accent_fg = fg or COLORS["fg"]
        if self._active:
            self.set_active(True)

    def set_active(self, active):
        self._active = active
        if not self._enabled:
            self._base_bg = COLORS["card"]
            self.config(bg=COLORS["card"], fg=COLORS["muted"], activebackground=COLORS["card"], state="disabled")
            return
        if active:
            self._base_bg = self._accent
            self.config(bg=self._accent, fg=self._accent_fg, activebackground=self._accent, state="normal")
        else:
            self._base_bg = COLORS["card"]
            self.config(bg=COLORS["card"], fg=COLORS["muted"], activebackground=COLORS["card"], state="normal")

    def set_enabled(self, enabled):
        self._enabled = enabled
        state = "normal" if enabled else "disabled"
        fg = COLORS["fg"] if enabled else COLORS["muted"]
        self.config(state=state, fg=fg)
        if not enabled:
            self._active = False
            self._base_bg = COLORS["card"]
            self.config(bg=COLORS["card"], activebackground=COLORS["card"])

    def _on_enter(self, _event):
        if not self._enabled:
            return
        self.config(cursor="hand2")
        if not self._active:
            self.config(bg=self._hover_bg, activebackground=self._hover_bg, fg=COLORS["fg"])

    def _on_leave(self, _event):
        self.config(cursor="")
        fg = self._accent_fg if self._active else (COLORS["fg"] if self._enabled else COLORS["muted"])
        self.config(bg=self._base_bg, activebackground=self._base_bg, fg=fg)


class CheckMark(tk.Canvas):
    SIZE = 16

    def __init__(self, master, var, color, mark_fg="white", bg=None):
        bg = bg or COLORS["row"]
        super().__init__(
            master,
            width=self.SIZE,
            height=self.SIZE,
            highlightthickness=0,
            bd=0,
            bg=bg,
            cursor="hand2",
        )
        self.var = var
        self.color = color
        self.mark_fg = mark_fg
        self._bg = bg
        self.bind("<Button-1>", self._toggle)
        self._trace = var.trace_add("write", lambda *_: self._draw())
        self._draw()

    def set_bg(self, bg):
        self._bg = bg
        self.config(bg=bg)
        self._draw()

    def _toggle(self, _event=None):
        self.var.set(not self.var.get())
        return "break"

    def _draw(self):
        self.delete("all")
        s = self.SIZE
        pad = 2
        if self.var.get():
            self.create_oval(pad, pad, s - pad, s - pad, fill=self.color, outline=self.color)
            self.create_line(5, 9, 7, 11, 12, 6, fill=self.mark_fg, width=2, capstyle="round", joinstyle="round")
        else:
            self.create_oval(pad, pad, s - pad, s - pad, fill=self._bg, outline=self.color, width=2)


def _round_poly(canvas, x1, y1, x2, y2, r, **kwargs):
    r = max(2, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


class DayCell(tk.Canvas):
    def __init__(self, master, on_click):
        super().__init__(
            master,
            width=42,
            height=28,
            highlightthickness=0,
            bd=0,
            bg=COLORS["surface"],
            cursor="",
        )
        self._on_click = on_click
        self.text = ""
        self._fill = COLORS["card"]
        self._fg = COLORS["fg"]
        self._today = False
        self._hover = False
        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)

    def set_day(self, text, fill, fg, today=False):
        self.text = str(text) if text else ""
        self._fill = fill
        self._fg = fg
        self._today = today
        self._redraw()

    def clear(self):
        self.text = ""
        self._today = False
        self._hover = False
        self.config(cursor="")
        self._redraw()

    def _click(self, _event=None):
        if self.text:
            self._on_click()

    def _enter(self, _event=None):
        if self.text:
            self._hover = True
            self.config(cursor="hand2")
            self._redraw()

    def _leave(self, _event=None):
        self._hover = False
        self.config(cursor="")
        self._redraw()

    def _redraw(self):
        self.delete("all")
        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        if w < 8 or h < 8:
            return
        if not self.text:
            return
        pad = 2
        fill = self._fill
        if self._hover and fill in (COLORS["card"], COLORS["surface"]):
            fill = COLORS["hover_soft"]
        radius = 7
        _round_poly(self, pad, pad, w - pad - 1, h - pad - 1, radius, fill=fill, outline=fill)
        if self._today:
            _round_poly(
                self,
                pad + 1,
                pad + 1,
                w - pad - 2,
                h - pad - 2,
                radius - 1,
                fill="",
                outline=COLORS["today_ring"],
                width=2,
            )
        self.create_text(w / 2, h / 2, text=self.text, fill=self._fg, font=("Segoe UI", 8, "bold"))

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Checklist Hipódromos")
        self.root.geometry("940x395")
        self.root.resizable(False, False)
        self.root.minsize(940, 395)
        self.root.maxsize(940, 395)
        self.root.configure(bg=COLORS["bg"])

        self.data = self.cargar_datos()  # Carga datos desde data.json
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.admin_mode = False
        self.login_popup_abierto = False

        self.setup_ui()
        # FIX: Actualizarinfo_paneles se llama al inicio para cargar estados de D2
        # Esto asegura que si D1 ya estaba completado, D2 se habilite correctamente
        self.actualizar_info_paneles()
        self.actualizar_info_paneles()

    def cargar_datos(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"calendario": {}, "checklist": {}}

    def guardar_datos(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=COLORS["bg"])
        main_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.left_frame = tk.Frame(main_frame, bg=COLORS["bg"], width=400)
        self.left_frame.pack(side="left", fill="y", expand=False, padx=(0, 6))
        self.left_frame.pack_propagate(False)

        right_frame = tk.Frame(main_frame, bg=COLORS["bg"])
        right_frame.pack(side="right", fill="both", expand=True)

        self.setup_calendario(self.left_frame)
        self.setup_checklist(right_frame)

    def setup_calendario(self, parent=None):
        if parent is None:
            parent = self.root

        cal_card = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        cal_card.pack(fill="both", expand=True, padx=0, pady=0)

        header = tk.Frame(cal_card, bg=COLORS["surface"])
        header.pack(fill="x", pady=(4, 4), padx=6)

        StyledButton(header, text="◀", bg=COLORS["card"], hover_bg=COLORS["hover_soft"], command=self.mes_anterior, padx=8, pady=2).pack(side="left")

        self.lbl_mes = tk.Label(
            header,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["fg"],
            width=18,
            anchor="center",
        )
        self.lbl_mes.pack(side="left", padx=8, expand=True)

        StyledButton(header, text="▶", bg=COLORS["card"], hover_bg=COLORS["hover_soft"], command=self.mes_siguiente, padx=8, pady=2).pack(side="left")

        self.btn_lock = StyledButton(
            header,
            text="Login",
            bg=COLORS["danger"],
            hover_bg="#DC2626",
            command=self.toggle_login,
            padx=8,
            pady=2,
        )
        self.btn_lock.pack(side="right", padx=(8, 0))

        cal_container = tk.Frame(cal_card, bg=COLORS["surface"])
        cal_container.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        dias = ["DOM", "LUN", "MAR", "MIE", "JUE", "VIE", "SAB"]
        for i, d in enumerate(dias):
            tk.Label(
                cal_container,
                text=d,
                font=("Segoe UI", 8, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                anchor="center",
            ).grid(row=0, column=i, sticky="nsew", padx=2, pady=(0, 2))

        for col in range(7):
            cal_container.grid_columnconfigure(col, weight=1, uniform="cal_cols", minsize=44)
        cal_container.grid_rowconfigure(0, minsize=18, weight=0)
        for row in range(1, 7):
            cal_container.grid_rowconfigure(row, weight=1, uniform="cal_rows", minsize=30)

        self.dias_widgets = []
        for i in range(6):
            fila = []
            for j in range(7):
                cell = DayCell(cal_container, on_click=lambda di=i, dj=j: self.seleccionar_dia(di, dj))
                cell.grid(row=i + 1, column=j, padx=2, pady=2, sticky="nsew")
                fila.append(cell)
            self.dias_widgets.append(fila)

        self.render_calendario()

        self.info_box = tk.Frame(parent, bg=COLORS["bg"])
        self.info_box.pack(fill="x", padx=0, pady=(6, 0))
        self.actualizar_info_box()

    def render_calendario(self):
        primer_dia = (date(self.current_year, self.current_month, 1).weekday() + 1) % 7
        
        if self.current_month == 12:
            dias_mes = (date(self.current_year + 1, 1, 1) - date(self.current_year, 12, 1)).days
        else:
            dias_mes = (date(self.current_year, self.current_month + 1, 1) - date(self.current_year, self.current_month, 1)).days
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes.config(text=f"{meses[self.current_month-1]} {self.current_year}")

        hoy_str = datetime.now().strftime("%Y-%m-%d")

        for f in self.dias_widgets:
            for cell in f:
                cell.clear()

        dia_actual = 1
        for i in range(6):
            for j in range(7):
                if dia_actual <= dias_mes and (i > 0 or j >= primer_dia):
                    fecha_key = f"{self.current_year}-{self.current_month:02d}-{dia_actual:02d}"
                    cell = self.dias_widgets[i][j]
                    fill = COLORS["card"]
                    fg_color = COLORS["fg"]
                    if fecha_key in self.data.get("calendario", {}) and self.data["calendario"][fecha_key]:
                        hipo = self.data["calendario"][fecha_key]
                        fill = hipo_color(hipo)
                        fg_color = hipo_fg(hipo)
                    cell.set_day(dia_actual, fill, fg_color, today=(fecha_key == hoy_str))
                    dia_actual += 1

    def seleccionar_dia(self, fila, columna):
        if not self.admin_mode:
            messagebox.showwarning("Bloqueado", "Iniciá sesión para modificar el calendario")
            return
        
        texto = self.dias_widgets[fila][columna].text
        if not texto:
            return
        try:
            dia = int(texto)
        except:
            return
        fecha_key = f"{self.current_year}-{self.current_month:02d}-{dia:02d}"
        
        popup = tk.Toplevel(self.root)
        popup.title(f"Asignar - {dia}/{self.current_month}")
        popup.geometry("300x340")
        popup.resizable(False, False)
        popup.configure(bg=COLORS["bg"])

        card = tk.Frame(
            popup,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        card.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            card,
            text=f"{dia}/{self.current_month}/{self.current_year}",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["fg"],
        ).pack(pady=(8, 4))
        tk.Label(
            card,
            text="Elegí el hipódromo",
            font=("Segoe UI", 8),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
        ).pack(pady=(0, 10))

        for nombre, datos in HIPODROMOS.items():
            color = datos["color"]
            fg = hipo_fg(nombre)
            StyledButton(
                card,
                text=datos["nombre"],
                bg=color,
                fg=fg,
                hover_bg=color,
                command=lambda h=nombre, f=fecha_key: self.asignar_hipodromo(h, f, popup),
            ).pack(pady=5, fill="x", padx=28)

        StyledButton(
            card,
            text="BORRAR",
            bg="#6B7280",
            hover_bg="#4B5563",
            command=lambda: self.borrar_hipodromo(fecha_key, popup),
        ).pack(pady=(8, 8), fill="x", padx=28)

    def asignar_hipodromo(self, hipodromo, fecha_key, popup):
        if "calendario" not in self.data:
            self.data["calendario"] = {}
        self.data["calendario"][fecha_key] = hipodromo
        self.guardar_datos()
        self.render_calendario()
        self.actualizar_info_box()
        self.actualizar_info_paneles()
        popup.destroy()

    def borrar_hipodromo(self, fecha_key, popup):
        if fecha_key in self.data.get("calendario", {}):
            del self.data["calendario"][fecha_key]
            self.guardar_datos()
            self.render_calendario()
            self.actualizar_info_box()
            self.actualizar_info_paneles()
        popup.destroy()

    def mes_anterior(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.render_calendario()
        self.actualizar_info_box()

    def mes_siguiente(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.render_calendario()
        self.actualizar_info_box()

    def _chip_hipodromo(self, parent, etiqueta, hipo, side):
        asignado = hipo and hipo in HIPODROMOS
        color = hipo_color(hipo) if asignado else COLORS["border"]
        nombre = HIPODROMOS[hipo]["nombre"] if asignado else "Sin carrera"
        name_fg = color if asignado else COLORS["muted"]

        chip = tk.Frame(parent, bg=color)
        chip.pack(side=side, fill="both", expand=True, padx=4)
        accent = tk.Frame(chip, bg=color, height=4)
        accent.pack(fill="x")
        body = tk.Frame(chip, bg=COLORS["card"])
        body.pack(fill="both", expand=True)
        tk.Label(body, text=etiqueta, font=("Segoe UI", 8), bg=COLORS["card"], fg=COLORS["muted"], pady=2).pack(fill="x", padx=10)
        tk.Label(body, text=nombre, font=("Segoe UI", 12, "bold"), bg=COLORS["card"], fg=name_fg, pady=6).pack(fill="x", padx=10)

    def actualizar_info_box(self):
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")

        hipo_hoy = self.data.get("calendario", {}).get(fecha_hoy, "")
        hipo_manana = self.data.get("calendario", {}).get(manana, "")

        for w in self.info_box.winfo_children():
            w.destroy()

        self._chip_hipodromo(self.info_box, "HOY", hipo_hoy, "left")
        self._chip_hipodromo(self.info_box, "MAÑANA", hipo_manana, "right")

    def ir_hoy(self):
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.render_calendario()
    
    def toggle_login(self):
        if self.admin_mode:
            self.cerrar_sesion()
        else:
            self.mostrar_login()
    
    def actualizar_btn_login(self):
        if self.admin_mode:
            self.btn_lock.config(text="Cerrar")
            self.btn_lock.set_bg(COLORS["success"], hover_bg="#0D9F74")
        else:
            self.btn_lock.config(text="Login")
            self.btn_lock.set_bg(COLORS["danger"], hover_bg="#DC2626")
    
    def mostrar_login(self):
        if self.login_popup_abierto:
            return

        self.login_popup_abierto = True
        popup = tk.Toplevel(self.root)
        popup.title("Login Admin")
        popup.geometry("320x250")
        popup.resizable(False, False)
        popup.configure(bg=COLORS["bg"])
        popup.transient(self.root)

        card = tk.Frame(
            popup,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            card,
            text="LOGIN ADMIN",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["fg"],
        ).pack(pady=(8, 10))

        tk.Label(card, text="USUARIO", font=("Segoe UI", 8, "bold"), bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=14)
        user_wrap = tk.Frame(card, bg=COLORS["card"], highlightthickness=1, highlightbackground=COLORS["input_border"])
        user_wrap.pack(fill="x", padx=14, pady=(3, 10))
        entry_user = tk.Entry(
            user_wrap,
            font=("Segoe UI", 10),
            bg=COLORS["card"],
            fg=COLORS["fg"],
            insertbackground=COLORS["fg"],
            relief="flat",
            bd=0,
        )
        entry_user.pack(fill="x", ipady=5, padx=6)

        tk.Label(card, text="CLAVE", font=("Segoe UI", 8, "bold"), bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=14)
        pass_wrap = tk.Frame(card, bg=COLORS["card"], highlightthickness=1, highlightbackground=COLORS["input_border"])
        pass_wrap.pack(fill="x", padx=14, pady=(3, 14))
        entry_pass = tk.Entry(
            pass_wrap,
            font=("Segoe UI", 10),
            show="*",
            bg=COLORS["card"],
            fg=COLORS["fg"],
            insertbackground=COLORS["fg"],
            relief="flat",
            bd=0,
        )
        entry_pass.pack(fill="x", ipady=5, padx=6)

        def verificar_login():
            usuario = entry_user.get().strip()
            clave = entry_pass.get().strip()
            if usuario == "admin" and clave == "eze1":
                self.admin_mode = True
                self.login_popup_abierto = False
                self.actualizar_btn_login()
                self.render_calendario()
                popup.destroy()
                messagebox.showinfo("OK", "Sesión iniciada")
            else:
                messagebox.showerror("Error", "Usuario o clave incorrectos")

        def on_popup_close():
            self.login_popup_abierto = False
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", on_popup_close)
        popup.bind("<Return>", lambda _e: verificar_login())
        entry_user.bind("<Return>", lambda _e: entry_pass.focus_set())
        entry_pass.bind("<Return>", lambda _e: verificar_login())

        StyledButton(
            card,
            text="ENTRAR",
            bg=COLORS["success"],
            hover_bg="#0D9F74",
            command=verificar_login,
        ).pack(pady=(0, 8))

        entry_user.focus_set()
    
    def cerrar_sesion(self, popup=None):
        self.admin_mode = False
        self.actualizar_btn_login()
        self.render_calendario()
        if popup:
            popup.destroy()
        # Don't show messagebox to avoid blocking
    
    def show_cerrar_sesion(self):
        popup = tk.Toplevel(self.root)
        popup.title("Cerrar Sesión")
        popup.geometry("200x100")
        popup.configure(bg=COLORS["bg"])
        StyledButton(popup, text="CERRAR SESIÓN", bg="#EF4444", command=lambda: self.cerrar_sesion(popup)).pack(pady=20)

    def setup_checklist(self, parent=None):
        if parent is None:
            parent = self.root

        self.header_frame = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.header_frame.pack(fill="x", pady=(0, 4), padx=0)

        toggle_group = SegmentedGroup(self.header_frame)
        toggle_group.pack(side="left", padx=6, pady=4)

        self.btn_hoy = SegmentedButton(
            toggle_group,
            text="HOY",
            bg=COLORS["accent"],
            activebackground=COLORS["accent"],
            fg=COLORS["fg"],
            hover_bg=COLORS["hover_accent"],
            command=self.mostrar_panel_hoy
        )
        self.btn_hoy.pack(side="left")

        self.btn_manana = SegmentedButton(
            toggle_group,
            text="MAÑANA",
            bg=COLORS["card"],
            activebackground=COLORS["card"],
            fg=COLORS["muted"],
            hover_bg=COLORS["hover_soft"],
            command=self._on_btn_manana_click
        )
        self.btn_manana.config(state="normal")
        self.btn_manana.pack(side="left")

        self.panel_actual = "hoy"

        self.panel_hoy_frame = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.panel_manana_frame = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )

        self.setup_panel_individual(self.panel_hoy_frame, "hoy")
        self.setup_panel_individual(self.panel_manana_frame, "manana")

        self.panel_hoy_frame.pack(fill="both", expand=True)
        self.render_checklist_panel("hoy")
        self.panel_manana_frame.pack(fill="both", expand=True)
        self.panel_manana_frame.pack_forget()
        self.panel_actual = "hoy"
        self.btn_hoy.set_active(True)
        self.btn_manana.set_active(False)

    def setup_panel_individual(self, frame, tipo):
        accent_bar = tk.Frame(frame, bg=COLORS["border"], height=3)
        accent_bar.pack(fill="x")
        header = tk.Frame(frame, bg=COLORS["surface"])
        header.pack(fill="x", pady=4, padx=6)

        if tipo == "hoy":
            self.bar_hoy = accent_bar
            self.lbl_titulo_hoy = tk.Label(
                header,
                text="",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["muted"],
            )
            self.lbl_titulo_hoy.pack(side="left", padx=(0, 8))
            self.header_hoy = header

            self.modo_hoy_var = tk.StringVar(value="dia2")
            mode_group = SegmentedGroup(header)
            mode_group.pack(side="left")
            self.btn_modo_d1_hoy = SegmentedButton(
                mode_group,
                text="D1",
                bg=COLORS["card"],
                activebackground=COLORS["card"],
                fg=COLORS["muted"],
                hover_bg=COLORS["hover_soft"],
                command=lambda: self.set_mode_panel("hoy", "dia1")
            )
            self.btn_modo_d1_hoy.pack(side="left")
            self.btn_modo_d2_hoy = SegmentedButton(
                mode_group,
                text="D2",
                bg=COLORS["accent"],
                activebackground=COLORS["accent"],
                fg=COLORS["fg"],
                hover_bg=COLORS["hover_accent"],
                command=lambda: self.set_mode_panel("hoy", "dia2")
            )
            self.btn_modo_d2_hoy.pack(side="left")

            self.btn_guardar_hoy = StyledButton(
                header,
                text="GUARDAR",
                bg=COLORS["success"],
                hover_bg="#0D9F74",
                command=lambda: self.guardar_checklist_panel("hoy"),
            )
            self.btn_guardar_hoy.pack(side="right")

            self.check_vars_hoy = {}
            self.checklist_frame_hoy = self.crear_checklist_frame(frame)
        else:
            self.bar_manana = accent_bar
            self.lbl_titulo_manana = tk.Label(
                header,
                text="",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["muted"],
            )
            self.lbl_titulo_manana.pack(side="left", padx=(0, 8))
            self.header_manana = header

            self.modo_manana_var = tk.StringVar(value="dia1")
            mode_group = SegmentedGroup(header)
            mode_group.pack(side="left")
            self.btn_modo_d1_manana = SegmentedButton(
                mode_group,
                text="D1",
                bg=COLORS["accent"],
                activebackground=COLORS["accent"],
                fg=COLORS["fg"],
                hover_bg=COLORS["hover_accent"],
                command=lambda: self.set_mode_panel("manana", "dia1")
            )
            self.btn_modo_d1_manana.pack(side="left")
            self.btn_modo_d2_manana = SegmentedButton(
                mode_group,
                text="D2",
                bg=COLORS["card"],
                activebackground=COLORS["card"],
                fg=COLORS["muted"],
                hover_bg=COLORS["hover_soft"],
                command=lambda: self.set_mode_panel("manana", "dia2")
            )
            self.btn_modo_d2_manana.pack(side="left")
            self.btn_modo_d2_manana.set_enabled(False)

            self.btn_guardar_manana = StyledButton(
                header,
                text="GUARDAR",
                bg=COLORS["success"],
                hover_bg="#0D9F74",
                command=lambda: self.guardar_checklist_panel("manana"),
            )
            self.btn_guardar_manana.pack(side="right")

            self.check_vars_manana = {}
            self.checklist_frame_manana = self.crear_checklist_frame(frame)

        self.update_mode_toggle(tipo)

    def crear_checklist_frame(self, parent):
        container = tk.Frame(parent, bg=COLORS["surface"])
        container.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        frame = tk.Frame(container, bg=COLORS["surface"])
        frame.pack(fill="both", expand=True)
        return frame

    def mostrar_panel_hoy(self):
        self.panel_actual = "hoy"
        self.btn_hoy.set_active(True)
        self.btn_manana.set_active(False)
        self.panel_manana_frame.pack_forget()
        self.panel_hoy_frame.pack(fill="both", expand=True)
        self.render_checklist_panel("hoy")

    def _on_btn_manana_click(self):
        self.mostrar_panel_manana()

    def mostrar_panel_manana(self):
        self.panel_actual = "manana"
        self.btn_hoy.set_active(False)
        self.btn_manana.set_active(True)
        self.panel_hoy_frame.pack_forget()
        self.panel_manana_frame.pack(fill="both", expand=True)
        self.render_checklist_panel("manana", force=True)

    def actualizar_info_paneles(self):
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")

        hipo_hoy = self.data.get("calendario", {}).get(fecha_hoy, "")
        hipo_manana = self.data.get("calendario", {}).get(manana, "")

        if hipo_hoy and hipo_hoy in HIPODROMOS:
            nombre = HIPODROMOS[hipo_hoy]["nombre"]
            color = HIPODROMOS[hipo_hoy]["color"]
            self.lbl_titulo_hoy.config(text=nombre, fg=color, bg=COLORS["surface"])
            self.bar_hoy.configure(bg=color)
            self.panel_hoy_frame.configure(bg=COLORS["surface"])
            if hasattr(self, "header_hoy"):
                self.header_hoy.configure(bg=COLORS["surface"])
            self.btn_hoy.set_accent(color, hipo_fg(hipo_hoy))
            self.btn_modo_d1_hoy.set_accent(color, hipo_fg(hipo_hoy))
            self.btn_modo_d2_hoy.set_accent(color, hipo_fg(hipo_hoy))
        else:
            self.lbl_titulo_hoy.config(text="Sin carrera", fg=COLORS["muted"], bg=COLORS["surface"])
            self.bar_hoy.configure(bg=COLORS["border"])
            self.panel_hoy_frame.configure(bg=COLORS["surface"])
            if hasattr(self, "header_hoy"):
                self.header_hoy.configure(bg=COLORS["surface"])
            self.btn_hoy.set_accent(COLORS["accent"], COLORS["fg"])
            self.btn_modo_d1_hoy.set_accent(COLORS["accent"], COLORS["fg"])
            self.btn_modo_d2_hoy.set_accent(COLORS["accent"], COLORS["fg"])

        if hipo_manana and hipo_manana in HIPODROMOS:
            nombre = HIPODROMOS[hipo_manana]["nombre"]
            color = HIPODROMOS[hipo_manana]["color"]
            self.lbl_titulo_manana.config(text=nombre, fg=color, bg=COLORS["surface"])
            self.bar_manana.configure(bg=color)
            self.panel_manana_frame.configure(bg=COLORS["surface"])
            if hasattr(self, "header_manana"):
                self.header_manana.configure(bg=COLORS["surface"])
            self.btn_manana.set_accent(color, hipo_fg(hipo_manana))
            self.btn_modo_d1_manana.set_accent(color, hipo_fg(hipo_manana))
            self.btn_modo_d2_manana.set_accent(color, hipo_fg(hipo_manana))
        else:
            self.lbl_titulo_manana.config(text="Sin carrera", fg=COLORS["muted"], bg=COLORS["surface"])
            self.bar_manana.configure(bg=COLORS["border"])
            self.panel_manana_frame.configure(bg=COLORS["surface"])
            if hasattr(self, "header_manana"):
                self.header_manana.configure(bg=COLORS["surface"])
            self.btn_manana.set_accent(COLORS["accent"], COLORS["fg"])
            self.btn_modo_d1_manana.set_accent(COLORS["accent"], COLORS["fg"])
            self.btn_modo_d2_manana.set_accent(COLORS["accent"], COLORS["fg"])

        estado_hoy = self.data.get("estado", {}).get(fecha_hoy, "")
        estado_manana = self.data.get("estado", {}).get(manana, "")

        self.set_mode_d2_enabled("hoy", estado_hoy in ("dia1_completado", "completo"))
        self.set_mode_d2_enabled("manana", estado_manana in ("dia1_completado", "completo"))

        if estado_hoy in ("dia1_completado", "completo") and self.modo_hoy_var.get() == "dia1":
            self.modo_hoy_var.set("dia2")
        if estado_manana in ("dia1_completado", "completo") and self.modo_manana_var.get() == "dia1":
            self.modo_manana_var.set("dia2")

        self.btn_hoy.set_active(self.panel_actual == "hoy")
        self.btn_manana.set_active(self.panel_actual == "manana")
        self.update_mode_toggle("hoy")
        self.update_mode_toggle("manana")

    def set_mode_panel(self, panel, modo):
        """
        Cambia el modo (D1/D2) del panel especificado.
        Args:
            panel: "hoy" o "manana"
            modo: "dia1" o "dia2"
        FIX: Ahora siempre renderiza el panel indicado (antes solo renderizaba HOY)
        """
        if panel == "hoy":
            self.modo_hoy_var.set(modo)
        else:
            self.modo_manana_var.set(modo)
        self.update_mode_toggle(panel)
        self.render_checklist_panel(panel)

    def set_mode_d2_enabled(self, panel, enabled):
        if panel == "hoy":
            self.btn_modo_d2_hoy.set_enabled(enabled)
            if not enabled and self.modo_hoy_var.get() == "dia2":
                self.modo_hoy_var.set("dia1")
            self.update_mode_toggle("hoy")
        else:
            self.btn_modo_d2_manana.set_enabled(enabled)
            if not enabled and self.modo_manana_var.get() == "dia2":
                self.modo_manana_var.set("dia1")
            self.update_mode_toggle("manana")

    def update_mode_toggle(self, panel):
        if panel == "hoy":
            self.btn_modo_d1_hoy.set_active(self.modo_hoy_var.get() == "dia1")
            self.btn_modo_d2_hoy.set_active(self.modo_hoy_var.get() == "dia2")
        else:
            self.btn_modo_d1_manana.set_active(self.modo_manana_var.get() == "dia1")
            self.btn_modo_d2_manana.set_active(self.modo_manana_var.get() == "dia2")

    def _crear_fila_check(self, parent, item, check_vars, hipo, accent, mark_fg, is_setear, wrap_len):
        var = tk.BooleanVar(value=False)
        check_vars[item] = var
        row_bg = hipo_checked(hipo) if hipo in HIPODROMOS else COLORS["row"]
        text_fg = hipo_fg(hipo) if hipo in HIPODROMOS else COLORS["fg"]
        checked_bg = hipo_color(hipo) if hipo in HIPODROMOS else COLORS["row_hover"]

        frame_item = tk.Frame(parent, bg=row_bg, cursor="hand2")
        bar = tk.Frame(frame_item, bg=accent, width=4, cursor="hand2")
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        inner = tk.Frame(frame_item, bg=row_bg, cursor="hand2")
        inner.pack(side="left", fill="both", expand=True, padx=5, pady=2)

        mark = CheckMark(inner, var, accent, mark_fg=mark_fg, bg=row_bg)
        mark.pack(side="left", padx=(0, 6))

        labels = []
        if is_setear:
            hipo_nombre = HIPODROMOS.get(hipo, {}).get("nombre", "SIN ASIGNAR")
            label_setear = tk.Label(
                inner,
                text="SETEAR CATEGORIA  ·",
                font=("Segoe UI", 8, "bold"),
                bg=row_bg,
                fg=text_fg,
                cursor="hand2",
            )
            label_setear.pack(side="left", padx=(0, 4))
            label_alerta = tk.Label(
                inner,
                text=hipo_nombre,
                font=("Segoe UI", 11, "bold"),
                bg=row_bg,
                fg="#FF0000",
                cursor="hand2",
            )
            label_alerta.pack(side="left")
            labels.extend([label_setear, label_alerta])

            blink_idx = [0]

            def blink_loop():
                if not label_alerta.winfo_exists():
                    return
                label_alerta.config(fg=["#FF0000", "#FFFFFF"][blink_idx[0] % 2])
                blink_idx[0] = (blink_idx[0] + 1) % 2
                label_alerta.after(600, blink_loop)

            blink_loop()
        else:
            lbl = tk.Label(
                inner,
                text=item,
                font=("Segoe UI", 8, "bold"),
                bg=row_bg,
                fg=text_fg,
                anchor="w",
                justify="left",
                wraplength=wrap_len,
                cursor="hand2",
            )
            lbl.pack(side="left", fill="x", expand=True)
            labels.append(lbl)

        def paint(bg):
            frame_item.configure(bg=bg)
            inner.configure(bg=bg)
            mark.set_bg(bg)
            for lab in labels:
                lab.configure(bg=bg)

        def on_toggle(*_args):
            paint(checked_bg if var.get() else row_bg)

        def toggle(_event=None):
            var.set(not var.get())
            return "break"

        var.trace_add("write", on_toggle)

        for widget in (frame_item, bar, inner, *labels):
            widget.bind("<Button-1>", toggle)

        return frame_item

    def render_checklist_panel(self, panel, force=False):
        """
        Renderiza el panel de checklist (HOY o MAÑANA).
        
        Args:
            panel: "hoy" o "manana"
            force: if True, fuerza el re-render aunque ya esté renderizado
        
        Esta función:
        1. Limpia los trace callbacks anteriores de los BooleanVars
        2. Destruye todos los widgets de checkboxes existentes
        3. Crea nuevos checkboxes basados en la fecha y modo (dia1/dia2)
        
        IMPORTANTE: No agregar lógica adicional de trace o callbacks aquí
        que pueda causar rerenderizado automático, ya que cela causa
        que los checkboxes pierdan su estado al hacer click.
        """
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")

        if panel == "hoy":
            fecha_key = fecha_hoy
            modo = self.modo_hoy_var.get()
            frame = self.checklist_frame_hoy
            check_vars = self.check_vars_hoy
        else:
            fecha_key = manana
            modo = self.modo_manana_var.get()
            frame = self.checklist_frame_manana
            check_vars = self.check_vars_manana

        if check_vars:
            print(f"CHECK_VARS panel={panel} count={len(check_vars)}")
        
        for item, var in list(check_vars.items()):
            try:
                for cb_id in var.trace_info():
                    var.trace_remove("write", cb_id)
            except Exception:
                pass
        check_vars.clear()

        for w in frame.winfo_children():
            w.destroy()
        self.update_mode_toggle(panel)
        estado_fecha = self.data.get("estado", {}).get(fecha_key, "")

        if estado_fecha == "completo":
            self.mostrar_pantalla_completado(panel)
            return

        if modo == "dia1" and estado_fecha in ("dia1_completado", "completo"):
            for w in frame.winfo_children():
                w.destroy()

            box = tk.Frame(frame, bg=COLORS["card"])
            box.pack(fill="x", padx=12, pady=10)
            tk.Frame(box, bg=COLORS["success"], height=3).pack(fill="x")
            tk.Label(
                box,
                text="Día 1 completado",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["card"],
                fg=COLORS["success"],
                pady=6,
            ).pack()
            tk.Label(
                box,
                text="D2 habilitado. Continuá con Día 2.",
                font=("Segoe UI", 8),
                bg=COLORS["card"],
                fg=COLORS["fg"],
                pady=2,
            ).pack()
            StyledButton(
                box,
                text="Ir a D2",
                bg=COLORS["accent"],
                hover_bg=COLORS["hover_accent"],
                command=lambda p=panel: self.set_mode_panel(p, "dia2"),
            ).pack(pady=(4, 10))
            return
        
        if modo == "dia1":
            items = CHECKLIST_DIA1
        else:
            hipo = self.data.get("calendario", {}).get(fecha_key, "")
            items = CHECKLIST_DIA2_POR_HIPODROMO.get(hipo, [])
            if hipo not in ("Sin hipodromo",) and not items:
                items = CHECKLIST_DIA2_SAN_ISIDRO
        
        hipo = self.data.get("calendario", {}).get(fecha_key, "")
        accent = hipo_color(hipo, COLORS["accent"])
        mark_fg = hipo_fg(hipo) if hipo in HIPODROMOS else "white"

        for w in frame.winfo_children():
            w.destroy()

        if not items:
            tk.Label(
                frame,
                text="Sin hipódromo: no hay checklist de Día 2.",
                font=("Segoe UI", 9),
                bg=COLORS["surface"],
                fg=COLORS["muted"],
            ).pack(pady=16)
            return

        container = frame.master
        container.update_idletasks()
        frame.update_idletasks()
        cols = 2
        wrap_len = 180
        row_items = {}
        max_items = 14
        row_count = max(1, (max_items + cols - 1) // cols)

        for r in range(0, 20):
            frame.rowconfigure(r, weight=0, minsize=0)

        for idx, item in enumerate(items):
            row = idx % row_count
            col = idx // row_count
            is_setear = modo == "dia2" and item == "SETEAR CATEGORIA"
            frame_item = self._crear_fila_check(frame, item, check_vars, hipo, accent, mark_fg, is_setear, wrap_len)
            frame_item.grid(row=row, column=col, sticky="nsew", pady=1, padx=2)
            row_items.setdefault(row, []).append(frame_item)
            frame.update_idletasks()

        for row, row_frames in row_items.items():
            target_height = 32
            frame.rowconfigure(row, weight=1, minsize=target_height)
            for item_frame in row_frames:
                item_frame.grid_propagate(False)
                item_frame.configure(height=target_height)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def guardar_checklist_panel(self, panel):
        """
        Guarda el checklist del panel especificado.
        Valida que todos los items estén completados antes de guardar.

        Fix: Se agregaron llamadas a actualizar_info_paneles() y render_checklist_panel()
        para asegurar que la UI se actualice correctamente después de guardar.
        """
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")

        if panel == "hoy":
            fecha_key = fecha_hoy
            modo = self.modo_hoy_var.get()
            check_vars = self.check_vars_hoy
            target_panel = "hoy"
        else:
            fecha_key = manana
            modo = self.modo_manana_var.get()
            check_vars = self.check_vars_manana
            target_panel = "manana"

        if "checklist" not in self.data:
            self.data["checklist"] = {}
        if fecha_key not in self.data["checklist"]:
            self.data["checklist"][fecha_key] = {}

        items_guardados = 0
        total_items = len(check_vars)

        for item, var in check_vars.items():
            estado_check = var.get()
            self.data["checklist"][fecha_key][item] = estado_check
            if estado_check:
                items_guardados += 1

        all_checked = items_guardados == total_items and total_items > 0

        if not all_checked:
            messagebox.showwarning("Incompleto", f"Completá todos los items ({items_guardados}/{total_items})")
            return

        if "estado" not in self.data:
            self.data["estado"] = {}

        estado_actual = self.data["estado"].get(fecha_key, "")
        if modo == "dia2" and estado_actual not in ("dia1_completado", "completo"):
            messagebox.showwarning("Bloqueado", "Primero completá y guardá DIA 1 para habilitar DIA 2.")
            return

        if modo == "dia1":
            # Guardar estado como "dia1_completado" y cambiar automáticamente a D2
            self.data["estado"][fecha_key] = "dia1_completado"
            self.set_mode_d2_enabled(target_panel, True)
            self.guardar_datos()
            self.limpiar_datos_antiguos()
            # FIX: Actualizar paneles para que se habilite D2 correctamente
            self.actualizar_info_paneles()
            self.root.update_idletasks()
            self.set_mode_panel(target_panel, "dia2")
            self.render_checklist_panel(target_panel)
            self.root.update_idletasks()
            messagebox.showinfo("Guardado", f"Día 1 completado!\n({items_guardados}/{total_items})\nAhora completá Día 2.")
        else:
            # Guardar estado como "completo" y mostrar pantalla de completado
            self.data["estado"][fecha_key] = "completo"
            self.guardar_datos()
            self.limpiar_datos_antiguos()
            self.actualizar_info_paneles()
            self.mostrar_pantalla_completado(panel)
            self.root.update_idletasks()

    def limpiar_datos_antiguos(self):
        from datetime import timedelta
        hoy = datetime.now()
        fecha_limite = (hoy - timedelta(days=2)).strftime("%Y-%m-%d")
        hubo_borrados = False
        
        if "checklist" in self.data:
            fechas_a_borrar = [f for f in self.data["checklist"].keys() if f < fecha_limite]
            for f in fechas_a_borrar:
                del self.data["checklist"][f]
                hubo_borrados = True
        
        if "estado" in self.data:
            fechas_a_borrar = [f for f in self.data["estado"].keys() if f < fecha_limite]
            for f in fechas_a_borrar:
                del self.data["estado"][f]
                hubo_borrados = True
        
        if hubo_borrados:
            self.guardar_datos()

    def mostrar_pantalla_completado(self, panel):
        if panel == "hoy":
            frame = self.checklist_frame_hoy
        else:
            frame = self.checklist_frame_manana

        for w in frame.winfo_children():
            w.destroy()

        container = tk.Frame(frame, bg=COLORS["card"])
        container.pack(fill="x", padx=12, pady=10)
        tk.Frame(container, bg=COLORS["success"], height=3).pack(fill="x")

        tk.Label(
            container,
            text="Checklist completo",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["card"],
            fg=COLORS["success"],
        ).pack(pady=(8, 2))

        tk.Label(
            container,
            text="Guardá el PDF, previsualizá para imprimir o reiniciá.",
            font=("Segoe UI", 8),
            bg=COLORS["card"],
            fg=COLORS["muted"],
        ).pack(pady=(0, 6))

        btn_frame = tk.Frame(container, bg=COLORS["card"])
        btn_frame.pack(pady=(0, 8))

        StyledButton(
            btn_frame,
            text="Imprimir",
            bg=COLORS["success"],
            hover_bg="#0D9F74",
            command=lambda: self.imprimir_directo_panel(panel),
        ).pack(side="left", padx=4)

        StyledButton(
            btn_frame,
            text="Guardar PDF",
            bg=COLORS["info"],
            hover_bg="#0891B2",
            command=lambda: self.guardar_pdf_panel(panel),
        ).pack(side="left", padx=4)

        StyledButton(
            btn_frame,
            text="Reiniciar",
            bg=COLORS["danger"],
            hover_bg="#DC2626",
            command=lambda: self.reiniciar_panel(panel),
        ).pack(side="left", padx=4)

    def reiniciar_panel(self, panel):
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")
        
        if panel == "hoy":
            fecha_key = fecha_hoy
            frame = self.checklist_frame_hoy
            check_vars = self.check_vars_hoy
        else:
            fecha_key = manana
            frame = self.checklist_frame_manana
            check_vars = self.check_vars_manana
        
        if hasattr(frame, 'checkboxes_inicializados'):
            frame.checkboxes_inicializados = False
        
        for w in frame.winfo_children():
            w.destroy()
        
        if panel == "hoy":
            self.modo_hoy_var.set("dia1")
        else:
            self.modo_manana_var.set("dia1")
        
        if panel == "hoy":
            self.btn_modo_d2_hoy.set_enabled(False)
        else:
            self.btn_modo_d2_manana.set_enabled(False)
        
        if "checklist" in self.data and fecha_key in self.data["checklist"]:
            del self.data["checklist"][fecha_key]
        
        if "estado" in self.data and fecha_key in self.data["estado"]:
            del self.data["estado"][fecha_key]
        
        self.guardar_datos()
        
        if panel == "hoy":
            self.btn_hoy.set_active(True)
            self.btn_manana.set_active(False)
            self.btn_manana.set_enabled(True)
            self.panel_hoy_frame.pack(fill="both", expand=True)
        else:
            self.btn_hoy.set_active(False)
            self.btn_manana.set_active(True)
            self.panel_manana_frame.pack(fill="both", expand=True)

    def _datos_panel(self, panel):
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")
        if panel == "hoy":
            return fecha_hoy, "HOY"
        return manana, "MAÑANA"

    def guardar_pdf_panel(self, panel):
        fecha_key, _titulo = self._datos_panel(panel)
        hipodromo = self.data.get("calendario", {}).get(fecha_key, "No asignado")
        nombre_archivo = f"Checklist_{hipodromo.replace(' ', '_')}_{fecha_key}.pdf"
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=nombre_archivo)
        if not archivo:
            return
        self._generar_pdf(panel, archivo)
        messagebox.showinfo("PDF", f"PDF guardado: {archivo}")

    def imprimir_directo_panel(self, panel):
        fecha_key, _titulo = self._datos_panel(panel)
        hipodromo = self.data.get("calendario", {}).get(fecha_key, "No asignado")
        archivo = os.path.join(tempfile.gettempdir(), f"Checklist_{hipodromo.replace(' ', '_')}_{fecha_key}.pdf")
        self._generar_pdf(panel, archivo)
        try:
            os.startfile(archivo)
        except OSError:
            messagebox.showerror("Imprimir", "No se pudo abrir la vista previa. Probá Guardar PDF.")

    def imprimir_pdf_panel(self, panel):
        self.guardar_pdf_panel(panel)

    def _generar_pdf(self, panel, archivo):
        fecha_key, _titulo = self._datos_panel(panel)
        hipodromo = self.data.get("calendario", {}).get(fecha_key, "No asignado")

        doc = SimpleDocTemplate(archivo, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        hipo = self.data.get("calendario", {}).get(fecha_key, "")
        hipo_data = HIPODROMOS.get(hipo, {})
        hipo_color_hex = hipo_data.get("color", "#374151")
        hipo_color = colors.HexColor(hipo_color_hex)
        header_fg = colors.white if hipo != "Palermo" else colors.black

        title_style = ParagraphStyle(
            "TitleModern",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=hipo_color,
            spaceAfter=8,
        )
        subtitle_style = ParagraphStyle(
            "SubtitleModern",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=8,
        )
        status_ok_style = ParagraphStyle(
            "StatusOk",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#047857"),
            spaceBefore=10,
        )
        status_bad_style = ParagraphStyle(
            "StatusBad",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#B91C1C"),
            spaceBefore=10,
        )

        titulo = Paragraph(f"CHECKLIST - {hipodromo.upper()}", title_style)
        story.append(titulo)
        story.append(Spacer(1, 6))

        fecha_display = f"{fecha_key[8:10]}/{fecha_key[5:7]}/{fecha_key[0:4]}"
        fecha_par = Paragraph(f"Fecha: {fecha_display}", subtitle_style)
        story.append(fecha_par)
        story.append(Spacer(1, 10))

        items_d1 = CHECKLIST_DIA1
        items_d2 = CHECKLIST_DIA2_POR_HIPODROMO.get(hipo, [])
        if hipo != "Sin hipodromo" and not items_d2:
            items_d2 = CHECKLIST_DIA2_SAN_ISIDRO

        def build_inner_table(title, items):
            data = [[title, "", ""]]
            data.append(["#", "Item", "Estado"])
            for i, item in enumerate(items, 1):
                checked = self.data.get("checklist", {}).get(fecha_key, {}).get(item, False)
                estado = "✓" if checked else "✗"
                data.append([i, item, estado])
            col_w = [16, 186, 40]
            t = Table(data, colWidths=col_w)
            t.setStyle(TableStyle([
                ("SPAN", (0, 0), (-1, 0)),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, 1), hipo_color),
                ("TEXTCOLOR", (0, 0), (-1, 1), header_fg),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, 1), 8),
                ("FONTSIZE", (0, 2), (-1, -1), 7.5),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F1F5F9")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            return t

        t_d1 = build_inner_table("DÍA 1 (PRE-CARRERA)", items_d1)
        t_d2 = build_inner_table("DÍA 2 (CARRERA)", items_d2)

        # PDF en 1 hoja: D1 y D2 lado a lado en tabla wrapper de 2 columnas
        wrapper = Table([[t_d1, t_d2]], colWidths=[242, 242])
        wrapper.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 10),
            ("LEFTPADDING", (1, 0), (1, 0), 10),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(wrapper)

        estado = self.data.get("estado", {}).get(fecha_key, "")
        if estado == "completo":
            story.append(Paragraph("✓ REUNIÓN COMPLETADA", status_ok_style))
        else:
            story.append(Paragraph("✗ REUNIÓN INCOMPLETA", status_bad_style))

        doc.build(story)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()