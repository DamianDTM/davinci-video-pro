# Instalación guiada

## Primera etapa: instalar y conectar

Seguir flujo-guiado.md: preguntar si ya posee Resolve instalado y el puente
configurado; reutilizar lo que ya confirmo. Si desconoce version/edicion o estado,
revisarlo localmente. Mostrar una version compatible concreta y preguntar
por instalarla si falta o hay que cambiarla, preservando proyectos y autorizaciones
previas. No pedir guion ni brief para instalar o probar conexiones.

Las pruebas tecnicas de autenticacion, modelos, texto minimo y version/proyecto
de Resolve estan permitidas en esta fase. Analizar materiales, generar recursos
y editar requieren despues guion y brief tecnico elegidos y workflow.py gate.
diagnose.py sin --check-connection solo lee datos locales. Ver clientes.md.

## Sin acceso para revisar el equipo: modo guiado

Comprobar si las herramientas disponibles realmente acceden al equipo del usuario.
Una terminal en la nube no demuestra el sistema ni los programas de su ordenador.
Si no hay acceso local, no insistir con diagnosticos imposibles ni detenerse en
«no puedo revisar». Continuar asi, reutilizando todo dato ya conocido:

1. Pedir sistema operativo y arquitectura si faltan, y si Resolve esta instalado.
   Si existe pero desconoce version/edicion, indicar Ayuda > Acerca de DaVinci Resolve
   y pedir el texto de version y si dice Studio. No exigir este paso si no lo tiene.
2. Recomendar una version y edicion concretas para el sistema indicado y explicar
   la compatibilidad con el MCP. Dar un enlace oficial clicable y los pasos de
   descarga/instalacion; no limitarse a «busca una version compatible».
