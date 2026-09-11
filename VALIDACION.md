# Validacion de la version 2.0.0

Fecha de preparacion: 10 de septiembre de 2026.

## Comprobaciones locales

14 pruebas funcionales automatizadas con servicios simulados:

- Puerta del guion: rechaza ausencia, plantilla vacia y modificaciones sin confirmar.
- Gemini models/check se detienen antes de crear un cliente o leer una clave si falta guion.
- Omni, OpenAI Images y configuracion MCP de Claude respetan la misma puerta.
- Gemini recibe el guion principal y retira el archivo remoto simulado incluso ante fallo.
- Omni registra un intento unico, respeta el plan estimado y limpia entradas en exito/fallo.
- El SDK real recibe un HTTP 429 simulado y no repite la generacion automaticamente.
- Imagenes realiza una sola peticion simulada y no registra credenciales.
- Confirmacion obligatoria del resumen; ambos documentos se actualizan juntos.
- Un fallo de escritura restaura los documentos; una revision obsoleta no sobrescribe cambios.
- Preferencias generales se heredan; guion y presupuesto del video anterior no se heredan.
- Instalacion para Codex y Claude Code en sus respectivas rutas de proyecto.
- Reinstalacion idempotente, deteccion de cambios existentes y backup al actualizar.
- Configuracion MCP de Claude conserva otros servidores y ajustes.

Prueba de medios local: se crea un clip sintetico, se recorta a cuatro segundos,
se comprueban 120 fotogramas a 30 fps, audio presente y fuente sin cambios.
El formulario Windows se prueba con guion pendiente: termina antes de mostrar
el campo de clave o consultar Google.

Validacion adicional: sintaxis Python/PowerShell, frontmatter de la skill, enlaces
internos, ausencia de claves/rutas personales y contenido del ZIP.

## Limites de estas pruebas

No se llamo a APIs de generacion para validar esta actualizacion ni se consumieron
creditos. Las pruebas de servicios usan respuestas simuladas. La conexion con
Resolve, el analisis Gemini y una generacion Omni reales se probaron en el flujo
de origen, antes de empaquetar esta version.

No se ha completado una instalacion desde cero en otra computadora, una sesion
real de Claude Code usando este paquete ni una generacion real con el helper
opcional de OpenAI Images. Compatibilidad de formato y scripts comprobada localmente;
el acceso efectivo depende de cuentas, herramientas y permisos en el destino.
Windows es la ruta comprobada. macOS/Linux requieren adaptar y probar instalacion.

El control de guion de los helpers es una comprobacion de flujo, no una barrera
de seguridad del sistema. Las herramientas MCP/nativas externas dependen tambien
de que el asistente siga SKILL.md. Los presupuestos limitan estimaciones locales,
no configuran un limite duro de facturacion del proveedor.

## Repetir pruebas

```text
python tests/test_workflow.py
```

Requiere google-genai==2.22.0 instalado; no requiere claves ni acceso a proveedores.
El instalador y el manejo de proyectos usan solo la biblioteca estandar de Python.
