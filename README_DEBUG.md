# Checklist Hipodromos - Notas de Debug y Desarrollo

## Bug: Checkboxes de MAÑANA no funcionan (RESUELTO)

### Síntoma Original
En la pestaña MAÑANA, al hacer click en un checkbox:
1. El checkbox se marcaba visualmente (True)
2. Inmediatamente después se desmarcaba (volvía a False)
3. HOY funcionaba perfectamente

### Causa Raíz
El código tenía `command=` en los checkbuttons con lógica que incluía:
- sys.stderr.write() para debug
- traceback.format_stack() para logging
- Llamadas adicionales que causaban rerenderizado

Estos comandos causaban que la aplicación procesara eventos adicionales durante el click,
lo cual eventualmente disparaba un re-render del panel y destruía los checkboxes recién creados.

### Solución Implementada

1. **Remover lógica compleja del command=**: 
   - Los checkbuttons ahora no tienen `command=` (Tkinter maneja el toggle automáticamente)
   - No hay funciones lambda con debug ni tracers dentro del command

2. **Mantener trace_add simple**:
   ```python
   var.trace_add("write", lambda *a, p=panel, i=item, v=var: None)
   ```
   - Solo se usa para mantener referencia al objeto var
   - No hace nada en el callback (solo `pass` o `None` implícito)

3. **No re-renderizar después de click de checkbox**:
   - La app ya no tiene timers ni callbacks que re-rendericen automáticamente
   - El render solo ocurre cuando el usuario cambia de pestaña (HOY/MAÑANA)

### Lecciones Aprendidas

1. **Evitar callbacks complejos en command=**: 
   - Especialmente aquellos que hacen I/O (stderr, logging)
   - Los que generan traceback son especialmente problemáticos
   - Cualquier cosa que pueda disparar eventos adicionales

2. **Tkinter y eventos mixtos**: 
   - Cuando combinas trace_add con command, pueden interferir
   - Es mejor dejar que Tkinter maneje el toggle automáticamente
   -Si necesitas guardar el estado, hacelo en otro momento (ej: botón GUARDAR)

3. **Debug logging en producción**:
   - NUNCA dejar sys.stderr.write() o print() en código de producción
   - Crear un flag de debug o usar logging profesional

## Arquitectura del Código

### Flujo Principal

```
ChecklistApp(root)
├── setup_ui()
│   ├── setup_calendario()  → Widgets del calendario
│   └── setup_checklist()  → Paneles HOY y MAÑANA
│       └── setup_panel_individual()  → Configura cada panel
│
├── render_checklist_panel(panel)
│   ├── Limpia traces anteriores
│   ├── Destruye widgets existentes
│   ├── Crea nuevos BooleanVars
│   └── Crea nuevos Checkbuttons
│
├── cambiar_pestañas
│   ├── mostrar_panel_hoy()
│   └── mostrar_panel_manana() → render_checklist_panel("manana", force=True)
│
└── guardar_checklist_panel(panel) → Guarda en data.json
```

### Datos (data.json)

```json
{
  "calendario": {
    "2026-05-10": "San isidro"
  },
  "checklist": {
    "2026-05-10": {
      "FECHA Y ESTADO": true,
      "MEET Y PERFORMANCE": true
    }
  },
  "estado": {
    "2026-05-10": "completo"
  }
}
```

### Estados de Checklist
- `""` (vacío): No iniciado
- `"dia1_completado": Día 1 completado, Día 2 habilitado
- `"completo"`: Checklist completo (Día 1 + Día 2)

## Variables Clave

```python
HIPODROMOS = {
    "San isidro": {"color": "#2E7D32", "nombre": "SAN ISIDRO"},
    "La plata": {"color": "#1565C0", "nombre": "LA PLATA"},
    "Palermo": {"color": "#F9A825", "nombre": "PALERMO"}
}

COLORS = {
    "bg": "#111827",      # Fondo principal
    "fg": "#F9FAFB",      # Texto
    "accent": "#8B5CF6",   # Violeta (botones activos)
    "card": "#1F2937",     # Tarjetas
    "card_soft": "#273449", # Tarjetas suaves
    "surface": "#0F172A",  # Superficie
    "border": "#334155",   # Bordes
    "hover_soft": "#334155",
    "hover_accent": "#7C3AED",
    "muted": "#9CA3AF",   # Texto secundaria
    "success": "#10B981",  # Verde
    "warning": "#F59E0B",  # Amarillo
    "danger": "#EF4444",   # Rojo
    "info": "#06B6D4"    # Cyan
}
```

## Compilación

```bash
python -m PyInstaller ChecklistHipodromos.spec --clean
```

## Notas para Desarrollos Futuros

1. **No agregar command callbacks complejos**:
   - Si necesitás lógica al hacer click, usar el botón GUARDAR
   - No depender de los checkboxes para lógica en tiempo real

2. **Cuidado con trace_add**:
   - Los traces pueden causar loops si modificas la variable dentro del trace
   - Siempre verificar que no haya recursión infinita

3. **Debug temporal**:
   - Usar print() o sys.stderr temporario durante desarrollo
   - Limpiar antes de compilar para producción

4. **Ventana fija**:
   - El tamaño es fijo (940x395) para mantener layout
   - Si se necesita resizable, recalcular posiciones