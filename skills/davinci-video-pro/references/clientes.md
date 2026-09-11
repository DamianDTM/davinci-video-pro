# Codex y Claude

La compatibilidad operativa de este paquete es Codex local y Claude Code con
acceso al mismo equipo que ejecuta Resolve. El formato SKILL.md es compartido.
Un chat web aislado puede leer instrucciones, pero no controla por eso el Resolve
local. En Claude Desktop/Cowork solo ejecutar el flujo si existen acceso local,
ejecucion de scripts y MCP compatibles; esa superficie no se ha probado aqui.

Sin acceso al equipo, ofrecer el modo guiado de instalacion.md: recomendacion de
version para el sistema conocido, enlace oficial y siguiente paso manual. No
afirmar que se detecto, descargo, instalo o conecto algo desde un chat aislado.
Pedir solo los datos que no puedan comprobarse; no bloquear la orientacion por
carecer de terminal, permisos o navegador.

## Instalar la skill

Desde la carpeta completa descargada, con Python >=3.11:

```text
python install.py --client codex
python install.py --client claude-code
python install.py --client both
```

Elegir solo los clientes solicitados. El instalador copia archivos y no consulta
APIs, instala Resolve ni guarda claves. Codex: CODEX_HOME/skills cuando esta
definido; si no, ~/.agents/skills. Claude Code: ~/.claude/skills.
Para un proyecto: --scope project --project-dir <ruta>, usando .agents/skills o
.claude/skills. Para una instalacion existente en otra ruta, usar --skills-dir.
No mantener dos copias activas de la misma skill en rutas de un mismo cliente.

--update conserva una copia fuera de las carpetas de descubrimiento antes de
reemplazar la skill. Revisar primero cambios locales. Las preferencias personales
se guardan fuera del paquete y permanecen intactas al actualizarlo.

Codex puede seleccionarla por descripcion o con $davinci-video-pro. Claude Code
puede seleccionarla por descripcion o con /davinci-video-pro. Si no aparece,
abrir otra sesion/recargar. No prometer activacion automatica en todas las frases.

## Configurar el MCP correcto

Registrar una entrada local no usa APIs y no requiere guion, tanto mediante
configure_claude_mcp.py como mediante claude mcp add-json. Las pruebas tecnicas
de conexion y los instaladores pueden ejecutarse antes del guion y brief. La
produccion de medios requiere ambos documentos vigentes. El instalador upstream distingue codex,
claude-code y claude-desktop. Elegir el host real; nunca --clients all por defecto.

En la version comprobada, claude-code escribe .mcp.json en el directorio de trabajo
del instalador. Si se ejecuta desde el checkout del MCP, ese archivo NO registra
automaticamente el servidor para todos los proyectos de Claude.

Para Claude Code, preparar y validar la entrada upstream, y registrarla en scope
user con la CLI actual, o combinarla en .mcp.json del proyecto autorizado. Para
una entrada JSON preparada en archivo, scripts/configure_claude_mcp.py conserva
los otros servidores y hace backup. No copiar tokens ni rutas de otra persona.
Para disponibilidad entre proyectos, usar el scope user mediante el comando
claude mcp add-json documentado actualmente, pasando la entrada como argumento
de subprocess, sin shell ni imprimir valores secretos. Verificar claude mcp --help.

Diagnosticar el cliente elegido con diagnose.py --client claude-code --project-dir
<proyecto>, o --client codex. Sin seleccion explicita, el informe separa ambos.
Claude: scope user en ~/.claude.json, scope local bajo projects en ese archivo y
scope project en <proyecto>/.mcp.json. Para otro perfil usar --claude-config si hace
falta. No deducir el estado de Claude desde CODEX_HOME. El informe lee registros,
no demuestra transporte ni aprobaciones/permisos efectivos del cliente.

Comprobar por separado registro, arranque del servidor MCP y respuesta real de
Resolve. «Connected» en claude mcp list no demuestra que su API responda. Hacer
esas pruebas durante la instalacion sin guion. Despues continuar directamente
con la recepcion de flujo-guiado.md.

## Capacidades por cliente

Gemini y Omni usan scripts portables con la clave propia del usuario. Las
herramientas MCP se descubren por capacidad, sin fijar nombres internos de Codex.
Para imagenes seguir recursos.md: ImageGen nativo en Codex cuando exista;
en Claude conectar un proveedor de imagenes o recibir archivos. No fingir acceso
a la herramienta de imagenes de otro host ni sustituir video por una imagen.

Fuentes: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills),
[MCP Claude](https://code.claude.com/docs/en/mcp).
