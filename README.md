# Checklist Hipodromos

## Descripción
Aplicación de escritorio en Python (Tkinter) para gestionar checklists de hipódromos (San Isidro, La Plata, Palermo). Permite registrar carreras por fecha, completar checklists de Día 1 (Pre-Carrera) y Día 2 (Carrera), y generar PDFs con estilo visual moderno.

## Estructura del Proyecto

```
Check/
├── main.py              # Código principal de la aplicación
├── data.json           # Archivo de datos (se genera automáticamente)
├── README.md           # Este archivo
├── README_DEBUG.md     # Notas de depuración
├── ChecklistHipodromos.spec  # Spec para PyInstaller
└── dist/
    └── ChecklistHipodromos.exe  # Ejecutable compilado
```

## Características

### Calendario
- Visualización de mes con navegación
- Asignación de hipódromos a fechas específicas (modo admin)
- Muestra "HOY" y "MAÑANA" con el hipódromo asignado
- Grilla uniforme (mismo espaciado y tamaño entre celdas)
- Encabezado de mes con ancho fijo para evitar que el layout se mueva
- Celdas más grandes para mejor legibilidad

### Checklists
- **Día 1 (Pre-Carrera)**: 14 items fija
- **Día 2 (Carrera)**: Variante según hipódromo
  - San Isidro: 13 items
  - La Plata: 10 items
  - Palermo: 7 items
- Visualización en 2 columnas sin scroll lateral visible
- Ajuste automático de altura de tarjetas para que entren todos los checks
- Texto de checks con fuente más grande y alineación prolija
- Validación de completitud antes de guardar
- Flujo guiado: al completar Día 1 se habilita Día 2 y cambia automáticamente al modo Día 2
- Botón de PDF removido del encabezado (imprimir solo al finalizar el checklist completo)

### PDF
- Genera PDF con Día 1 y Día 2 juntos
- Incluye fecha, hipódromo y estado de cada item
- Diseño modernizado:
  - Cabeceras y títulos con color del hipódromo
  - Filas alternadas para mejor lectura
  - Estado final con color semántico (completado/incompleto)

### Admin
- Login: usuario `admin`, clave `eze1`
- Solo con login se pueden modificar asignaciones del calendario
- Popup de login rediseñado (estilo moderno y compacto)

### Interfaz
- Ventana principal de tamaño fijo: `940x395`
- Estilo visual modernizado (paleta, tarjetas, botones segmentados)
- Botones/controles con comportamiento hover

## Variables Importantes

```python
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
```

### Listas de Checks
- CHECKLIST_DIA1: 14 items pre-carrera
- CHECKLIST_DIA2_SAN_ISIDRO: 13 items
- CHECKLIST_DIA2_LA_PLATA: 10 items
- CHECKLIST_DIA2_PALERMO: 7 items

## Datos (data.json)
Estructura:
```json
{
  "calendario": {
    "2026-05-06": "San isidro"
  },
  "checklist": {
    "2026-05-06": {
      "FECHA Y ESTADO": true,
      "MEET Y PERFORMANCE": true,
      ...
    }
  },
  "estado": {
    "2026-05-06": "completo"
  }
}
```

## Compilación
```bash
python -m PyInstaller ChecklistHipodromos.spec --noconfirm
```

## Cambios Realizados Recientemente
- Rediseño visual general de la app (look más moderno)
- Ventana fija compacta (`940x395`)
- Calendario más grande con grilla uniforme y espaciados consistentes
- Checks en 2 columnas optimizados para ocupar mejor el área visible
- Eliminación del botón `PDF` del header de checklist
- Impresión disponible al finalizar checklist completo (pantalla de completado)
- Flujo Día 1 -> Día 2 automático tras completar Día 1
- PDF modernizado con colores por hipódromo y mejor legibilidad de tablas
- Recompilación del ejecutable con todos los ajustes

## Estado Actual
- El ejecutable funciona correctamente
- Los datos se guardan en data.json en la carpeta del exe
- Login evita apertura múltiple de popup
- Calendario y checklist ajustados para reducir espacios vacíos y mejorar legibilidad
- D2 de MAÑANA se habilita correctamente tras completar D1
- Renderizado uniforme de checklists (mismo tamaño de filas para todos los hipódromos)
- Cambio entre D1/D2 funciona correctamente para ambos paneles (HOY y MAÑANA)

## Cambios de Mantenimiento y Fixes (2025-05-10)

### Fix: Habilitación de D2 para MAÑANA
- **Problema**: Al completar D1 de MAÑANA, el botón D2 no se habilitaba automáticamente
- **Causa**: La función `actualizar_info_paneles()` nunca se llamaba después de guardar
- **Solución**: Se llama `actualizar_info_paneles()` en:
  - `__init__`: al iniciar la app
  - `guardar_checklist_panel`: después de guardar D1 o D2

### Fix: Renderizado uniforme de checkboxes
- **Problema**: Los items de La Plata (10 items) se veían más grandes que San Isidro (13 items)
- **Causa**: `row_count` dependía de la cantidad de items reales
- **Solución**: Se usa un `row_count` máximo fijo de 14 items para mantener proporciones uniformes

### Fix: Cambio entre D1 y D2 no actualizaba la vista
- **Problema**: Al hacer click en D1 desde D2 en el panel MAÑANA, no se refreshaba la vista
- **Causa**: `set_mode_panel` solo llamaba a `render_checklist_panel` para HOY
- **Solución**: Ahora `set_mode_panel` siempre renderiza el panel seleccionado

### Fix: Refresh después de guardar D1
- **Problema**: Al guardar D1 completado, no mostraba "Día 1 completado" automáticamente
- **Causa**: Faltaba forzar el render después de cambiar el modo
- **Solución**: Se agregaron `root.update_idletasks()` y `render_checklist_panel()` después de guardar

## Problemas Conocidos / Próximos Ajustes
- Ajustar fino de tipografías según escala de Windows (100%, 125%, 150%) para mantener proporciones ideales.
- Opcional: agregar selector de tema (oscuro/claro) manteniendo paleta por hipódromo.
- Opcional: incluir logo/encabezado institucional en el PDF.
- Opcional: sumar configuración de tamaño de ventana desde archivo de ajustes.