# Validacion de la version 2.1.0

## Correcciones verificadas

La revision externa de Claude identifico un fallo real en 2.0.0: la restauracion
de documentos cambiaba LF por CRLF en Windows. Se reprodujo con el codigo publicado.
Las pruebas anteriores se habian ejecutado antes de normalizar los saltos de linea
del paquete; su resultado no demostraba que el ZIP final restaurase los bytes.

2.1.0 escribe texto nuevo con LF y respalda/restaura bytes originales, incluyendo
CRLF y BOM existentes, tanto en documentos como en preferencias y project.json.
La verificacion de esta version se ejecuta desde el ZIP extraido, despues de
normalizar y empaquetar. No se reutiliza el resultado anterior como evidencia.

El SDK Google se comprueba antes de construir el cliente: una version distinta
de google-genai==2.22.0 genera instrucciones de instalacion y no un AttributeError.
Si falta su configuracion de Interactions, se cierra el cliente sin generar.
El diagnostico lee Codex y Claude Code por separado (user/local/project), no imprime
credenciales y distingue registro de comprobacion del transporte y de Resolve.
Registrar JSON de MCP no requiere guion; las consultas de conexion y APIs si.

## Pruebas locales

23 pruebas funcionales, sin claves reales ni llamadas a proveedores:

- Ausencia de guion, plantilla incompleta y cambio sin confirmar bloquean APIs.
- «Usa el guion por defecto» activa el guion profesional mediante el comando real,
  conserva el brief tecnico y registra la eleccion sin otra confirmacion.
- Un guion propio existente no se sobrescribe; otro video requiere elegir el suyo.
- Puertas de Gemini, Omni, imagenes y consulta de Resolve antes de usar servicios.
- Confirmacion de revisiones, rechazo de cambios concurrentes y persistencia del perfil.
- Restauracion byte por byte tras fallo: documentos, plantillas, BOM, LF/CRLF y estado.
- Instalacion Codex/Claude, copia de respaldo e idempotencia; MCP conserva otros ajustes.
- Diagnostico Claude independiente de Codex, scopes correctos y secretos omitidos.
- SDK incompatible detectado antes del cliente; capacidad faltante cierra el cliente.
- HTTP 429 simulado con el SDK real: un solo envio, sin reintento automatico.
- Analisis simulado usa el guion principal y limpia la entrada remota en exito/fallo.
- Omni e imagenes simulados respetan intentos, costes estimados y recursos unicos.

Resultado en Windows con Python 3.14.2 y google-genai 2.22.0: **23/23 aprobadas**.
Con Python 3.11.15 sin google-genai: **22 aprobadas y 1 omitida**, indicando como
instalar el SDK. La prueba omitida es la integracion con el SDK real; no se cuenta
como aprobada. La deteccion de versiones incompatibles tambien usa casos simulados.

Prueba de medios real y local: clip sintetico recortado a cuatro segundos,
120 fotogramas a 30 fps, audio presente, fuente intacta. El formulario Windows
con guion pendiente termina antes de abrir el campo de clave o consultar Google.
FFmpeg se obtiene de imageio-ffmpeg; no necesita estar en PATH para este helper.

Verificaciones adicionales: sintaxis Python, frontmatter de skill, enlaces internos,
contenido del ZIP, manifiesto SHA-256 y ausencia de claves/rutas personales.

## Limites

No se llamo a APIs audiovisuales ni se consumieron creditos para esta actualizacion.
El analisis Gemini, la conexion Resolve y una generacion Omni reales pertenecen
al flujo de origen, antes de empaquetar; no son pruebas nuevas de 2.1.0.

Claude informo instalacion y registro user de la version anterior en una sesion
real. El diagnostico local tambien encuentra ese registro; no demuestra que se
haya probado el puente de Resolve desde Claude. «Connected» del servidor MCP
no equivale a respuesta de la API de la aplicacion.

No se ha completado una instalacion desde cero en otro equipo, macOS/Linux ni una
edicion real con la version 2.1.0 en Claude. El acceso efectivo depende del entorno,
cuentas, permisos y capacidades presentes. Las herramientas externas dependen
de que el asistente siga SKILL.md: el gate no es una barrera de seguridad del sistema.
Los presupuestos controlan estimaciones locales, no el limite de facturacion del proveedor.

## Repetir

Desde el paquete extraido, con Python >=3.11:

```text
python tests/test_workflow.py
```

Para incluir la prueba del SDK, usar un entorno aislado con:

```text
python -m pip install -r requirements-media.txt
python tests/test_workflow.py
```

Sin google-genai las pruebas locales siguen funcionando y solo se omite la prueba
del SDK. No se requieren claves ni acceso a proveedores. El instalador, el estado
del proyecto y el registro de MCP usan la biblioteca estandar de Python.
