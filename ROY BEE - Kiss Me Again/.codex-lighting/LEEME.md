# Kiss Me Again — muros y luces

Normal / Standard contiene la nueva decoración. Easy / Standard, etiquetado
«BACKUP - Original sin cambios», es una copia exacta del antiguo Normal: no es
una adaptación fácil y tiene las mismas notas y velocidad que antes.

La copia completa original está en `../backups/before-lighting-20261011-170244.zip`.
Incluye audio, portada, mapas, metadatos, autosaves, bookmarks y el ZIP que ya
existía. Se verificó su integridad y los hashes SHA-256 de los archivos.

## Cambios

- 292 muros vanilla v3: pilares abiertos, abanicos hacia fuera, ondas de alturas,
  respuestas alternadas y marcos laterales. Los motivos dejan espacios de descanso.
- 2.046 eventos: pulso grave en luces traseras, respuesta de notas en laterales,
  acentos centrales y cambios de color/intensidad en las secciones existentes.
- Se sustituyen los nueve muros originales, incluido el del beat 372,5 que
  ocupaba el carril 0. Todos los nuevos quedan fuera de los carriles de juego,
  con un carril adicional de separación a cada lado; no hay techos centrales.
- Las luces están en `NormalStandard.dat` (v3.3.0). Su `Lightshow.dat` externo
  no se utiliza para este mapa v3, por lo que se ha conservado intacto.
- No se añaden requisitos de Chroma, Noodle Extensions o Mapping Extensions.
- Se conservan notas, bombas, BPM, velocidades, bookmarks, entorno y Lawless.

## Análisis y límites

El audio dura 139,2556 segundos. La autocorrelación estima unos 166,67 BPM con
resolución temporal de 10 ms; el ajuste fino de la rejilla entre 164 y 169 BPM
encuentra 166,48 BPM, coincidente con el mapa. No se ha cambiado el tempo.
La distancia mediana entre tiempos únicos de notas y ataques detectados es
16,7 ms, y el 90 % cae a menos de 60 ms. Es una medida orientativa: no demuestra
que cada nota represente una voz o instrumento concreto.

El análisis utiliza flujo espectral de graves, medios y agudos; no separa stems
ni reconoce cada sílaba o altura vocal. Las notas y los diez marcadores originales
guían las frases. La energía medida del audio modula los acentos.

Comprobaciones ejecutadas con `verify.py`: copia Easy idéntica byte a byte;
notas, bombas y resto de campos conservados; referencias JSON válidas;
eventos ordenados sin duplicados por grupo/tiempo; cero muros en carriles de
juego y cero solapamientos volumétricos de muros; apagado final explícito.
Máximo de seis muros simultáneos en el plano del jugador. No se ha validado
visualmente en Beat Saber/ChroMapper ni se ha realizado playtest en VR.

## Revisar y restaurar

Recarga la carpeta en ChroMapper o Beat Saber para ver los cambios. Selecciona
Normal para probar la decoración y Easy para comparar con el original.
Easy no implica dificultad reducida. Si el editor estaba abierto, evita guardar
su versión antigua en memoria antes de recargar.

Para deshacer todo, cierra el mapa en el editor y restaura `Info.dat` y
`NormalStandard.dat` del ZIP. La antigua información ya no referencia Easy;
el archivo Easy puede conservarse como otra copia. Los demás archivos
originales no fueron modificados.

## Fuentes consultadas

Se aplican técnicas documentadas por BSMG, no una clasificación demostrada
de las tendencias más populares de 2026:

- https://bsmg.wiki/mapping/intermediate-lighting.html — contraste entre secciones,
  respuesta de laterales y movimiento moderado de anillos.
- https://bsmg.wiki/mapping/intermediate-mapping.html — uso musical de muros
  cosméticos vanilla v3.
- https://bsmg.wiki/mapping/basic-lighting.html — grupos de DefaultEnvironment.
- https://bsmg.wiki/mapping/map-format/lightshow.html — valores de eventos.
- https://bsmg.wiki/mapping/map-format/info.html — luces integradas en mapas v3.

`analysis.json` contiene las medidas; `result.json`, los motivos por sección.
`analyze.py` y `build.py` documentan el proceso. No son herramientas de ejecución
repetida: build se niega a sobrescribir un Easy existente o una fuente modificada.
