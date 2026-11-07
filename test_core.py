import json
import os
import shutil
import tempfile
import unittest
from datetime import date

import core


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.archivo = os.path.join(self.dir, "data.json")
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump({
                "calendario": {
                    "2026-11-04": "San isidro",
                    "2026-11-05": "La plata",
                    "2026-11-06": "Palermo",
                    "2026-11-07": "San isidro",
                },
                "checklist": {"2026-11-04": {item: True for item in core.CHECKLIST_DIA2_SAN_ISIDRO}},
                "estado": {},
            }, f)
        self.fecha = date(2026, 11, 4)
        self.core = core.ChecklistCore(self.archivo, hoy=lambda: self.fecha)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_abre_en_d1_si_d1_no_esta_hecho(self):
        panel = self.core.estado()["paneles"]["hoy"]
        self.assertEqual(panel["modo"], "dia1")
        self.assertEqual([i["nombre"] for i in panel["items"]], core.CHECKLIST_DIA1)
        self.assertEqual(panel["hechos"], 0)

    def test_d2_bloqueado_sin_d1(self):
        r = self.core.set_modo("hoy", "dia2")
        self.assertFalse(r["ok"])
        self.assertEqual(r["tipo"], "d1_pendiente")
        self.assertEqual(self.core.modos["hoy"], "dia1")

    def test_guardar_incompleto(self):
        r = self.core.guardar("hoy", "dia1", core.CHECKLIST_DIA1)
        self.assertEqual(r["tipo"], "incompleto")
        self.assertIn("0/14", r["mensaje"])

    def test_d1_completo_habilita_d2_y_conserva_checks_de_d2(self):
        for item in core.CHECKLIST_DIA1:
            self.core.toggle_check("hoy", item, True)
        r = self.core.guardar("hoy", "dia1", core.CHECKLIST_DIA1)
        self.assertEqual(r["tipo"], "dia1_completado")
        panel = self.core.estado()["paneles"]["hoy"]
        self.assertEqual(panel["modo"], "dia2")
        self.assertEqual(panel["hechos"], panel["total"])
        r = self.core.guardar("hoy", "dia2", [i["nombre"] for i in panel["items"]])
        self.assertEqual(r["tipo"], "completo")
        self.assertEqual(self.core.estado()["paneles"]["hoy"]["vista"], "completo")

    def test_lista_desfasada(self):
        r = self.core.guardar("hoy", "dia2", core.CHECKLIST_DIA2_SAN_ISIDRO)
        self.assertEqual(r["tipo"], "desfasado")
        self.assertEqual(self.core.estado_fecha("2026-11-04"), "")

    def test_checks_persisten_en_archivo(self):
        self.core.toggle_check("manana", "PRINTERS", True)
        otro = core.ChecklistCore(self.archivo, hoy=lambda: self.fecha)
        self.assertTrue(otro.data["checklist"]["2026-11-05"]["PRINTERS"])

    def test_secuencia_alertas_xml(self):
        secuencia = []
        while (alerta := self.core.estado()["xml"]) and len(secuencia) < 5:
            secuencia.append(alerta["texto"])
            self.core.marcar_xml(alerta["fecha"])
        self.assertEqual(secuencia, ["SUBIR EL XML DE SI (04/11)", "SUBIR EL XML DE LP (05/11)"])
        self.fecha = date(2026, 11, 6)
        self.assertEqual(self.core.estado()["xml"]["texto"], "SUBIR EL XML DE SI (07/11)")

    def test_cambio_de_dia_recalcula_modos(self):
        self.core.data["estado"]["2026-11-05"] = "dia1_completado"
        self.fecha = date(2026, 11, 5)
        self.assertEqual(self.core.estado()["paneles"]["hoy"]["modo"], "dia2")

    def test_calendario_requiere_login(self):
        self.assertFalse(self.core.asignar("2026-11-08", "Palermo")["ok"])
        self.assertFalse(self.core.login("admin", "mal")["ok"])
        self.assertTrue(self.core.login("admin", "eze1")["ok"])
        self.assertTrue(self.core.asignar("2026-11-08", "Palermo")["ok"])
        cal = self.core.calendario(2026, 11)
        self.assertEqual(cal["offset"], 0)
        self.assertEqual(cal["dias"][7]["hipo"], "Palermo")
        self.assertTrue(cal["dias"][3]["hoy"])

    def test_preferencia_caballito_persiste(self):
        self.assertTrue(self.core.estado()["preferencias"]["caballito"])
        self.assertTrue(self.core.set_preferencia("caballito", False)["ok"])
        otro = core.ChecklistCore(self.archivo, hoy=lambda: self.fecha)
        self.assertFalse(otro.estado()["preferencias"]["caballito"])
        self.assertFalse(self.core.set_preferencia("otra", True)["ok"])

    def test_pdf(self):
        archivo = os.path.join(self.dir, "x.pdf")
        self.core.generar_pdf("hoy", archivo)
        self.assertGreater(os.path.getsize(archivo), 1000)


if __name__ == "__main__":
    unittest.main()
