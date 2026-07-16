================================================================================
                         MANUAL DE USUARIO FINAL
              COMO JUGAR CADA JUEGO DEL ECOSISTEMA BRICKSCRIPT
================================================================================

#Video integración: https://drive.google.com/file/d/1toWM8IZSF-QBTiRPtZm7YQ0mCI4mFzAh/view?usp=sharing

Este documento explica COMO JUGAR cada uno de los 5 juegos incluidos en el
proyecto: los originales, sus versiones remake, y el juego nuevo de tanques.

--------------------------------------------------------------------------------
INDICE
--------------------------------------------------------------------------------
0. Como abrir un juego
1. Tabla rapida de controles
2. TETRIS (original)
3. TETRIS REMAKE
4. SNAKE (original)
5. SNAKE EVOLVED (remake)
6. BRICK TANKS (juego nuevo)
7. Consejos y problemas comunes


================================================================================
0. COMO ABRIR UN JUEGO
================================================================================

Requisitos: Windows + Python 2.7 (ver INSTALL.txt si necesitas instalarlo).

1. Abre una consola (cmd.exe) dentro de la ca rpeta del proyecto.
2. Escribe "jugar" seguido del nombre del juego que quieras probar:

       jugar tetris             -> Tetris original
       jugar tetris_remake      -> Tetris Remake (con power-ups)
       jugar snake              -> Snake original
       jugar snake_evolved      -> Snake Evolved (con niveles)
       jugar brick_tanks        -> Brick Tanks (juego nuevo)

3. Se abrira una ventana con el juego. Para salir, cierra la ventana, o
   presiona el boton "SALIR" que aparece en la pantalla de Game Over.

No existe pausa ni tecla de menu: cada partida se juega de principio a fin
en una sola ventana.


================================================================================
1. TABLA RAPIDA DE CONTROLES
================================================================================

  JUEGO                    MOVIMIENTO              ACCION ESPECIAL
  ------------------------ ----------------------- -----------------------
  Tetris / Tetris Remake   Flecha IZQ/DER: mueve    Flecha ARRIBA: rota
                           la pieza a los lados     la pieza
                           Flecha ABAJO: acelera
                           la caida

  Snake / Snake Evolved    Flechas ARRIBA/ABAJO/    (ninguna: la serpiente
                           IZQ/DER: cambian la      avanza sola en la
                           direccion                direccion elegida)

  Brick Tanks              Flechas o W A S D:       BARRA ESPACIADORA:
                           mueven el tanque una     dispara en la
                           casilla y fijan hacia    direccion en la que
                           donde apunta              mira el tanque

En todos los casos los controles se manejan con el teclado; no se necesita
mouse durante la partida.


================================================================================
2. TETRIS (ORIGINAL)                                       jugar tetris
================================================================================

Version clasica del Tetris, estilo "brick game" de LCD.

OBJETIVO
  Acomodar las piezas que caen para completar filas horizontales completas
  en un tablero de 10 columnas x 20 filas. Cada fila completa desaparece y
  suma puntos.

PIEZAS
  Solo hay 3 piezas posibles: I, L y T. Las tres caen con la misma
  probabilidad y se dibujan siempre del mismo color cian clasico.

CONTROLES
  Flecha IZQUIERDA / DERECHA : mover la pieza a los lados
  Flecha ABAJO               : bajar la pieza mas rapido
  Flecha ARRIBA              : rotar la pieza

REGLAS
  - La pieza cae 1 casilla automaticamente en cada turno de juego (gravedad
    constante, no aumenta de velocidad).
  - Al completar una fila: +100 puntos y la fila se elimina.
  - El juego termina cuando una pieza nueva ya no cabe en la parte de
    arriba del tablero.

INTERFAZ
  Panel simple: tablero y puntuacion. Sin vista previa de la siguiente
  pieza, sin colores por pieza, sin power-ups. Es la version "pura".


================================================================================
3. TETRIS REMAKE                                    jugar tetris_remake
================================================================================

Mismo objetivo y mismos controles que el Tetris original (IZQ/DER mueve,
ABAJO acelera, ARRIBA rota). Si ya sabes jugar el original, ya sabes jugar
el remake: lo que cambia es todo lo que rodea a esa base.

