# Validacion de la version 2.4.0

## Cambios y alcance

Esta revision incorpora recepcion opcional de HTML/CSS, PDF, documentos e imagenes,
con instrucciones de capturas fieles y resaltados segun el discurso. La musica se
elige mediante archivo/carpeta o ninguna; audios de voz y canciones se guardan
separados. No hay generacion musical de pago por defecto. El usuario valida
reproduciendo el montaje antes del export final. Al cierre se pregunta por
publicacion opcional en TikTok, YouTube, Facebook e Instagram con textos del brief
o aportados en ese momento. Se conserva la duracion objetivo elegida por el usuario.

intake.py inventaria y guarda support_files, music y los textos de cada salida;
no renderiza documentos ni publica. Las instrucciones de publicacion descubren
el acceso real del host y conservan decisiones/id/estado por destino en PUBLICACION.md.
No se incluye un conector social universal ni se configura OAuth de redes al instalar.

Se conserva de 2.3.2 la exigencia de preparar Omni desde imagen y audio corregidos,
incluidas las muestras. prepare_clip.py requiere un informe local de revision y
conserva hashes de montaje, fragmento, informe, guion y brief. omni_video.py rechaza
registros ausentes, antiguos, malformados o desactualizados antes de leer claves,
subir archivos o reservar un intento. Exige ambas pistas y registra el fragmento
corregido cuya voz debe restaurarse. El informe lo escribe el agente tras revisar;
no agrega una confirmacion del usuario ni certifica calidad perceptiva por si solo.

Se conserva de 2.3.1 la instalacion guiada sin acceso al equipo:
datos minimos, version recomendada, enlace oficial y siguiente paso manual. El
catalogo de Blackmagic se consulto el 11-09-2026 y confirma Resolve 21.0.3 build 7
para el formulario Windows incluido. Se distingue ese dato de comprobar el equipo
o ejecutar una instalacion. Sin navegador se comunica la fecha de referencia.
La actualizacion de esa guia no requirio pruebas que solo comprobaran su texto.

Omni elimina el presupuesto obligatorio de las instrucciones y los helpers.
Una respuesta real habilita un intento; despues se muestran video y coste y
se espera la decision sobre otro. El registro persiste entre chats; los planes
antiguos no habilitan lotes. Un reintento identico necesita una peticion explicita.
GASTOS-OMNI.md registra estimaciones con fuente/fecha, componentes parciales e
intentos de coste desconocido. No afirma conocer cargos reales de Google.

Se ordena el flujo en instalacion/conexion, recepcion y produccion. Las pruebas
tecnicas de conexion pueden ejecutarse sin guion ni brief por peticion expresa.
Analizar medios, generar recursos y editar requieren ambos documentos vigentes.

Se muestra siempre la ruta editable del guion y del brief. La copia predeterminada
puede editarse antes de elegirla; no se sobrescribe al volver a mostrar las rutas.
«Hazlo con el de defecto» o indicar que no tiene guion permite usar el profesional
sin otra confirmacion. El brief se elige por separado y es obligatorio.

La recepcion guarda seleccion explicita de videos, cantidad y objetivos de salidas,
audio opcional y elecciones Omni/imagenes en ENCARGO.md. No supone permiso para
subir archivos ni gastar; no sustituye la comprobacion final de cada export.

## Pruebas locales del paquete

40 pruebas funcionales sin claves reales ni llamadas a proveedores:

