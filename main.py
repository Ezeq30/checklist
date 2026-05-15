import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json
import os

HIPODROMOS = {
    "San isidro": {"color": "#2E7D32", "nombre": "SAN ISIDRO"},
    "La plata": {"color": "#1565C0", "nombre": "LA PLATA"},
    "Palermo": {"color": "#F9A825", "nombre": "PALERMO"}
}

COLORS = {
    "bg": "#111827",
    "fg": "#F9FAFB",
    "accent": "#8B5CF6",
    "card": "#1F2937",
    "card_soft": "#273449",
    "surface": "#0F172A",
    "border": "#334155",
    "hover_soft": "#334155",
    "hover_accent": "#7C3AED",
    "muted": "#9CA3AF",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#06B6D4"
}

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
    "INICIAR APP MOBILE",
    "CANAL 26 ASIGNACION 29",
    "CONFIRMAR GENERACION DE ARCHIVO DETALLE",
    "CARGAR EL VIDEO EN LA APP MOBILE",
    "SETEAR VIDEOS POR MEET"
]

CHECKLIST_DIA2_LA_PLATA = [
    "SETEAR CATEGORIA",
    "VOLVER A REVISAR EL PROGRAMA Y POSTING",
    "CAMBIAR EN LAS VENTANILLAS LOS AGENTES QUE CORRESPONDAN",
    "BLOQUEAR / DESBLOQUEAR AGENTES",
    "PONER TIPS EN SERVICIO",
    "PONER TERMINALES EN SERVICIO",
    "RESETEAR TERMINALES",
    "ABRIR LA VENTA A LA HORA INDICADA",
    "INICIAR APP MOBILE",
    "CARGAR EL VIDEO EN LA APP MOBILE",
    "SETEAR VIDEOS POR MEET"
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

import sys
import os

if getattr(sys, 'frozen', False):
    exec_dir = os.path.dirname(sys.executable)
else:
    exec_dir = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(exec_dir, "data.json")

class StyledButton(tk.Button):
    def __init__(self, master, **kwargs):
        bg = kwargs.pop("bg", COLORS["accent"])
        fg = kwargs.pop("fg", "white")
        hover_bg = kwargs.pop("hover_bg", COLORS["hover_soft"])
        super().__init__(
            master,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            **kwargs
        )
        self._base_bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        self.config(cursor="hand2", bg=self._hover_bg, activebackground=self._hover_bg)

    def _on_leave(self, _event):
        self.config(cursor="", bg=self._base_bg, activebackground=self._base_bg)


class SegmentedButton(tk.Button):
    def __init__(self, master, **kwargs):
        hover_bg = kwargs.pop("hover_bg", COLORS["hover_soft"])
        super().__init__(
            master,
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            font=("Segoe UI", 8, "bold"),
            activeforeground=COLORS["fg"],
            **kwargs
        )
        self._base_bg = self.cget("bg")
        self._hover_bg = hover_bg
        self._enabled = True
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_active(self, active):
        if not self._enabled:
            self._base_bg = COLORS["card"]
            self.config(bg=COLORS["card"], fg=COLORS["muted"], activebackground=COLORS["card"], state="disabled")
            return
        if active:
            self._base_bg = COLORS["accent"]
            self.config(bg=COLORS["accent"], fg=COLORS["fg"], activebackground=COLORS["accent"], state="normal")
        else:
            self._base_bg = COLORS["card"]
            self.config(bg=COLORS["card"], fg=COLORS["muted"], activebackground=COLORS["card"], state="normal")

    def set_enabled(self, enabled):
        self._enabled = enabled
        state = "normal" if enabled else "disabled"
        fg = COLORS["fg"] if enabled else COLORS["muted"]
        self.config(state=state, fg=fg)
        if not enabled:
            self._base_bg = COLORS["card"]
            self.config(bg=COLORS["card"], activebackground=COLORS["card"])

    def _on_enter(self, _event):
        if not self._enabled:
            return
        self.config(cursor="hand2")
        if self.cget("bg") != COLORS["accent"]:
            self.config(bg=self._hover_bg, activebackground=self._hover_bg, fg=COLORS["fg"])

    def _on_leave(self, _event):
        self.config(cursor="")
        self.config(bg=self._base_bg, activebackground=self._base_bg)

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Checklist Hipodromos")
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
        self.day_default_styles = {}

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
        
        self.left_frame = tk.Frame(main_frame, bg=COLORS["bg"])
        self.left_frame.pack(side="left", fill="both", expand=False, padx=(0, 6))
        
        right_frame = tk.Frame(main_frame, bg=COLORS["bg"])
        right_frame.pack(side="right", fill="both", expand=True, padx=0)
        
        self.setup_calendario(self.left_frame)
        self.setup_checklist(right_frame)

    def setup_calendario(self, parent=None):
        if parent is None:
            parent = self.root
        
        header = tk.Frame(parent, bg=COLORS["bg"])
        header.pack(fill="x", pady=(2, 6), padx=6)
        
        StyledButton(header, text="◀", bg="#374151", command=self.mes_anterior).pack(side="left", padx=3)
        
        self.lbl_mes = tk.Label(
            header,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["fg"],
            width=18,
            anchor="center",
        )
        self.lbl_mes.pack(side="left", padx=10)
        
        StyledButton(header, text="▶", bg="#374151", command=self.mes_siguiente).pack(side="left", padx=3)
        
        self.btn_lock = StyledButton(header, text="🔓", bg=COLORS["danger"], command=self.toggle_login)
        self.btn_lock.pack(side="right", padx=8)

        cal_container = tk.Frame(parent, bg=COLORS["bg"])
        cal_container.pack(fill="both", expand=True, padx=6, pady=2)
        
        dias = ["DOM", "LUN", "MAR", "MIE", "JUE", "VIE", "SAB"]
        for i, d in enumerate(dias):
            tk.Label(cal_container, text=d, font=("Segoe UI", 8, "bold"), bg=COLORS["bg"], fg=COLORS["muted"], width=6).grid(row=0, column=i, pady=2)

        # Keep calendar grid spacing uniform across all columns/rows.
        for col in range(7):
            cal_container.grid_columnconfigure(col, weight=1, uniform="calendar_cols", minsize=50)
        cal_container.grid_rowconfigure(0, minsize=22)
        for row in range(1, 7):
            cal_container.grid_rowconfigure(row, weight=1, uniform="calendar_rows", minsize=36)

        self.dias_widgets = []
        for i in range(6):
            fila = []
            for j in range(7):
                btn = self._crear_boton_dia(cal_container, i, j)
                btn.grid(row=i+1, column=j, padx=1, pady=1, sticky="nsew")
                fila.append(btn)
            self.dias_widgets.append(fila)
        
        self.render_calendario()
        
        self.info_box = tk.Frame(parent, bg=COLORS["card"])
        self.info_box.pack(fill="x", padx=6, pady=(4, 2))
        self.actualizar_info_box()

    def _crear_boton_dia(self, parent, i, j):
        btn = tk.Button(
            parent,
            text="",
            font=("Segoe UI", 8, "bold"),
            bg=COLORS["card"],
            fg=COLORS["fg"],
            activebackground=COLORS["hover_soft"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            command=lambda di=i, dj=j: self.seleccionar_dia(di, dj),
        )
        btn.bind("<Enter>", lambda _e, b=btn: self._on_day_enter(b))
        btn.bind("<Leave>", lambda _e, b=btn: self._on_day_leave(b))
        return btn

    def _on_day_enter(self, btn):
        if btn.cget("text"):
            btn.config(cursor="hand2")
            default_bg = self.day_default_styles.get(btn, {}).get("bg", COLORS["card"])
            if btn.cget("bg") == default_bg:
                btn.config(bg=COLORS["hover_soft"], activebackground=COLORS["hover_soft"])

    def _on_day_leave(self, btn):
        style = self.day_default_styles.get(btn)
        btn.config(cursor="")
        if style:
            btn.config(bg=style["bg"], fg=style["fg"], relief=style["relief"], bd=style["bd"], highlightbackground=style["border"])

    def render_calendario(self):
        primer_dia = (date(self.current_year, self.current_month, 1).weekday() + 1) % 7
        
        if self.current_month == 12:
            dias_mes = (date(self.current_year + 1, 1, 1) - date(self.current_year, 12, 1)).days
        else:
            dias_mes = (date(self.current_year, self.current_month + 1, 1) - date(self.current_year, self.current_month, 1)).days
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes.config(text=f"{meses[self.current_month-1].upper()} {self.current_year}")

        hoy_str = datetime.now().strftime("%Y-%m-%d")

        for f in self.dias_widgets:
            for b in f:
                b.config(
                    text="",
                    bg=COLORS["card"],
                    fg=COLORS["fg"],
                    relief="flat",
                    bd=0,
                    cursor="",
                    activebackground=COLORS["hover_soft"],
                    highlightbackground=COLORS["border"],
                )
                self.day_default_styles[b] = {
                    "bg": COLORS["card"],
                    "fg": COLORS["fg"],
                    "relief": "flat",
                    "bd": 0,
                    "border": COLORS["border"],
                }

        dia_actual = 1
        for i in range(6):
            for j in range(7):
                if dia_actual <= dias_mes and (i > 0 or j >= primer_dia):
                    fecha_key = f"{self.current_year}-{self.current_month:02d}-{dia_actual:02d}"
                    self.dias_widgets[i][j].config(text=f"{dia_actual}")
                    
                    if fecha_key in self.data.get("calendario", {}) and self.data["calendario"][fecha_key]:
                        hipo = self.data["calendario"][fecha_key]
                        color = HIPODROMOS.get(hipo, {}).get("color", COLORS["card"])
                        fg_color = "white" if hipo != "Palermo" else "black"
                        self.dias_widgets[i][j].config(bg=color, fg=fg_color)
                        self.day_default_styles[self.dias_widgets[i][j]] = {
                            "bg": color,
                            "fg": fg_color,
                            "relief": "flat",
                            "bd": 0,
                            "border": COLORS["border"],
                        }
                    
                    if fecha_key == hoy_str:
                        self.dias_widgets[i][j].config(relief="solid", bd=1, fg="#10B981", highlightbackground=COLORS["accent"])
                        current_style = self.day_default_styles.get(self.dias_widgets[i][j], {})
                        self.day_default_styles[self.dias_widgets[i][j]] = {
                            "bg": current_style.get("bg", COLORS["card"]),
                            "fg": "#10B981",
                            "relief": "solid",
                            "bd": 1,
                            "border": COLORS["accent"],
                        }
                    
                    if self.admin_mode:
                        self.dias_widgets[i][j].config(cursor="hand2")
                    
                    dia_actual += 1

    def seleccionar_dia(self, fila, columna):
        if not self.admin_mode:
            messagebox.showwarning("Bloqueado", "Iniciá sesión para modificar el calendario")
            return
        
        texto = self.dias_widgets[fila][columna].cget("text")
        if not texto:
            return
        try:
            dia = int(texto)
        except:
            return
        fecha_key = f"{self.current_year}-{self.current_month:02d}-{dia:02d}"
        
        popup = tk.Toplevel(self.root)
        popup.title(f"Asignar - {dia}/{self.current_month}")
        popup.geometry("280x250")
        popup.configure(bg=COLORS["bg"])
        
        tk.Label(popup, text=f"{dia}/{self.current_month}", 
                font=("Segoe UI", 12, "bold"), bg=COLORS["bg"], fg="white").pack(pady=15)
        
        for nombre, datos in HIPODROMOS.items():
            color = datos["color"]
            fg = "white" if nombre != "La plata" else "black"
            StyledButton(popup, text=datos["nombre"], bg=color, 
                      command=lambda h=nombre, f=fecha_key: self.asignar_hipodromo(h, f, popup)).pack(pady=8, fill="x", padx=40)
        
        StyledButton(popup, text="BORRAR", bg=COLORS["danger"], 
                    command=lambda: self.borrar_hipodromo(fecha_key, popup)).pack(pady=25, fill="x", padx=40)

    def asignar_hipodromo(self, hipodromo, fecha_key, popup):
        if "calendario" not in self.data:
            self.data["calendario"] = {}
        self.data["calendario"][fecha_key] = hipodromo
        self.guardar_datos()
        self.render_calendario()
        self.actualizar_info_box()
        popup.destroy()

    def borrar_hipodromo(self, fecha_key, popup):
        if fecha_key in self.data.get("calendario", {}):
            del self.data["calendario"][fecha_key]
            self.guardar_datos()
            self.render_calendario()
            self.actualizar_info_box()
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

    def actualizar_info_box(self):
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")
        
        hipo_hoy = self.data.get("calendario", {}).get(fecha_hoy, "")
        hipo_manana = self.data.get("calendario", {}).get(manana, "")
        
        for w in self.info_box.winfo_children():
            w.destroy()
        
        frame_hoy = tk.Frame(self.info_box, bg=COLORS["bg"])
        frame_hoy.pack(side="left", fill="both", expand=True, padx=2)
        
        color_hoy = HIPODROMOS.get(hipo_hoy, {}).get("color", COLORS["card"]) if hipo_hoy else COLORS["card"]
        fg_hoy = "white" if hipo_hoy and hipo_hoy != "La plata" else "black"
        
        tk.Label(frame_hoy, text="HOY", font=("Segoe UI", 8, "bold"), bg=color_hoy, fg="white", pady=1).pack(fill="x")
        nombre_hoy = HIPODROMOS.get(hipo_hoy, {}).get("nombre", "-") if hipo_hoy else "-"
        tk.Label(frame_hoy, text=nombre_hoy, font=("Segoe UI", 9, "bold"), bg=color_hoy, fg=fg_hoy, pady=2).pack(fill="x")
        
        frame_manana = tk.Frame(self.info_box, bg=COLORS["bg"])
        frame_manana.pack(side="right", fill="both", expand=True, padx=2)
        
        color_manana = HIPODROMOS.get(hipo_manana, {}).get("color", COLORS["card"]) if hipo_manana else COLORS["card"]
        fg_manana = "white" if hipo_manana and hipo_manana != "La plata" else "black"
        
        tk.Label(frame_manana, text="MAÑANA", font=("Segoe UI", 8, "bold"), bg=color_manana, fg="white", pady=1).pack(fill="x")
        nombre_manana = HIPODROMOS.get(hipo_manana, {}).get("nombre", "-") if hipo_manana else "-"
        tk.Label(frame_manana, text=nombre_manana, font=("Segoe UI", 9, "bold"), bg=color_manana, fg=fg_manana, pady=2).pack(fill="x")

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
            self.btn_lock.config(text="🔒 CERRAR", bg=COLORS["success"])
        else:
            self.btn_lock.config(text="🔓 LOGIN", bg=COLORS["danger"])
    
    def mostrar_login(self):
        if self.login_popup_abierto:
            return
        
        self.login_popup_abierto = True
        popup = tk.Toplevel(self.root)
        popup.title("Login Admin")
        popup.geometry("300x220")
        popup.resizable(False, False)
        popup.configure(bg=COLORS["bg"])

        card = tk.Frame(popup, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
        card.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(card, text="LOGIN ADMIN", font=("Segoe UI", 10, "bold"), bg=COLORS["surface"], fg=COLORS["fg"]).pack(pady=(10, 8))

        tk.Label(card, text="USUARIO", font=("Segoe UI", 8, "bold"), bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=14)
        entry_user = tk.Entry(
            card,
            font=("Segoe UI", 10),
            bg=COLORS["card"],
            fg=COLORS["fg"],
            insertbackground=COLORS["fg"],
            relief="flat",
            bd=0
        )
        entry_user.pack(fill="x", padx=14, pady=(4, 10), ipady=4)
        
        tk.Label(card, text="CLAVE", font=("Segoe UI", 8, "bold"), bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=14)
        entry_pass = tk.Entry(
            card,
            font=("Segoe UI", 10),
            show="*",
            bg=COLORS["card"],
            fg=COLORS["fg"],
            insertbackground=COLORS["fg"],
            relief="flat",
            bd=0
        )
        entry_pass.pack(fill="x", padx=14, pady=(4, 12), ipady=4)
        
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
        
        StyledButton(card, text="ENTRAR", bg=COLORS["success"], hover_bg="#0D9F74", command=verificar_login).pack(pady=(0, 10))
    
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
        
        self.header_frame = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
        self.header_frame.pack(fill="x", pady=4, padx=6)
        
        self.btn_hoy = SegmentedButton(
            self.header_frame,
            text="HOY",
            bg=COLORS["accent"],
            activebackground=COLORS["accent"],
            fg=COLORS["fg"],
            hover_bg=COLORS["hover_accent"],
            command=self.mostrar_panel_hoy
        )
        self.btn_hoy.pack(side="left", padx=(6, 3), pady=4)
        
        self.btn_manana = SegmentedButton(
            self.header_frame,
            text="MAÑANA",
            bg=COLORS["card"],
            activebackground=COLORS["card"],
            fg=COLORS["muted"],
            hover_bg=COLORS["hover_soft"],
            command=self._on_btn_manana_click
        )
        self.btn_manana.config(state="normal")
        self.btn_manana.pack(side="left", padx=(3, 6), pady=4)
        
        self.panel_actual = "hoy"
        
        self.panel_hoy_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.panel_manana_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.panel_hoy_frame.configure(highlightthickness=1, highlightbackground=COLORS["border"])
        self.panel_manana_frame.configure(highlightthickness=1, highlightbackground=COLORS["border"])
        
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
        header = tk.Frame(frame, bg=COLORS["bg"])
        header.pack(fill="x", pady=3, padx=6)
        
        if tipo == "hoy":
            self.lbl_titulo_hoy = tk.Label(header, text="", font=("Segoe UI", 10, "bold"), bg=COLORS["bg"], fg=COLORS["fg"])
            self.lbl_titulo_hoy.pack(side="left", padx=5)
            self.header_hoy = header
            
            self.modo_hoy_var = tk.StringVar(value="dia2")
            self.btn_modo_d1_hoy = SegmentedButton(
                header,
                text="D1",
                bg=COLORS["card"],
                activebackground=COLORS["card"],
                fg=COLORS["muted"],
                hover_bg=COLORS["hover_soft"],
                command=lambda: self.set_mode_panel("hoy", "dia1")
            )
            self.btn_modo_d1_hoy.pack(side="left", padx=2)
            self.btn_modo_d2_hoy = SegmentedButton(
                header,
                text="D2",
                bg=COLORS["accent"],
                activebackground=COLORS["accent"],
                fg=COLORS["fg"],
                hover_bg=COLORS["hover_accent"],
                command=lambda: self.set_mode_panel("hoy", "dia2")
            )
            self.btn_modo_d2_hoy.pack(side="left", padx=2)
            
            self.btn_guardar_hoy = StyledButton(header, text="GUARDAR", bg=COLORS["success"], command=lambda: self.guardar_checklist_panel("hoy"))
            self.btn_guardar_hoy.pack(side="right", padx=3)
            
            self.check_vars_hoy = {}
            self.checklist_frame_hoy = self.crear_checklist_frame(frame)
        else:
            self.lbl_titulo_manana = tk.Label(header, text="", font=("Segoe UI", 10, "bold"), bg=COLORS["bg"], fg=COLORS["fg"])
            self.lbl_titulo_manana.pack(side="left", padx=5)
            self.header_manana = header
            
            self.modo_manana_var = tk.StringVar(value="dia1")
            self.btn_modo_d1_manana = SegmentedButton(
                header,
                text="D1",
                bg=COLORS["accent"],
                activebackground=COLORS["accent"],
                fg=COLORS["fg"],
                hover_bg=COLORS["hover_accent"],
                command=lambda: self.set_mode_panel("manana", "dia1")
            )
            self.btn_modo_d1_manana.pack(side="left", padx=2)
            self.btn_modo_d2_manana = SegmentedButton(
                header,
                text="D2",
                bg=COLORS["card"],
                activebackground=COLORS["card"],
                fg=COLORS["muted"],
                hover_bg=COLORS["hover_soft"],
                command=lambda: self.set_mode_panel("manana", "dia2")
            )
            self.btn_modo_d2_manana.pack(side="left", padx=2)
            self.btn_modo_d2_manana.set_enabled(False)
            
            self.btn_guardar_manana = StyledButton(header, text="GUARDAR", bg=COLORS["success"], command=lambda: self.guardar_checklist_panel("manana"))
            self.btn_guardar_manana.pack(side="right", padx=3)
            
            self.check_vars_manana = {}
            self.checklist_frame_manana = self.crear_checklist_frame(frame)

        self.update_mode_toggle(tipo)

    def crear_checklist_frame(self, parent):
        container = tk.Frame(parent, bg=COLORS["surface"])
        container.pack(fill="both", expand=True, padx=2, pady=1)
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
            fg = "white" if hipo_hoy != "La plata" else "black"
            self.lbl_titulo_hoy.config(text=f"HOY - {nombre}", fg=fg, bg=color)
            self.panel_hoy_frame.configure(bg=color)
            if hasattr(self, 'header_hoy'):
                self.header_hoy.configure(bg=color)
        else:
            self.lbl_titulo_hoy.config(text="HOY - SIN CARRERA", fg="#9CA3AF", bg=COLORS["bg"])
            self.panel_hoy_frame.configure(bg=COLORS["bg"])
            if hasattr(self, 'header_hoy'):
                self.header_hoy.configure(bg=COLORS["bg"])

        if hipo_manana and hipo_manana in HIPODROMOS:
            nombre = HIPODROMOS[hipo_manana]["nombre"]
            color = HIPODROMOS[hipo_manana]["color"]
            fg = "white" if hipo_manana != "La plata" else "black"
            self.lbl_titulo_manana.config(text=f"MAÑANA - {nombre}", fg=fg, bg=color)
            self.panel_manana_frame.configure(bg=color)
            if hasattr(self, 'header_manana'):
                self.header_manana.configure(bg=color)
        else:
            self.lbl_titulo_manana.config(text="MAÑANA - SIN CARRERA", fg="#9CA3AF", bg=COLORS["bg"])
            self.panel_manana_frame.configure(bg=COLORS["bg"])
            if hasattr(self, 'header_manana'):
                self.header_manana.configure(bg=COLORS["bg"])

        estado_hoy = self.data.get("estado", {}).get(fecha_hoy, "")
        estado_manana = self.data.get("estado", {}).get(manana, "")

        self.set_mode_d2_enabled("hoy", estado_hoy in ("dia1_completado", "completo"))
        self.set_mode_d2_enabled("manana", estado_manana in ("dia1_completado", "completo"))

        if estado_hoy in ("dia1_completado", "completo") and self.modo_hoy_var.get() == "dia1":
            self.modo_hoy_var.set("dia2")
        if estado_manana in ("dia1_completado", "completo") and self.modo_manana_var.get() == "dia1":
            self.modo_manana_var.set("dia2")

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

            box = tk.Frame(frame, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
            box.pack(fill="x", padx=6, pady=8)
            tk.Label(
                box,
                text="DIA 1 COMPLETADO",
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["success"],
                pady=8,
            ).pack()
            tk.Label(
                box,
                text="D2 habilitado. Continuá con DIA 2.",
                font=("Segoe UI", 8),
                bg=COLORS["surface"],
                fg=COLORS["fg"],
                pady=4,
            ).pack()
            StyledButton(box, text="IR A D2", bg=COLORS["accent"], command=lambda p=panel: self.set_mode_panel(p, "dia2")).pack(pady=(2, 10))
            return
        
        if modo == "dia1":
            items = CHECKLIST_DIA1
        else:
            hipo = self.data.get("calendario", {}).get(fecha_key, "")
            items = CHECKLIST_DIA2_POR_HIPODROMO.get(hipo, CHECKLIST_DIA2_SAN_ISIDRO)
        
        hipo = self.data.get("calendario", {}).get(fecha_key, "")
        
        bg_color = COLORS["card_soft"]
        fg_color = COLORS["fg"]
        
        if hipo and hipo in HIPODROMOS:
            bg_color = HIPODROMOS[hipo]["color"]
            fg_color = "white" if hipo != "Palermo" else "black"
        
        for w in frame.winfo_children():
            w.destroy()
        
        container = frame.master
        container.update_idletasks()
        
        frame.update_idletasks()
        cols = 2
        wrap_len = 180
        row_items = {}
        # FIX: Usar max_items fijo (14) para mantener uniforme el tamaño de filas
        # Esto evita que La Plata (10 items) se vea diferente que San Isidro (13 items)
        max_items = 14
        row_count = max(1, (max_items + cols - 1) // cols)
        target_row_height = 26

        for r in range(0, 20):
            frame.rowconfigure(r, weight=0, minsize=0)

        for idx, item in enumerate(items):
            row = idx % row_count
            col = idx // row_count
            
            frame_item = tk.Frame(
                frame,
                bg=bg_color,
                pady=3,
                padx=5,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=COLORS["border"]
            )
            frame_item.grid(row=row, column=col, sticky="nsew", pady=1, padx=1)
            row_items.setdefault(row, []).append(frame_item)
            
            var = tk.BooleanVar(value=False)
            check_vars[item] = var
            
            if modo == "dia2" and item == "SETEAR CATEGORIA":
                hipo_nombre = HIPODROMOS.get(hipo, {}).get("nombre", "SIN ASIGNAR")
                
                inner_frame = tk.Frame(frame_item, bg=bg_color)
                inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
                
                cb = tk.Checkbutton(
                    inner_frame,
                    text="",
                    variable=var,
                    bg=bg_color,
                    fg=fg_color,
                    selectcolor="#22C55E",
                    activebackground=bg_color,
                    activeforeground=fg_color,
                    font=("Segoe UI", 9, "bold"),
                    bd=0,
                    relief="flat",
                    indicatoron=True,
                )
                cb.pack(side="left", padx=(0, 4), anchor="center", fill="none")
                
                label_setear = tk.Label(
                    inner_frame,
                    text="SETEAR CATEGORIA -",
                    font=("Segoe UI", 9, "bold"),
                    bg=bg_color,
                    fg=fg_color,
                )
                label_setear.pack(side="left", padx=2, anchor="center")
                
                label_alerta = tk.Label(
                    inner_frame,
                    text=hipo_nombre,
                    font=("Segoe UI", 14, "bold"),
                    bg=bg_color,
                    fg="#FF0000"
                )
                label_alerta.pack(side="left", padx=2, anchor="center")
                
                blinking = [True]
                blink_colors = ["#FF0000", "#FFFFFF"]
                blink_idx = [0]
                blink_timer = [None]
                
                def blink_loop():
                    label_alerta.config(fg=blink_colors[blink_idx[0] % 2])
                    blink_idx[0] = (blink_idx[0] + 1) % 2
                    blink_timer[0] = label_alerta.after(600, blink_loop)
                
                blink_loop()
                
                def on_toggle(*args, fi=frame_item, inf=inner_frame, ob=bg_color, v=var):
                    bg = COLORS["success"] if v.get() else ob
                    fi.configure(bg=bg)
                    inf.configure(bg=bg)
                    for c in inf.winfo_children():
                        try:
                            c.configure(bg=bg)
                        except tk.TclError:
                            pass
                var.trace_add("write", on_toggle)
            else:
                cb = tk.Checkbutton(
                    frame_item,
                    text=item,
                    variable=var,
                    bg=bg_color,
                    fg=fg_color,
                    selectcolor="#22C55E",
                    activebackground=bg_color,
                    activeforeground=fg_color,
                    font=("Segoe UI", 9, "bold"),
                    anchor="w",
                    justify="left",
                    wraplength=wrap_len,
                    bd=0,
                    relief="flat",
                )
                cb.pack(fill="x", expand=True)
                
                def on_toggle(*args, fi=frame_item, ob=bg_color, v=var):
                    bg = COLORS["success"] if v.get() else ob
                    fi.configure(bg=bg)
                    for c in fi.winfo_children():
                        try:
                            c.configure(bg=bg)
                        except tk.TclError:
                            pass
                var.trace_add("write", on_toggle)
            
                frame.update_idletasks()
        for row, row_frames in row_items.items():
            target_height = 34
            frame.rowconfigure(row, weight=1, minsize=target_height)
            for item in row_frames:
                item.grid_propagate(False)
                item.configure(height=target_height)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        print(f"RENDER DONE panel={panel}")

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
        
        container = tk.Frame(frame, bg=COLORS["success"], highlightthickness=1, highlightbackground=COLORS["border"])
        container.pack(fill="x", padx=6, pady=10)
        
        tk.Label(container, text="✓ CHECKLIST COMPLETO", 
               font=("Segoe UI", 12, "bold"), bg=COLORS["success"], fg="white").pack(pady=10)
        
        btn_frame = tk.Frame(container, bg=COLORS["success"])
        btn_frame.pack(pady=5, fill="x", expand=True)
        
        btn_imprimir = tk.Button(btn_frame, text="📄 IMPRIMIR", bg="white", fg=COLORS["success"],
                                font=("Segoe UI", 9, "bold"), command=lambda: self.imprimir_pdf_panel(panel))
        btn_imprimir.pack(side="left", padx=10, pady=5)
        
        btn_reiniciar = tk.Button(btn_frame, text="🔄 REINICIAR", bg=COLORS["danger"], fg="white",
                                  font=("Segoe UI", 9, "bold"), command=lambda: self.reiniciar_panel(panel))
        btn_reiniciar.pack(side="left", padx=10, pady=5)

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

    def imprimir_pdf_panel(self, panel):
        from datetime import timedelta
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        fecha_hoy = hoy.strftime("%Y-%m-%d")
        
        if panel == "hoy":
            fecha_key = fecha_hoy
            titulo_panel = "HOY"
        else:
            fecha_key = manana
            titulo_panel = "MAÑANA"
        
        hipodromo = self.data.get("calendario", {}).get(fecha_key, "No asignado")
        
        nombre_archivo = f"Checklist_{hipodromo.replace(' ', '_')}_{fecha_key}.pdf"
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=nombre_archivo)
        if not archivo:
            return

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
        items_d2 = CHECKLIST_DIA2_POR_HIPODROMO.get(hipo, CHECKLIST_DIA2_SAN_ISIDRO)

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
        messagebox.showinfo("PDF", f"PDF guardado: {archivo}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()