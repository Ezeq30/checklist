import json
import os
import sys
from datetime import date, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HIPODROMOS = {
    "San isidro": {"color": "#2E7D32", "nombre": "SAN ISIDRO", "checked": "#4CAF50"},
    "La plata": {"color": "#1565C0", "nombre": "LA PLATA", "checked": "#42A5F5"},
    "Palermo": {"color": "#F9A825", "nombre": "PALERMO", "checked": "#FDD835"},
    "Sin hipodromo": {"color": "#C62828", "nombre": "SIN HIPODROMO", "checked": "#EF4444"},
}

XML_HIPODROMOS = {"San isidro": "SI", "La plata": "LP"}

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

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
         "Septiembre", "Octubre", "Noviembre", "Diciembre"]

ADMIN_USUARIO = "admin"
ADMIN_CLAVE = "eze1"

PREFERENCIAS_POR_DEFECTO = {"caballito": True}

if getattr(sys, "frozen", False):
    exec_dir = os.path.dirname(sys.executable)
else:
    exec_dir = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(exec_dir, "data.json")


def hipo_fg(hipo):
    return "#000000" if hipo == "Palermo" else "#FFFFFF"


def dia_mes(fecha_key):
    return f"{fecha_key[8:10]}/{fecha_key[5:7]}"


def resultado(ok, tipo, titulo="", mensaje=""):
    return {"ok": ok, "tipo": tipo, "titulo": titulo, "mensaje": mensaje}


