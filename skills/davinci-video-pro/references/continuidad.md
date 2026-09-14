# Documentos, encargo y continuidad

Python >=3.11. Estos comandos solo operan archivos locales. Resolver rutas absolutas.
La instalacion y las pruebas tecnicas de conexion no requieren guion ni brief.
Antes de producir, ambos documentos deben estar elegidos, leidos y vigentes.

## Inicializar y mostrar los archivos

```text
python <skill>/scripts/workflow.py --project-dir <encargo> init
python <skill>/scripts/workflow.py --project-dir <encargo> documents
python <skill>/scripts/workflow.py --project-dir <encargo> status
```

init no sobrescribe proyectos: crea documentos, tareas, estado, comentarios,
carpetas y AGENTS.md/CLAUDE.md para nuevos chats. Si ya hay documentos sin estado,
conservarlos y elegir otra carpeta para inicializar. Un encargo puede contener
varias salidas identificadas en ENCARGO.md; crear montajes y exports separados.

documents devuelve rutas absolutas existentes: guion de trabajo, copia editable
del predeterminado y brief. Mostrar SIEMPRE las rutas al usuario como enlaces
locales cuando sea posible. No enviar rutas de ejemplo ni pedir editar el paquete.
La copia GUION-POR-DEFECTO.md se crea una sola vez; documents no elimina sus cambios.
Una vez elegido, GUION-CREATIVO.md es el archivo activo para siguientes ediciones.

Las plantillas generales viven en DAVINCI_VIDEO_PRO_HOME o ~/.davinci-video-pro/templates.
Codex y Claude comparten ese perfil. Otro equipo necesita su propia copia.
Un nuevo encargo hereda estilo, sin autorizaciones de gasto ni discurso anterior.

## Elegir guion y brief sin preguntas repetidas

Si tiene guion propio, conservar su fuente y colocar el contenido en GUION-CREATIVO.md.
Si elige nuestro guion o dice que no tiene, activar la copia editable predeterminada.
«Hazlo con el de defecto» es suficiente; mostrar su ruta y continuar.
Un borrador nuevo personalizado se muestra y confirma antes de usarlo.

```text
python <skill>/scripts/workflow.py --project-dir <encargo> use-default-script --confirmation <respuesta-real>
python <skill>/scripts/workflow.py --project-dir <encargo> confirm-script --confirmation <respuesta-real>
python <skill>/scripts/workflow.py --project-dir <encargo> confirm-brief --source default --confirmation <respuesta-real>
python <skill>/scripts/workflow.py --project-dir <encargo> gate
```

Elegir use-default-script O confirm-script segun corresponda. Para un brief propio,
usar confirm-brief --source user despues de leer su copia de trabajo.
--confirmation registra la respuesta REAL que entrega o elige ese documento;
no exige un segundo «si» si ya lo eligio. «Ambos por defecto» permite registrar los
dos con esa respuesta. Nunca inventar una respuesta que todavia falta.

gate comprueba los hashes de ambos documentos, su contenido y ausencia de una
transaccion interrumpida. Cambiar un archivo invalida su eleccion vigente. Si el
usuario dice «ya lo edite, usalo», leer los cambios y registrar esa instruccion;
no reiniciar la instalacion. Para cambios propuestos por la IA usar la revision
confirmada siguiente. Los helpers no garantizan calidad por si solos: la IA debe
leer, ejecutar y comprobar todos los criterios tecnicos.

Al retomar un proyecto de una version anterior, no destruir documentos ni su
historial. Si falta brief_approval, leer el brief y registrar una eleccion real
previa si consta; si no, preguntar solo por esa eleccion, mostrando su ruta.
Revisar instrucciones de continuidad generadas por versiones anteriores que aun
exijan guion para conexiones; actualizar ese texto generado al orden de 2.2,
conservando instrucciones personales ajenas. Guardar la migracion en ESTADO.md.

## Guardar la recepcion

Seguir flujo-guiado.md e intake.py: inventario local, seleccion concreta, numero
de videos finales y distribucion, documentos, Omni e imagenes. ENCARGO.md guarda
las elecciones y .davinci-video-pro/intake.json su registro. Reutilizarlo al retomar.
Si cambian documentos, verificar la coherencia del plan, actualizarlo con las
respuestas existentes y conservar el historial; no repetir todas las preguntas.
Conservar tambien support_files, music y los textos publication de cada salida.
Conservar reference_videos con su uso on_screen/style; no convertir un ejemplo
de estilo en un clip insertado al abrir otro chat.
Al retomar leer RECURSOS.md y PUBLICACION.md si existen: revision validada,
capturas, pistas elegidas y estado/id por red. Actualizar intake no debe convertir
datos antiguos en permisos nuevos. Nunca reintentar una subida sin consultar su estado.

## Rondas de comentarios

Guardar comentarios en CAMBIOS-PENDIENTES.md mientras se ejecuta trabajo autorizado.
Al cerrar la ronda, preparar ambos documentos candidatos y resumir por documento
y alcance: video actual o preferencias generales. Mostrar el resumen, preguntar
si es correcto y esperar respuesta antes de consolidar. No generalizar discursos,
nombres, marcas ni CTA concretos de un video.

```text
python <skill>/scripts/workflow.py --project-dir <encargo> stage-revision --creative <guion-candidato.md> --technical <brief-candidato.md> --summary-file <resumen.md>
python <skill>/scripts/workflow.py --project-dir <encargo> apply-revision --confirmation <respuesta-real>
```

Si hay correcciones antes de confirmar, conservar/archivar la propuesta y preparar
el resumen actualizado. Para guardar preferencias futuras, agregar a stage-revision
--profile-creative y --profile-technical con las dos plantillas generales.
Conservar PENDIENTE_DE_GUION en la plantilla creativa y su seccion «Preferencias
creativas reutilizables»: se incorpora al crear la copia del guion predeterminado.
La preferencia tecnica vive en BRIEF-TECNICO.md. Actualizar el paquete no pisa el perfil.

Se comprueban cambios concurrentes, se respaldan bytes originales en history,
se actualizan ambos documentos y se registran sus hashes vigentes. Cada documento
recibe sus cambios pertinentes; no inventar modificaciones para forzar una diferencia.

Si existe transaction.json tras una interrupcion, detener produccion, leer el
historial y restaurar documentos y project-before.json o completar la revision
comprobada. Conservar evidencia hasta verificar. Guardar tareas, rutas y siguiente paso.