- Gemini models/check funcionan sin documentos mediante cliente simulado; no analizan medios.
- La consulta tecnica de Resolve funciona sin guion mediante puente simulado.
- Analisis se detiene antes de cliente/clave si falta guion o brief.
- Gemini, Omni, imagenes y preparacion de clips requieren el brief vigente.
- Cambiar el brief invalida produccion; una revision confirmada registra ambos hashes.
- Las rutas de documentos son absolutas y existen; el default editado por el usuario se conserva.
- «Hazlo con el de defecto» activa esa copia sin repetir confirmacion del guion.
- Inventario limitado a carpeta, subcarpetas explicitas, sin seleccionar ni subir automaticamente.
- Recepcion con varios exports y fuentes concretas; rechaza cantidad incoherente o fuentes ajenas.
- Instalacion Codex/Claude, backups, idempotencia y preservacion de ajustes MCP.
- Diagnostico independiente por cliente y scopes, sin imprimir secretos.
- Revisiones, cambios concurrentes y restauracion exacta de documentos, preferencias y estado.
- LF/CRLF/BOM se preservan en backups y rollback; el texto nuevo usa LF.
- SDK incompatible produce un error util antes de crear cliente.
- SDK real ante HTTP 429 simulado: una sola peticion, sin reintento.
- Gemini/Omni simulados limpian entradas en exito/fallo; imagenes e intentos no se duplican.
- Omni funciona sin presupuesto por CLI; otra generacion se bloquea antes de claves/subidas.
- Revisar la escena anterior y pedir otra habilita un intento; reintentos identicos son explicitos.
- Un plan de presupuesto antiguo no permite generar automaticamente.
- Costes por tokens/duracion, subtotales parciales y fallo incierto sin afirmar coste cero.
- Omni rechaza entradas sin registro, antiguas o malformadas sin consumir el intento.
- Cambiar montaje, fragmento, informe, proyecto o documentos invalida la revision.
- Una entrada sin imagen o sin audio se rechaza antes de claves y reserva.
- El intento completado conserva la revision y la ruta de la voz corregida a restaurar.
- Inventario de HTML/PDF/documentos e imagenes sin ejecutar/renderizar ni cambiar fuentes.
- Documentos opcionales, rutas seleccionadas exactas y rechazo de duplicados/tipos incorrectos.
- Musica separada de la voz; eleccion pendiente/ninguna/aportada sin habilitar generacion pagada.
- Titulo y descripcion con saltos de linea se preservan exactamente sin crear permiso de publicacion.

Windows, Python 3.14.2 con google-genai==2.22.0: **40/40 aprobadas**.
Python 3.11.15 sin google-genai: **39 aprobadas y 1 omitida** con instrucciones
de instalacion. La prueba omitida corresponde al SDK real, no se cuenta como aprobada.

Las comprobaciones se ejecutan desde el ZIP extraido despues de empaquetarlo:
manifiesto SHA-256, pruebas, metadatos de skill y prueba de medios. Esta ultima
recorta un clip sintetico a cuatro segundos, verifica 120 fotogramas a 30 fps,
audio y fuente intacta con guion y brief elegidos; tambien comprueba el registro
de entrada corregida y su informe. El formulario Windows se valida
con -ValidateOnly, sin guion, sin abrir ventana ni llamar a Google.
Tambien se revisan sintaxis, enlaces internos y ausencia de claves/rutas personales.

## Limites

No se llamo a APIs audiovisuales ni se consumieron creditos en esta actualizacion.
El flujo real anterior probo Resolve, Gemini y una generacion Omni; no constituye
una prueba nueva de edicion completa con 2.4.0.

El usuario probo la version anterior en Claude y sus comentarios originaron esta
actualizacion. No se ha ejecutado una nueva instalacion desde cero en otro equipo,
una edicion real con 2.4.0 en Claude, ni una prueba interactiva nueva del formulario.
Su entrada oculta y verificacion de catalogo se conservan; la comprobacion nueva
del formulario solo valida parametros sin interfaz ni red.

El nuevo flujo de capturas, musica y revision/publicacion es una instruccion del
asistente, no un motor visual o publicador autonomo incluido. No se ha probado
en esta actualizacion un render HTML real, una mezcla musical real ni publicaciones
en las cuatro redes. Las pruebas cubren inventario/registro sin servicios reales.
La fidelidad visual, sincronizacion y validacion del usuario requieren ejecutar
ese flujo con materiales reales; una cuenta conectada requiere verificacion propia.

El gate comprueba documentos y versiones, pero no garantiza calidad ni obliga a
un modelo a leer con atencion: el asistente debe aplicar el brief y verificar
auditiva/visualmente cada resultado. Las herramientas MCP/nativas externas dependen
tambien de seguir SKILL.md. El control Omni limita intentos por decision registrada,
no la facturacion del proveedor. Las estimaciones usan una tarifa de referencia
fechada y deben revisarse si cambia; los impuestos/descuentos/cargos reales no se
consultan. No se ha contrastado este calculo nuevo con una factura real.

«Connected» del cliente MCP y una clave guardada no prueban por si solos la
conexion real de Resolve ni la comprension audiovisual. Windows es la ruta de
referencia; macOS/Linux y otras superficies requieren comprobacion en su destino.

## Repetir

Desde el paquete extraido, Python >=3.11:

```text
python tests/test_workflow.py
```

Para incluir la prueba del SDK, usar un entorno aislado:

```text
python -m pip install -r requirements-media.txt
python tests/test_workflow.py
```

Sin google-genai, los casos de flujo siguen funcionando y la integracion del SDK
se omite de forma explicita. Las pruebas no requieren claves. Inventario, instalador,
estado y registro MCP usan la biblioteca estandar.