QUE CAMBIA RESPECTO AL ORIGINAL

  a) Mas piezas: ademas de I, L y T se agregan O (cuadrado), S y Z. En
     total son 6 figuras distintas, cada una con su propio color, y no
     todas caen con la misma frecuencia (el cuadrado O es, por ejemplo,
     algo mas frecuente que el resto).

  b) Panel mejorado: ademas de la puntuacion, se muestra la cantidad de
     lineas eliminadas y una VISTA PREVIA de la proxima pieza que va a
     caer, para que puedas planear mejor tu jugada.

  c) Power-ups (piezas especiales): en vez de una pieza normal, a veces
     aparece una pieza especial como recompensa por como limpiaste
     lineas. Estas son las tres que existen:

     * DOBLE LIMPIEZA (bloque magenta, 3x2)
       Aparece si eliminas EXACTAMENTE 2 lineas de una sola jugada.

     * TRIPLE / MODO BOMBA (bloque blanco, 1x2)
       Aparece si eliminas 3 lineas o mas de una sola jugada.
       Truco: si la GIRAS 10 veces o mas mientras cae (presiona ARRIBA
       repetidamente antes de que aterrice), la pieza entra en "modo
       bomba": se pinta con colores arcoiris animados y, al fijarse en
       el tablero, ELIMINA TODAS las filas donde quedo alguna de sus
       celdas, sumando 500 puntos extra por cada fila borrada de esa
       forma. Es la manera mas rentable de sumar puntos rapido.

     * PURGA DE LINEAS (bloque gris)
       Aparece automaticamente cada vez que acumulas 8 lineas eliminadas
       en total durante la partida (sin importar de a cuantas las hayas
       ido limpiando). No es una pieza que controles: en cuanto aparece,
       borra en silencio las dos filas mas altas que tengan contenido,
       sin sumar puntos. Sirve como un "respiro" que suaviza el tablero
       cuando se te esta llenando.

  d) Estetica: fondo oscuro, borde con efecto arcoiris y una cuadricula
     con textura sutil, en vez del tablero gris plano del original.

  En resumen: juega igual que el Tetris clasico, pero presta atencion a
  como limpias tus lineas (de a 1, de a 2, de a 3+) porque de eso depende
  que power-up te toca.


================================================================================
4. SNAKE (ORIGINAL)                                        jugar snake
================================================================================

Version clasica de la vibora que crece al comer.

OBJETIVO
  Guiar a la serpiente para que coma la comida (un cuadro) y crezca, sin
  chocar contra las paredes ni contra su propio cuerpo. Tablero de 18x18.

CONTROLES
  Flecha ARRIBA / ABAJO / IZQUIERDA / DERECHA : cambia la direccion en la
  que avanza la serpiente. (No puedes girar 180 grados de golpe sobre tu
  propia cola, por ejemplo si vas hacia la derecha no puedes apretar
  izquierda directamente).

REGLAS
  - La serpiente avanza sola, un paso por turno, en la ultima direccion
    que hayas indicado.
  - Comer la comida: +10 puntos, la serpiente crece 1 segmento, y aparece
    comida nueva en otro lugar del tablero.
  - Chocar contra una pared, o contra tu propio cuerpo: GAME OVER
    inmediato.
  - La velocidad es fija durante toda la partida; no hay niveles ni
    power-ups.


================================================================================
5. SNAKE EVOLVED (REMAKE)                          jugar snake_evolved
================================================================================

Mismos controles que el Snake original (las 4 flechas cambian la
direccion). Lo que cambia es que ahora la partida evoluciona con vos a
medida que sumas puntos: mas velocidad, mas peligros, y una recompensa
para sobrevivir a todo eso.

SISTEMA DE NIVELES (progresion automatica por puntaje)
  El juego siempre EMPIEZA en el nivel mas facil y va subiendo de nivel
  solo, sin que tengas que hacer nada especial, en cuanto tu puntaje llega
  al umbral necesario. El titulo de la ventana siempre te dice en que
  nivel estas parado:

    BABY       (nivel inicial)  - lento, sin veneno, sin obstaculos,
                                  sin power-up.
    ENTUSIASTA (desde 30 pts)   - mas rapido, aparece veneno (resta
                                  puntos pero no mata) y aparece el
                                  escudo.
    NYAN_CAT   (desde 80 pts)   - el nivel maximo: muy rapido, aparecen
                                  4 nubes-obstaculo fijas y el veneno
                                  pasa a ser MORTAL (ver abajo).

  En NYAN_CAT ademas la serpiente cambia de forma (los segmentos se
  vuelven triangulares en vez de redondos) y la cabeza dibuja una carita
  de gato, como referencia al meme "Nyan Cat".

PELIGROS NUEVOS
  * Comida venenosa (cuadro magenta con una X): aparece despues de comer
    comida normal.
      - En ENTUSIASTA solo te resta 5 puntos.
      - En NYAN_CAT es LETAL: comerla es Game Over inmediato (salvo que
        tengas el escudo activo). Ten cuidado al llegar a este nivel.

  * Nubes obstaculo (ovalos grises): solo aparecen en NYAN_CAT, en 4
    posiciones fijas del tablero. Si chocas contra una, pierdes TODOS tus
    puntos (o mueres si ya tenias 0 puntos), salvo que tengas el escudo
    activo.

  * Choque contra pared o contra tu propio cuerpo en NYAN_CAT: a
    diferencia del original, en este nivel maximo un choque no te mata de
    inmediato la primera vez; pierdes todo tu puntaje y la serpiente
    "atraviesa" hacia el lado opuesto del tablero para seguir jugando. Si
    vuelves a chocar estando ya en 0 puntos, ahi si es Game Over
    definitivo. Es una segunda oportunidad, no una inmunidad permanente.