3. Para Windows estandar y la via gratuita, la referencia probada es DaVinci Resolve
   21.0.3, compilacion 7 (21.0.3.7). [Formulario oficial de descarga para Windows](https://www.blackmagicdesign.com/support/download/f549d6da20df4cc98f57d4777d8c8a03/Windows).
   Nombre, compilacion y plataforma se verificaron el 11-09-2026 en el
   [catalogo oficial](https://www.blackmagicdesign.com/api/support/us/downloads.json).
   El formulario requiere registro; no es el ZIP ni el instalador de Studio.
   Confirmar arquitectura antes de dar este enlace como el instalador adecuado;
   Windows ARM, macOS y Linux requieren su opcion correspondiente del catalogo.
4. Si puede navegar, comprobar que enlace/version siguen disponibles y contrastar
   soporte actual del puente en el repositorio. Si no puede navegar, presentar
   la referencia fechada como previamente verificada, sin afirmar haber comprobado
   disponibilidad actual. Si el enlace falla, dar el
   [centro oficial de soporte](https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion)
   e indicar buscar «DaVinci Resolve 21.0.3 Update» y seleccionar el sistema adecuado.
   No sustituirla automaticamente por la ultima Free: comprobar primero el puente.
5. Indicar completar el formulario, descargar, extraer y ejecutar el instalador;
   aceptar los permisos necesarios, abrir Resolve y comunicar la version instalada.
   Para una instalacion existente, conservar proyectos antes de proponer un cambio.
   Si no puede abrir el instalador por el usuario, explicar exactamente ese paso.
6. Continuar con MCP y clave Google: automatizar lo que permita el acceso disponible
   o dar los comandos locales de esta guia para el cliente/sistema correctos.
   La clave se introduce en el formulario local o almacen de secretos; nunca en
   el chat, aunque el asistente no tenga acceso. No afirmar que quedo guardada
   o conectado sin evidencia. Terminar con el siguiente paso concreto del puente.

Este modo permite orientar desde un chat sin acceso local. Controlar Resolve y
comprobar su conexion requieren despues un asistente/cliente conectado al equipo,
o que el usuario ejecute las comprobaciones y comunique resultados sin secretos.
Guardar version recomendada, enlace, fecha/fuente y estado pendiente o comprobado.

## Alcance y comprobación inicial

Ruta probada: Windows, Codex local, Resolve Free 21.0.3.7 y MCP 2.224.1.
Es una referencia de compatibilidad comprobada el 10 de septiembre de 2026,
no una instrucción de fijar esa versión para siempre. Confirma la documentación
actual del [repositorio](https://github.com/samuelgursky/davinci-resolve-mcp)
antes de instalar o cambiar versiones. Para sintaxis de APIs o CLI usa Context7
si está disponible; después consulta el código y las fuentes oficiales.

Ejecuta `scripts/diagnose.py --client <codex-o-claude-code> --project-dir <trabajo>`
con Python 3.11 o posterior. Sin --check-connection es de solo lectura local.
El informe separa registros por cliente; no usa la configuracion de Codex como
prueba de que Claude esta registrado. FFmpeg puede estar en PATH o incluido en
imageio-ffmpeg: prepare_clip.py utiliza este ultimo; su ausencia en PATH no basta
para declarar que falta FFmpeg.
Si Codex ofrece `load_workspace_dependencies`, localiza allí Python antes de
pedir que lo instalen. Registra sistema, Resolve, versión, edición comprobada o
desconocida, Git/Python/Node, instalación MCP, clave presente (solo booleano) y
estado de conexión. No imprimas el entorno ni config.toml o bridge.json completos.

No solicites a una persona nueva todas estas comprobaciones manuales.
Si la edición no se puede determinar, pide que mire Ayuda > Acerca de DaVinci Resolve.
En macOS/Linux no uses los scripts PowerShell: adapta con la documentación del
repositorio. La instalación de esos sistemas no fue probada con este paquete.

## Elegir una vía compatible

| Situación real | Siguiente paso |
| --- | --- |
| Resolve Studio con scripting disponible | Preferencias > Sistema > General > External scripting using: Local. Reiniciar si Resolve lo requiere y comprobar API. |
| Free 21.0.x | Reutilizar el puente existente; instalarlo solo si falta. Activarlo desde Workspace > Scripts > resolve_bridge con un proyecto abierto si aun no responde. |
| Free 21.1 o posterior | Comprobar soporte actual. El README consultado indica que 21.1 restringe Python a Studio. No insistir con el mismo puente ni prometer que funcionará. |
| Resolve ausente | Encontrar un instalador oficial compatible con edición, sistema y puente elegido; guiar su instalación y comprobar versión al terminar. |
| Ya hay conexión funcional | Reutilizarla; omitir reinstalaciones y cambios de versión. |

Para cambiar una versión, confirma si hay proyectos que conservar. Si los hay,
prepara y verifica exportación de proyectos y copia de biblioteca antes de proponer
el cambio concreto. No desinstales ni abras una biblioteca nueva con una versión
antigua sin compatibilidad comprobada. No elimines bibliotecas. No compres Studio.
Descargas: [soporte oficial de Blackmagic](https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion).
El registro, la descarga, el instalador y un diálogo de Windows pueden requerir al usuario.
Explica esa acción justo cuando haga falta. No rellenes identidad o datos de contacto inventados.

## Instalar el MCP

Antes de descargar, clonar, registrar o ejecutar el instalador del puente,
comprobar lo que ya existe: MCP del cliente actual, checkout/rutas configuradas
y script del puente en Resolve. Preguntar solo los datos que no puedan revisarse.
Resolver la ruta real; no crear otro checkout ni otra copia del puente porque
se abrio otro chat. No ejecutar install_resolve_bridge.py si ya esta instalado
y compatible. Si esta detenido o Resolve cerrado, activar/abrir y volver a probar.
Si solo falta el registro en Codex o Claude, completar ese registro reutilizando
el servidor y puente existentes. Ante una averia o incompatibilidad demostrada,
diagnosticar y reparar lo necesario, conservando configuracion y personalizaciones.

Descubre primero herramientas instaladas de Resolve. Si responden, comprueba su
versión y reutiliza la conexión. Si solo falta exponer el servidor en esta sesión,
guarda el estado y pide recargar Codex después de configurar.

Para una instalación nueva preferir un checkout identificable por usuario:
`<directorio de configuración del cliente>/integrations/davinci-resolve-mcp`.
Obten ese directorio del perfil local del cliente elegido, nunca de este paquete.
Si existe un checkout, verifica su remoto y estado. No hagas reset, pull forzado
ni actualizaciones de una instalación funcional.

Secuencia del instalador oficial verificada en el código 2.224.1:
```text
git clone https://github.com/samuelgursky/davinci-resolve-mcp.git <repo>
<python> <repo>/install.py --help
<python> <repo>/install.py --clients codex
<python-del-venv-del-repo> <repo>/scripts/install_resolve_bridge.py
```

Ejecuta install.py con el repositorio como directorio de trabajo solo cuando
corresponda instalar/configurar componentes pendientes. La última línea es para
un puente que falta en Free compatible o cuando se ha elegido explícitamente esa
via; omitirla si ya existe y funciona. No ejecutar la secuencia entera al reconectar.
El instalador crea su entorno y combina la entrada de Codex. Examina los flags
actuales antes de usarlos; no inventes --skip-test o --no-update-check.
Los identificadores comprobados son `codex` y `claude-code`; selecciona el cliente solicitado. Para Claude Code lee clientes.md: el instalador upstream escribe .mcp.json en su cwd. No configures `all`.
Si no hay Git pero hay Node, la alternativa oficial es
`npx davinci-resolve-mcp setup --clients codex`. Descubre la ruta administrada
que produzca, en vez de asumir que coincide con el checkout anterior.

Antes de cambiar config.toml, haz una copia con nombre nuevo. Verifica después
solo la entrada MCP pertinente, intérprete, script y existencia de los archivos;
preserva los demás servidores y ajustes. El registro de configuración no es
todavía una conexión. Usa rutas absolutas del equipo destinatario.

Configura allowed_media_roots y allowed_output_roots únicamente para las carpetas
necesarias según la documentación vigente. Nunca desactives restricciones ni
autenticación para arreglar un problema de rutas. Usa un directorio de exportación
admitido o agrega el directorio concreto autorizado.

## Configurar la clave propia de Google

Despues de instalar los componentes, seguir gemini.md: comprobar si ya hay clave
local; si falta, preguntar si tiene una de AI Studio y ofrecer la entrada local
oculta. No pedir que la pegue en el chat. Verificar autenticacion y modelo sin
subir videos. No confundir guardar la clave con una conexion comprobada.

## Activar y verificar el puente Free

Explicación al usuario: "Abre Resolve, abre o crea un proyecto y ve a
Workspace > Scripts > resolve_bridge. Cuando termine, dime listo."
Si no aparece, diagnostica antes de repetir: versión/edición, instalación de Python,
carpeta de scripts y reinicio de Resolve. El instalador incorpora un canario Lua
para distinguir Python no detectado de una carpeta incorrecta.

El puente escucha solo en loopback y usa autenticación propia. No publiques su
puerto, copies su token o reutilices bridge.json de otro equipo. No mates procesos
por nombre: identifica primero el dueño del puerto y conserva el trabajo abierto.

Prueba una consulta de versión y proyecto actual mediante el MCP.
También puedes ejecutar:
```text
<python> <skill>/scripts/diagnose.py --client <codex-o-claude-code> --repo <repo> --project-dir <trabajo> --check-connection --output <trabajo>/diagnostico.json
```
El cliente directo usa `connect(require_enabled=False, timeout=15)` y llama
GetVersionString/GetProjectManager. Una respuesta autenticada demuestra transporte;
un proyecto actual demuestra además que hay un contexto de trabajo.
Si solo funciona el cliente directo pero no aparecen las herramientas MCP,
informa de esa diferencia y termina el registro/recarga de Codex.

No marques la conexión como lista solo porque se importa DaVinciResolveScript,
el servidor arranca o el usuario dice que ya abrió Resolve.

## Estado para retomar

Guardar en ESTADO.md: sistema y versiones observadas, ruta del repo y Python,
ruta de configuración sin su contenido secreto, vía Studio/puente, estado de
las consultas, último error seguro y siguiente clic pendiente.
Al reconectar, prueba primero la conexión: no repitas la instalación.

Una vez comprobados Resolve y Gemini, pasar directamente a flujo-guiado.md:
carpeta/seleccion, cantidad de videos, brief, guion, Omni e imagenes. Reutilizar
cualquier dato ya recibido. Mostrar las rutas editables reales de ambos documentos.