class ChecklistCore:
    def __init__(self, data_file=DATA_FILE, hoy=date.today):
        self.data_file = data_file
        self._hoy = hoy
        self.data = self.cargar_datos()
        self.admin = False
        self.modos = {}
        self._fecha_modos = None
        self._sincronizar_modos()

    # Datos

    def cargar_datos(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "xml_si" in data:
                data.setdefault("xml_subido", {}).update(data.pop("xml_si"))
            return data
        return {"calendario": {}, "checklist": {}}

    def guardar_datos(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def limpiar_datos_antiguos(self):
        fecha_limite = (self._hoy() - timedelta(days=2)).isoformat()
        hubo_borrados = False
        for seccion in ("checklist", "estado", "xml_subido"):
            fechas = [f for f in self.data.get(seccion, {}) if f < fecha_limite]
            for f in fechas:
                del self.data[seccion][f]
                hubo_borrados = True
        if hubo_borrados:
            self.guardar_datos()

    # Fechas y modos

    def fecha_panel(self, panel):
        hoy = self._hoy()
        return (hoy if panel == "hoy" else hoy + timedelta(days=1)).isoformat()

    def hipodromo(self, fecha_key):
        return self.data.get("calendario", {}).get(fecha_key, "")

    def estado_fecha(self, fecha_key):
        return self.data.get("estado", {}).get(fecha_key, "")

    def d1_hecho(self, fecha_key):
        return self.estado_fecha(fecha_key) in ("dia1_completado", "completo")

    def _sincronizar_modos(self):
        if self._fecha_modos != self._hoy():
            self._fecha_modos = self._hoy()
            self.modos = {
                panel: "dia2" if self.d1_hecho(self.fecha_panel(panel)) else "dia1"
                for panel in ("hoy", "manana")
            }
        for panel in ("hoy", "manana"):
            if not self.d1_hecho(self.fecha_panel(panel)):
                self.modos[panel] = "dia1"

    def items_checklist(self, fecha_key, modo):
        if modo == "dia1":
            return CHECKLIST_DIA1
        hipo = self.hipodromo(fecha_key)
        items = CHECKLIST_DIA2_POR_HIPODROMO.get(hipo, [])
        if hipo not in ("Sin hipodromo",) and not items:
            items = CHECKLIST_DIA2_SAN_ISIDRO
        return items

    def set_modo(self, panel, modo):
        self._sincronizar_modos()
        if modo == "dia2" and not self.d1_hecho(self.fecha_panel(panel)):
            return resultado(
                False, "d1_pendiente", "Día 1 pendiente",
                "Todavía no se completó el Día 1. Completá y guardá el Día 1 para poder pasar al Día 2.",
            )
        self.modos[panel] = modo
        return resultado(True, "ok")

    # Checks

    def toggle_check(self, panel, item, valor):
        fecha_key = self.fecha_panel(panel)
        self.data.setdefault("checklist", {}).setdefault(fecha_key, {})[item] = bool(valor)
        self.guardar_datos()
        return resultado(True, "ok")

    def guardar(self, panel, modo_ui=None, items_ui=None):
        self._sincronizar_modos()
        fecha_key = self.fecha_panel(panel)
        modo = self.modos[panel]
        items = self.items_checklist(fecha_key, modo)

        if (modo_ui is not None and modo_ui != modo) or (items_ui is not None and set(items_ui) != set(items)):
            return resultado(
                False, "desfasado", "Revisá el checklist",
                "La lista en pantalla no correspondía al día seleccionado. Se actualizó: revisala y volvé a guardar.",
            )

        checks = self.data.setdefault("checklist", {}).setdefault(fecha_key, {})
        hechos = sum(1 for item in items if checks.get(item))
        total = len(items)
        if total == 0 or hechos < total:
            return resultado(False, "incompleto", "Incompleto", f"Completá todos los items ({hechos}/{total})")

        if modo == "dia2" and not self.d1_hecho(fecha_key):
            return resultado(False, "bloqueado", "Bloqueado", "Primero completá y guardá DIA 1 para habilitar DIA 2.")

        estados = self.data.setdefault("estado", {})
        if modo == "dia1":
            estados[fecha_key] = "dia1_completado"
            self.guardar_datos()
            self.limpiar_datos_antiguos()
            self.modos[panel] = "dia2"
            return resultado(True, "dia1_completado", "Día 1 completado", f"({hechos}/{total}) Ahora completá el Día 2.")

        estados[fecha_key] = "completo"
        self.guardar_datos()
        self.limpiar_datos_antiguos()
        return resultado(True, "completo", "Checklist completo", "Guardá el PDF, imprimilo o reiniciá.")

    def reiniciar(self, panel):
        fecha_key = self.fecha_panel(panel)
        self.data.get("checklist", {}).pop(fecha_key, None)
        self.data.get("estado", {}).pop(fecha_key, None)
        self.modos[panel] = "dia1"
        self.guardar_datos()
        return resultado(True, "ok")

    # Alertas XML

    def buscar_xml_pendiente(self):
        hoy = self._hoy()
        subidos = self.data.get("xml_subido", {})
        for fecha_key in sorted(self.data.get("calendario", {})):
            if self.data["calendario"][fecha_key] not in XML_HIPODROMOS or subidos.get(fecha_key):
                continue
            try:
                fecha = date.fromisoformat(fecha_key)
            except ValueError:
                continue
            if fecha - timedelta(days=2) <= hoy <= fecha:
                return fecha_key
        return None

    def marcar_xml(self, fecha_key):
        if self.hipodromo(fecha_key) not in XML_HIPODROMOS:
            return resultado(False, "invalido", "XML", "Esa fecha no tiene XML para subir.")
        self.data.setdefault("xml_subido", {})[fecha_key] = True
        self.guardar_datos()
        return resultado(True, "ok")

    def _alerta_xml(self):
        fecha_key = self.buscar_xml_pendiente()
        if not fecha_key:
            return None
        hipo = self.hipodromo(fecha_key)
        sigla = XML_HIPODROMOS[hipo]
        return {
            "fecha": fecha_key,
            "hipo": hipo,
            "sigla": sigla,
            "nombre": HIPODROMOS[hipo]["nombre"],
            "color": HIPODROMOS[hipo]["color"],
            "claro": HIPODROMOS[hipo]["checked"],
            "texto": f"SUBIR EL XML DE {sigla} ({dia_mes(fecha_key)})",
            "confirmacion": f"¿Confirmás que subiste el XML de {sigla} del {dia_mes(fecha_key)}?",
        }

    # Calendario y admin

    def login(self, usuario, clave):
        if (usuario or "").strip() == ADMIN_USUARIO and (clave or "").strip() == ADMIN_CLAVE:
            self.admin = True
            return resultado(True, "ok", "Sesión iniciada", "Ya podés modificar el calendario.")
        return resultado(False, "error", "Error", "Usuario o clave incorrectos")

    def logout(self):
        self.admin = False
        return resultado(True, "ok")

    def asignar(self, fecha_key, hipo):
        if not self.admin:
            return resultado(False, "bloqueado", "Bloqueado", "Iniciá sesión para modificar el calendario")
        if hipo not in HIPODROMOS:
            return resultado(False, "invalido", "Error", "Hipódromo desconocido")
        self.data.setdefault("calendario", {})[fecha_key] = hipo
        self.guardar_datos()
        return resultado(True, "ok")

    def borrar(self, fecha_key):
        if not self.admin:
            return resultado(False, "bloqueado", "Bloqueado", "Iniciá sesión para modificar el calendario")
        if fecha_key in self.data.get("calendario", {}):
            del self.data["calendario"][fecha_key]
            self.guardar_datos()
        return resultado(True, "ok")

    def calendario(self, anio, mes):
        primero = date(anio, mes, 1)
        siguiente = date(anio + 1, 1, 1) if mes == 12 else date(anio, mes + 1, 1)
        hoy = self._hoy().isoformat()
        dias = []
        for n in range((siguiente - primero).days):
            fecha_key = (primero + timedelta(days=n)).isoformat()
            hipo = self.hipodromo(fecha_key)
            datos = HIPODROMOS.get(hipo)
            dias.append({
                "dia": n + 1,
                "fecha": fecha_key,
                "hipo": hipo if datos else "",
                "color": datos["color"] if datos else "",
                "fg": hipo_fg(hipo) if datos else "",
                "hoy": fecha_key == hoy,
            })
        return {
            "anio": anio,
            "mes": mes,
            "titulo": f"{MESES[mes - 1]} {anio}",
            "offset": (primero.weekday() + 1) % 7,
            "dias": dias,
        }

    # Preferencias

    def preferencias(self):
        return {**PREFERENCIAS_POR_DEFECTO, **self.data.get("preferencias", {})}

    def set_preferencia(self, clave, valor):
        if clave not in PREFERENCIAS_POR_DEFECTO:
            return resultado(False, "invalido", "Error", "Preferencia desconocida")
        self.data.setdefault("preferencias", {})[clave] = bool(valor)
        self.guardar_datos()
        return resultado(True, "ok")

    # Estado para la interfaz

    def _panel(self, panel):
        fecha_key = self.fecha_panel(panel)
        hipo = self.hipodromo(fecha_key)
        datos = HIPODROMOS.get(hipo)
        modo = self.modos[panel]
        estado = self.estado_fecha(fecha_key)
        items = self.items_checklist(fecha_key, modo)
        checks = self.data.get("checklist", {}).get(fecha_key, {})

        if estado == "completo":
            vista = "completo"
        elif modo == "dia1" and self.d1_hecho(fecha_key):
            vista = "d1_hecho"
        elif not items:
            vista = "sin_items"
        else:
            vista = "checks"

        return {
            "panel": panel,
            "fecha": fecha_key,
            "fecha_display": f"{fecha_key[8:10]}/{fecha_key[5:7]}/{fecha_key[0:4]}",
            "hipo": hipo if datos else "",
            "nombre": datos["nombre"] if datos else "Sin carrera",
            "color": datos["color"] if datos else "#38BDF8",
            "claro": datos["checked"] if datos else "#7DD3FC",
            "fg": hipo_fg(hipo) if datos else "#FFFFFF",
            "estado": estado,
            "d1_hecho": self.d1_hecho(fecha_key),
            "modo": modo,
            "vista": vista,
            "items": [
                {"nombre": item, "checked": bool(checks.get(item)), "setear": modo == "dia2" and item == "SETEAR CATEGORIA"}
                for item in items
            ],
            "hechos": sum(1 for item in items if checks.get(item)),
            "total": len(items),
        }

    def estado(self):
        self._sincronizar_modos()
        return {
            "hoy": self._hoy().isoformat(),
            "admin": self.admin,
            "preferencias": self.preferencias(),
            "paneles": {panel: self._panel(panel) for panel in ("hoy", "manana")},
            "xml": self._alerta_xml(),
            "hipodromos": [
                {"id": hipo, "nombre": datos["nombre"], "color": datos["color"], "fg": hipo_fg(hipo)}
                for hipo, datos in HIPODROMOS.items()
            ],
        }

    # PDF

    def nombre_pdf(self, panel):
        fecha_key = self.fecha_panel(panel)
        hipodromo = self.data.get("calendario", {}).get(fecha_key, "No asignado")
        return f"Checklist_{hipodromo.replace(' ', '_')}_{fecha_key}.pdf"

    def generar_pdf(self, panel, archivo):
        fecha_key = self.fecha_panel(panel)
        hipodromo = self.data.get("calendario", {}).get(fecha_key, "No asignado")

        doc = SimpleDocTemplate(archivo, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        hipo = self.hipodromo(fecha_key)
        hipo_color = colors.HexColor(HIPODROMOS.get(hipo, {}).get("color", "#374151"))
        header_fg = colors.white if hipo != "Palermo" else colors.black

        title_style = ParagraphStyle(
            "TitleModern", parent=styles["Title"], fontName="Helvetica-Bold",
            fontSize=18, textColor=hipo_color, spaceAfter=8,
        )
        subtitle_style = ParagraphStyle(
            "SubtitleModern", parent=styles["Normal"], fontName="Helvetica",
            fontSize=10, textColor=colors.HexColor("#4B5563"), spaceAfter=8,
        )
        status_ok_style = ParagraphStyle(
            "StatusOk", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=11, textColor=colors.HexColor("#047857"), spaceBefore=10,
        )
        status_bad_style = ParagraphStyle(
            "StatusBad", parent=styles["Normal"], fontName="Helvetica-Bold",
            fontSize=11, textColor=colors.HexColor("#B91C1C"), spaceBefore=10,
        )

        story.append(Paragraph(f"CHECKLIST - {hipodromo.upper()}", title_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Fecha: {fecha_key[8:10]}/{fecha_key[5:7]}/{fecha_key[0:4]}", subtitle_style))
        story.append(Spacer(1, 10))

        items_d2 = CHECKLIST_DIA2_POR_HIPODROMO.get(hipo, [])
        if hipo != "Sin hipodromo" and not items_d2:
            items_d2 = CHECKLIST_DIA2_SAN_ISIDRO
        checks = self.data.get("checklist", {}).get(fecha_key, {})

        def build_inner_table(title, items):
            filas = [[title, "", ""], ["#", "Item", "Estado"]]
            for i, item in enumerate(items, 1):
                filas.append([i, item, "✓" if checks.get(item) else "✗"])
            t = Table(filas, colWidths=[16, 186, 40])
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

        wrapper = Table(
            [[build_inner_table("DÍA 1 (PRE-CARRERA)", CHECKLIST_DIA1), build_inner_table("DÍA 2 (CARRERA)", items_d2)]],
            colWidths=[242, 242],
        )
        wrapper.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 10),
            ("LEFTPADDING", (1, 0), (1, 0), 10),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(wrapper)

        if self.estado_fecha(fecha_key) == "completo":
            story.append(Paragraph("✓ REUNIÓN COMPLETADA", status_ok_style))
        else:
            story.append(Paragraph("✗ REUNIÓN INCOMPLETA", status_bad_style))

        doc.build(story)
