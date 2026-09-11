# DaVinci Video Pro 2.0

Skill portable para **Codex local y Claude Code**, pensada para guiar a una persona
desde la configuracion de Resolve hasta un video completo exportado.

**Primero el guion.** Antes de editar o llamar APIs, el asistente pide el guion
del usuario y lo usa como fuente principal. Si falta, prepara un borrador con sus
indicaciones y espera confirmacion. Una plantilla vacia no permite continuar.

## Instalacion sencilla

Repositorio: [DamianDTM/davinci-video-pro](https://github.com/DamianDTM/davinci-video-pro).
Paquete descargable: [version 2.0.0](https://github.com/DamianDTM/davinci-video-pro/releases/tag/v2.0.0).

Para instalar desde GitHub, copia esto en **Codex local o Claude Code**:

> Instala DaVinci Video Pro desde https://github.com/DamianDTM/davinci-video-pro,
> version v2.0.0. Lee su README e instala la skill para el asistente que estoy
> usando. Despues aplicala para configurar DaVinci Resolve, su MCP y Gemini.
> Primero pideme el guion y usalo como fuente principal antes de editar o llamar APIs.

La carpeta de la skill es `skills/davinci-video-pro`. El asistente puede instalarla
desde esa ruta con su instalador de skills o descargar el paquete completo y usar
install.py. Si descarga un ZIP, descomprimirlo antes de ejecutar el instalador.
La instalacion local de la skill no requiere proporcionar una clave de Google.

Tambien puedes descargar el ZIP manualmente:

Descomprime el paquete completo y abre esta carpeta con Codex o Claude Code.
Escribe:

> Instala DaVinci Video Pro de esta carpeta para el asistente que estoy usando.
> Despues aplicala para configurar mi flujo de video. Primero pideme el guion
> y guíame cuando necesites que haga algo en mi computadora.

El asistente ejecuta con Python 3.11 o posterior uno de estos comandos:

```text
python install.py --client codex
python install.py --client claude-code
```

`--client both` instala para ambos cuando se solicita. `--update` conserva copia
de la skill anterior antes de actualizar; revisar cambios locales primero.
El instalador copia la skill localmente y no llama APIs, guarda claves ni instala
Resolve por su cuenta. La skill dirige esas fases despues de recibir el guion.

Una vez instalada, pedir «Quiero editar un video con DaVinci» o invocarla con
`$davinci-video-pro` en Codex o `/davinci-video-pro` en Claude Code.
Si no aparece, abrir otra sesion o recargar el cliente.

## Que incluye

- Instalacion guiada y comprobada del MCP de Samuel Gursky, segun el cliente.
- Ruta de referencia Windows/Resolve Free 21.0.3.7 y MCP 2.224.1; se comprueba
  compatibilidad actual y se reutilizan instalaciones que ya funcionan.
- Gemini 3.8 Flash para comprender imagen, voz y contenido.
- Omni 1.1 Flash para escenas de perspectiva alternativa, con plan acotado,
  registro de intentos y revision de sincronizacion, apariencia y fondo.
- Imagenes OpenAI mediante herramienta nativa cuando exista o helper API opcional
  para Claude y otros hosts con clave propia. No incluye cuentas ni creditos.
- Guion creativo y brief tecnico separados, editables y con historial.
- Resumen de comentarios y confirmacion antes de actualizar ambos documentos
  y las preferencias generales para proximos videos.
- Subtitulos con enfasis, limpieza del discurso, recursos unicos, CTA, transiciones,
  lista de tareas y entrega de MP4 completo, proyecto con medios y SRT.

## El segundo video y los nuevos chats

Cada video tiene su propia carpeta. Las preferencias generales confirmadas viven
en `~/.davinci-video-pro/templates`, compartidas por Codex y Claude. El instalador
no las reemplaza. Cambiar esta ubicacion con DAVINCI_VIDEO_PRO_HOME si se necesita.

En un nuevo chat del proyecto: «Continua mi video leyendo el estado guardado».
Para otro video: «Quiero editar otro video con mis preferencias. Mis materiales
estan en [carpeta]. Este es el nuevo guion: ...».

## Alcance comprobado

El flujo de origen uso Windows, Resolve, Gemini y una generacion Omni real.
Los scripts nuevos se verifican localmente con servicios simulados, sin gastar
creditos. Ver [VALIDACION.md](VALIDACION.md) para resultados y limites.
La instalacion nueva en otro equipo, macOS/Linux y una sesion real de Claude
requieren comprobacion en ese destino. Un chat web aislado no controla Resolve
local solo por recibir el ZIP. En Claude Desktop/Cowork se necesitan capacidades
locales y MCP compatibles; este paquete apunta a Claude Code.

Para una instalacion sin Python, el asistente debe localizar un runtime incluido
en su app o guiar la instalacion oficial. Las claves se introducen localmente.
La generacion y el analisis pueden consumir credito del proveedor elegido.

## Compartir y mantener

Esta carpeta esta preparada para un repositorio dedicado. Contiene instrucciones,
scripts y plantillas; los proyectos personales se crean fuera de ella. No incluye
instaladores propietarios, credenciales ni medios de usuarios. Las referencias
enlazan las descargas oficiales. Las versiones descargables se publican en Releases.

Los archivos siguen el formato abierto Agent Skills; no requieren un plugin
especifico de un solo proveedor. Puede agregarse distribucion como plugin despues.

Fuentes: [Skills Codex](https://learn.chatgpt.com/docs/build-skills),
[Skills Claude](https://code.claude.com/docs/en/skills),
[MCP Resolve](https://github.com/samuelgursky/davinci-resolve-mcp).
