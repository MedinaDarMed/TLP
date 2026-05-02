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
