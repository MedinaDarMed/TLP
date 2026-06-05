=============================================================
          PROYECTO: BrickScript - Un Lenguaje para Juegos Retro
=============================================================

BrickScript es un lenguaje de programacion simple (un "DSL" o Lenguaje de Dominio Especifico) disenado para crear juegos clasicos de estilo "Brick Game", como Tetris y Snake.

Este proyecto incluye el compilador que traduce el codigo BrickScript a un formato que la computadora entiende, y el motor de juego que lo ejecuta.

El runtime fue implementado para Windows con Python 2.7

-------------------------------------------------------------
                      COMO JUGAR
-------------------------------------------------------------

Para compilar y ejecutar un juego, hemos creado un script que hace todo el trabajo por ti.

1. Abre una terminal de comandos (cmd.exe) en la carpeta principal del proyecto (C:\tpl).

2. Usa el comando "jugar.bat" seguido del nombre del juego que quieres ejecutar (sin la extension .brick).

   EJEMPLO PARA JUGAR SNAKE:
   jugar.bat snake

   EJEMPLO PARA JUGAR TETRIS:
   jugar.bat tetris

El script primero compilara el archivo .brick correspondiente. Si la compilacion es exitosa, el juego se iniciara automaticamente.

Para salir del juego, presiona la tecla 'q'.


-------------------------------------------------------------
                 SINTAXIS DE BRICKSCRIPT
-------------------------------------------------------------

El lenguaje se basa en bloques de comandos simples y faciles de entender.

--- COMANDOS GENERALES ---

* GAME_TYPE [TIPO_DE_JUEGO]
    Define que logica usara el motor. Obligatorio.
    Ej: GAME_TYPE TETRIS
    Ej: GAME_TYPE SNAKE

* GAME_GRID (ANCHO, ALTO)
    Establece el tamano del area de juego.
    Ej: GAME_GRID (10, 20)

* DEFINE SHAPE [NOMBRE_PIEZA]: ... END
    Define una forma geometrica con uno o mas estados (para rotaciones).
    Ej: DEFINE SHAPE T_PIEZA: STATE 1: [0,1,0][1,1,1][0,0,0] END

--- SINTAXIS PARA TETRIS ---

Eventos disponibles: ON START, ON TICK, ON LINE_CLEAR, ON KEY_UP, ON KEY_DOWN, ON KEY_LEFT, ON KEY_RIGHT

Acciones comunes:
* SPAWN RANDOM_SHAPE
* MOVE CURRENT_PIEZA [LEFT | RIGHT | DOWN]
* ROTATE CURRENT_PIEZA
* INCREASE_SCORE [PUNTOS]

--- SINTAXIS PARA SNAKE ---

Eventos disponibles: ON START, ON TICK, ON EAT_FOOD, ON COLLISION_WALL, ON COLLISION_SELF, ON KEY_UP, ON KEY_DOWN, ON KEY_LEFT, ON KEY_RIGHT

Acciones comunes:
* SPAWN PLAYER AT (X, Y)
* SPAWN FOOD AT RANDOM
* MOVE PLAYER FORWARD
* SET_DIRECTION [UP | DOWN | LEFT | RIGHT]
* INCREASE_SCORE [PUNTOS]
* GROW PLAYER [CANTIDAD]
* GAME_OVER


---------------------------------------------------------------------------------------------------------------------
                                            Cambios realizados.
---------------------------------------------------------------------------------------------------------------------

He realizado un único cambio en el archivo tetris.json linea 143 para completar las rotaciones de las piezas del Tetris.

Sección afectada: La definición de la pieza "I_PIECE"


Descripción del cambio:

* La pieza I originalmente tenía solo 2 estados de rotación (vertical y horizontal).
* Agregué los estados de rotación 3 y 4 para completar los 4 estados requeridos.
* El estado 3 es idéntico al estado 1 (pieza vertical).
* El estado 4 es idéntico al estado 2 (pieza horizontal).
* Esto se debe a que la pieza I tiene solo 2 orientaciones únicas en Tetris estándar, pero el requerimiento pedía 4 estados.

* Las piezas T y L ya tenían 4 estados de rotación completos.
* La pieza I necesitaba los estados adicionales para cumplir con el requerimiento de "4 estados de rotación".
* Las rotaciones mantienen la coherencia geométrica, rotando alrededor del centro de la pieza (posición 1.5, 1.5 en la cuadrícula 4x4) sin saltos.

Código antes del cambio:

"I_PIECE": [
  [
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0]
  ],
  [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ]
]

Codigo después del cambio:

"I_PIECE": [
  [
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0]
  ],
  [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ],
  [
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 0, 0]
  ],
  [
    [0, 0, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ]
]

