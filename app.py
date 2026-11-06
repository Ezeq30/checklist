import os
import sys
import tempfile
import threading

import webview

from core import ChecklistCore

if getattr(sys, "frozen", False):
    RECURSOS = sys._MEIPASS
else:
    RECURSOS = os.path.dirname(os.path.abspath(__file__))

UI_INDEX = os.path.join(RECURSOS, "ui", "index.html")


class Api:
    def __init__(self, core):
        self._core = core
        self._lock = threading.Lock()
        self._window = None

    def _con_estado(self, res):
        return {"resultado": res, "estado": self._core.estado()}

    def estado(self):
        with self._lock:
            return self._core.estado()

    def toggle_check(self, panel, item, valor):
        with self._lock:
            return self._con_estado(self._core.toggle_check(panel, item, valor))

    def set_modo(self, panel, modo):
        with self._lock:
            return self._con_estado(self._core.set_modo(panel, modo))

    def guardar(self, panel, modo, items):
        with self._lock:
            return self._con_estado(self._core.guardar(panel, modo, items))

    def reiniciar(self, panel):
        with self._lock:
            return self._con_estado(self._core.reiniciar(panel))

    def marcar_xml(self, fecha):
        with self._lock:
            return self._con_estado(self._core.marcar_xml(fecha))

    def calendario(self, anio, mes):
        with self._lock:
            return self._core.calendario(int(anio), int(mes))

    def login(self, usuario, clave):
        with self._lock:
            return self._con_estado(self._core.login(usuario, clave))

    def logout(self):
        with self._lock:
            return self._con_estado(self._core.logout())

    def asignar(self, fecha, hipo):
        with self._lock:
            return self._con_estado(self._core.asignar(fecha, hipo))

    def borrar(self, fecha):
        with self._lock:
            return self._con_estado(self._core.borrar(fecha))

    def guardar_pdf(self, panel):
        destino = self._window.create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=self._core.nombre_pdf(panel),
            file_types=("PDF (*.pdf)",),
        )
        if not destino:
            return {"ok": False, "tipo": "cancelado", "titulo": "", "mensaje": ""}
        archivo = destino if isinstance(destino, str) else destino[0]
        if not archivo.lower().endswith(".pdf"):
            archivo += ".pdf"
        with self._lock:
            self._core.generar_pdf(panel, archivo)
        return {"ok": True, "tipo": "ok", "titulo": "PDF guardado", "mensaje": archivo}

    def imprimir(self, panel):
        archivo = os.path.join(tempfile.gettempdir(), self._core.nombre_pdf(panel))
        with self._lock:
            self._core.generar_pdf(panel, archivo)
        try:
            os.startfile(archivo)
        except OSError:
            return {"ok": False, "tipo": "error", "titulo": "Imprimir", "mensaje": "No se pudo abrir la vista previa. Probá Guardar PDF."}
        return {"ok": True, "tipo": "ok", "titulo": "Vista previa", "mensaje": "Se abrió el PDF para imprimir."}


def main():
    api = Api(ChecklistCore())
    window = webview.create_window(
        "Checklist Hipódromos",
        url=UI_INDEX,
        js_api=api,
        width=940,
        height=400,
        resizable=False,
        background_color="#070B14",
    )
    api._window = window
    webview.start(debug=bool(os.environ.get("CHECKLIST_DEBUG")))


if __name__ == "__main__":
    main()