ESCUDO (power-up, diamante cian/verde)
  Aparece en el tablero desde el nivel ENTUSIASTA en adelante. Al
  comerlo, quedas invulnerable durante unos segundos: mientras dura,
  cualquier choque (pared, tu propio cuerpo, veneno o nubes) no te
  hace dano, y en vez de morir contra un borde, la serpiente aparece por
  el lado opuesto del tablero.

RESUMEN
  Juega igual que el Snake clasico. La diferencia es que mientras mas
  puntos acumules, mas dificil (y mas vistoso) se pone el juego, y
  conviene recoger el escudo apenas lo veas para sobrevivir los tramos
  mas peligrosos.


================================================================================
6. BRICK TANKS (JUEGO NUEVO)                        jugar brick_tanks
================================================================================

El unico juego de tanques del proyecto. A diferencia de Tetris y Snake,
aqui controlas un tanque que se mueve casilla por casilla y dispara,
enfrentando oleadas de tanques enemigos y, al final, a un jefe.

OBJETIVO
  Sobrevivir a las oleadas de tanques enemigos, acumular puntos, y
  derrotar al jefe final (Boss) cuando aparezca para ganar la partida.

CONTROLES
  Flechas o W A S D  : mueven tu tanque UNA casilla en esa direccion y
                        hacen que tu tanque quede "mirando" hacia ese
                        mismo lado (no avanza solo; cada movimiento es
                        una pulsacion de tecla).
  BARRA ESPACIADORA  : dispara un proyectil en la direccion hacia la que
                        esta mirando tu tanque en ese momento.

  Tip: para disparar hacia otro lado, primero muevete un paso en esa
  direccion (aunque sea contra una pared, para solo girar) y luego
  dispara.

TU TANQUE (cian)
  - Empieza con 100 puntos de vida (resistencia).
  - Cada impacto de un enemigo te quita 10 de vida.
  - Si tu vida llega a 0: GAME OVER.

ENEMIGOS
  - Tanque GRUNT (rojo): rapido, poca resistencia (30 HP). Cambia de
    color a medida que pierde vida (rojo -> naranja -> amarillo), asi
    puedes ver a simple vista que tan danado esta.
  - Tanque HEAVY (rojo oscuro): mas lento pero mas resistente (60 HP),
    tambien cambia de color con el dano.
  - Ambos se acercan poco a poco hacia tu posicion y disparan
    periodicamente en tu direccion.

MUROS DESTRUCTIBLES (bloques color caqui)
  Bloquean el paso de tanques y de proyectiles. Aguantan 2 impactos antes
  de destruirse. Puedes usarlos como cobertura, o destruirlos disparando
  para abrirte paso.

MARTILLO (power-up dorado, aparece al azar)
  Si lo recoges, recuperas 25 puntos de vida (sin superar tu maximo).
  Aparece de vez en cuando en una posicion aleatoria del mapa mientras no
  haya ya uno activo; conviene ir a buscarlo si tu vida esta baja.

OLEADAS Y PROGRESION
  - Al eliminar a todos los enemigos de una oleada, aparece una nueva
    oleada un poco mas rapida y con disparos mas frecuentes que la
    anterior, los muros se reparan por completo, y tu tanque recupera 25
    puntos de vida como recompensa.
  - Al llegar a 500 puntos, las oleadas normales terminan: los enemigos
    restantes desaparecen y aparece el JEFE FINAL (tanque grande color
    magenta, 200 de vida), que tambien cambia de color segun cuanta vida
    le queda.
  - Derrotar al jefe final = VICTORIA. Se muestra una pantalla especial
    indicando tu puntuacion final y la oleada alcanzada.


================================================================================
7. CONSEJOS Y PROBLEMAS COMUNES
================================================================================

* El juego no abre / dice error de Python:
    Revisa INSTALL.txt; necesitas Python 2.7 instalado (no sirve Python 3).

* No se que tecla usar:
    Revisa la seccion 1 (tabla rapida de controles) de este documento;
    todos los juegos se manejan solo con el teclado.

* En Tetris Remake no me sale ningun power-up:
    Los power-ups dependen de COMO limpias las lineas: exactamente 2 de
    una vez, 3 o mas de una vez, o acumular 8 en total. Prueba a limpiar
    varias lineas de una sola jugada en vez de una por una.

* En Snake Evolved el veneno me mato de repente:
    Es normal a partir del nivel NYAN_CAT (80+ puntos): ahi el veneno deja
    de solo restar puntos y pasa a ser mortal. Ve por el escudo si vas a
    seguir jugando en ese nivel.

* En Brick Tanks disparo hacia el lado equivocado:
    Tu tanque dispara hacia el ultimo lado en el que se movio. Da un paso
    (o intenta moverte contra una pared para solo girar) en la direccion
    que quieres antes de presionar espacio.

================================================================================
                              FIN DEL MANUAL
================================================================================
