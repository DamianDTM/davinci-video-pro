# Validacion de la version 2.3.0

## Cambios y alcance

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

33 pruebas funcionales sin claves reales ni llamadas a proveedores:

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

Windows, Python 3.14.2 con google-genai==2.22.0: **33/33 aprobadas**.
Python 3.11.15 sin google-genai: **32 aprobadas y 1 omitida** con instrucciones
de instalacion. La prueba omitida corresponde al SDK real, no se cuenta como aprobada.

Las comprobaciones se ejecutan desde el ZIP extraido despues de empaquetarlo:
manifiesto SHA-256, pruebas, metadatos de skill y prueba de medios. Esta ultima
recorta un clip sintetico a cuatro segundos, verifica 120 fotogramas a 30 fps,
audio y fuente intacta con guion y brief elegidos. El formulario Windows se valida
con -ValidateOnly, sin guion, sin abrir ventana ni llamar a Google.
Tambien se revisan sintaxis, enlaces internos y ausencia de claves/rutas personales.

## Limites

No se llamo a APIs audiovisuales ni se consumieron creditos en esta actualizacion.
El flujo real anterior probo Resolve, Gemini y una generacion Omni; no constituye
una prueba nueva de edicion completa con 2.3.0.

El usuario probo la version anterior en Claude y sus comentarios originaron esta
actualizacion. No se ha ejecutado una nueva instalacion desde cero en otro equipo,
una edicion real con 2.3.0 en Claude, ni una prueba interactiva nueva del formulario.
Su entrada oculta y verificacion de catalogo se conservan; la comprobacion nueva
del formulario solo valida parametros sin interfaz ni red.

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
