# Validar, exportar y publicar si el usuario lo elige

La publicacion es una etapa OPCIONAL al terminar el video. Exportar crea un archivo;
publicar lo envia a una cuenta de una red social. Instalar esta skill no conecta
las cuentas ni concede permiso para publicar. No crear cuentas, apps de desarrollador,
suscripciones ni servicios de alojamiento por defecto.

## Primero mostrar el montaje

Tras el QA, decir por cada video el proyecto de Resolve, nombre exacto de timeline,
revision y como reproducirlo: abrir el proyecto, seleccionar esa timeline en Edit,
ir al inicio y usar el boton de reproduccion del visor (o el atajo configurado).
Ayudar a abrirlo con herramientas disponibles cuando sea posible. Si necesita
un archivo para revisarlo fuera de Resolve, crear una previsualizacion identificada
como tal y dar enlace/ruta y forma de reproducirla; no presentarla como export final.

Preguntar si el montaje esta aprobado o necesita cambios. Registrar la respuesta
real junto con timeline/revision en ESTADO.md; el QA del agente no es visto bueno
del usuario. Tras cambios materiales, mostrar la nueva revision. Solo exportar
como final la revision aprobada; reutilizar un «exporta estos videos» que identifique
los montajes revisados. Esta validacion final es obligatoria aunque un brief antiguo
limite las preguntas a la recepcion.

## Pregunta de entrega y textos

Tras validar, preguntar: «¿Quieres que exporte los archivos solamente o que tambien
los publique directamente en TikTok, YouTube, Facebook o Instagram? Indica las
redes/cuentas y el titulo y descripcion de cada video; si ya estan en tu brief,
usare esos textos». Si la respuesta anterior ya cubre esto, reutilizarla.

El titulo y descripcion deben venir del usuario, desde su brief o su respuesta
actual. No bloquear el montaje inicial si esos campos faltan: se piden al elegir
publicar. No inventar textos, hashtags, enlaces, etiquetas de cuentas ni menciones
para publicar. Si pide que la IA los redacte, preparar una propuesta y obtener su
aprobacion antes de usarla. Permitir una descripcion vacia si asi lo elige y la red
lo admite. Conservar literalmente el texto aprobado; adaptar formato solo sin
cambiarlo. Si una red no tiene campo de titulo separado, mostrar como quedaran
titulo y descripcion en su caption/texto y reutilizar esa eleccion en el envio.

Crear PUBLICACION.md desde [la plantilla](../assets/PUBLICACION.md) solo cuando
se elija publicar, preservando archivos previos. Registrar por video Y destino:
revision, MP4 verificado y hash, cuenta/canal/pagina, titulo y descripcion exactos,
portada si procede, visibilidad, publicar ahora o fecha/hora/zona elegidas, metodo,
respuesta que autoriza y estado. No asumir todas las redes ni todas las cuentas.
Los textos y permisos de publicacion de un video no se heredan a otro encargo.

Antes de enviar, mostrar el resumen concreto de archivo, cuenta, texto y visibilidad.
Una respuesta previa «publica ahora ...» que ya autoriza exactamente esos datos
basta: no pedir confirmacion repetida. Si faltan decisiones, agruparlas en una
consulta final con la propuesta completa. El visto bueno de edicion o elegir una
red como formato de destino, por si solos, no autorizan subir ni publicar.

## Comprobar la conexion real

Descubrir primero conectores/herramientas ya disponibles en el cliente. Preferir
una integracion oficial configurada; si no existe y hay navegador controlable,
usar la interfaz normal de subida con la sesion del usuario. El usuario inicia
sesion y resuelve MFA; no pedir contrasenas, cookies o tokens en el chat. Confirmar
identidad y permisos del destino antes de enviar. La API key de Gemini no autoriza
publicar en YouTube ni en otras redes: requieren sus propias sesiones/OAuth.

Estas son comprobaciones, no promesas de acceso universal. Verificar documentacion
actual al conectar. Referencias consultadas el 14-09-2026:

- **TikTok:** Direct Post requiere acceso autorizado a Content Posting API. Consultar
  la informacion actual del creador para formatos, duracion y opciones de privacidad.
  Un cliente sin auditar tiene restricciones de publicacion privada; no prometer
  un post publico ni confundir Upload/inbox con una publicacion terminada.
  [Guia oficial](https://developers.tiktok.com/doc/content-sharing-guidelines),
  [informacion del creador](https://developers.tiktok.com/doc/content-posting-api-reference-query-creator-info).
- **YouTube:** verificar canal y OAuth con permiso de subida. Proyectos API no
  verificados pueden quedar restringidos a privado; comparar el estado real con
  la visibilidad elegida. Resolver los campos exigidos por el destino con el usuario.
  [Subida oficial](https://developers.google.com/youtube/v3/docs/videos/insert).
- **Instagram:** comprobar cuenta profesional y requisitos de la ruta elegida
  (Instagram Login o Facebook Login). Usar permisos de publicacion vigentes y
  comprobar procesamiento/publicacion del contenedor; crearlo no publica el Reel.
  [Contenido y publicacion](https://developers.facebook.com/documentation/instagram-platform/content-publishing.md).
- **Facebook:** identificar la pagina o destino exacto y comprobar que la integracion
  elegida puede publicar alli; no confundir una pagina con un perfil personal.
  Verificar el permiso de la cuenta y la ruta de video/Reels soportada por ese host.
  Usar la documentacion oficial que corresponda a la integracion disponible.

Si no hay una conexion util, completar los exports aprobados y entregar archivos,
textos y pasos concretos para la subida manual. Registrar publicacion pendiente
y que acceso o accion falta. No marcarla publicada, no simular un conector ni
cambiar de cuenta, visibilidad o contratar un servicio para sortear el bloqueo.
La descarga y configuracion de otra integracion se acuerdan por separado.

## Publicar y verificar sin duplicados

Comprobar que el MP4 coincide con la revision validada y que cumple los requisitos
actuales de la red. Si requiere otro recorte o cambio material, mostrar esa variante
para validarla. Conservar el export local aunque se pida publicar directamente.
No agregar musica de catalogo por una API que no lo soporte. Si el usuario eligio
terminar ese paso en la app, dejar la publicacion pendiente de esa accion.

Registrar intento y destino antes de enviar; guardar el identificador remoto tan
pronto aparezca. Al retomar consultar PUBLICACION.md y el estado remoto. Si hubo
timeout o respuesta incierta, consultar la subida/post existente antes de reintentar:
no crear una publicacion duplicada para comprobar si funciono. Respetar controles
de la plataforma y detener reintentos repetidos sin evidencia nueva.

Distinguir pendiente, subiendo, procesando, borrador, programado, publicado,
fallido e incierto. Un HTTP exitoso o barra de subida completa no prueba publicacion.
Verificar cuenta, texto, revision y visibilidad final mediante la respuesta/estado
remoto o interfaz. Entregar enlace real o id y el estado por CADA destino. Un fallo
en una red no debe volver a subir los videos que ya se publicaron en otras.
