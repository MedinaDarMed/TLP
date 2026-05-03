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

| "I_PIECE": [
|  [
|    [0, 1, 0, 0],
|    [0, 1, 0, 0],
|    [0, 1, 0, 0],
|    [0, 1, 0, 0]
|  ],
|  [
|    [0, 0, 0, 0],
|    [1, 1, 1, 1],
|    [0, 0, 0, 0],
|    [0, 0, 0, 0]
|  ]
| ]

Codigo después del cambio:

| "I_PIECE": [
|  [
|    [0, 1, 0, 0],
|    [0, 1, 0, 0],
|    [0, 1, 0, 0],
|    [0, 1, 0, 0]
|  ],
|  [
|    [0, 0, 0, 0],
|    [1, 1, 1, 1],
|    [0, 0, 0, 0],
|    [0, 0, 0, 0]
|  ],
|  [
|    [0, 1, 0, 0],
|    [0, 1, 0, 0],
|    [0, 1, 0, 0],
|    [0, 1, 0, 0]
|  ],
|  [
|    [0, 0, 0, 0],
|    [1, 1, 1, 1],
|    [0, 0, 0, 0],
|    [0, 0, 0, 0]
|  ]
| ]

---------------------------------------------------------------------------------------------------------------------
                                            Cambios realizados (Sara y Anderson).
---------------------------------------------------------------------------------------------------------------------

Hemos modificado cuatro archivos, únicamente vamos a mencionar los cambios de lógica (no se mencionan las líneas que solo cambiaron espaciado o comentarios):

# tetris.brick

* Cambio 1 — I_PIECE: se agrega COLOR y CHANCE, y se corrige el END (estaba como END con sangría, ahora va al nivel raíz).

- ANTES (al final del bloque I_PIECE)
    [0, 0, 0, 0]
    [1, 1, 1, 1]
    [0, 0, 0, 0]
    [0, 0, 0, 0]
  END

- DESPUÉS
    [0, 0, 0, 0]
    [1, 1, 1, 1]
    [0, 0, 0, 0]
    [0, 0, 0, 0]
  COLOR: #00FFFF
  CHANCE: 15
END

* Cambio 2 — L_PIECE: los estados 2, 3 y 4 estaban en el orden incorrecto. Se reordenan, y se agregan COLOR y CHANCE.

- ANTES
  STATE 2:
    [0, 1, 0]
    [0, 1, 0]
    [1, 1, 0]
  STATE 3:
    [0, 0, 1]
    [1, 1, 1]
    [0, 0, 0]
  STATE 4:
    [0, 0, 0]
    [1, 1, 1]
    [1, 0, 0]
END

- DESPUÉS
  STATE 2:
    [0, 0, 0]
    [1, 1, 1]
    [1, 0, 0]
  STATE 3:
    [1, 1, 0]
    [0, 1, 0]
    [0, 1, 0]
  STATE 4:
    [0, 0, 1]
    [1, 1, 1]
    [0, 0, 0]
  COLOR: #FF8800
  CHANCE: 15
END

* Cambio 3 — T_PIECE: se agrega COLOR y CHANCE

- ANTES (al final del bloque T_PIECE)
    [0, 1, 0]
    [1, 1, 0]
    [0, 1, 0]
END

- DESPUÉS
    [0, 1, 0]
    [1, 1, 0]
    [0, 1, 0]
  COLOR: #AA00FF
  CHANCE: 15
END

* Cambio 4 — Se agregan las tres piezas nuevas completas (después de T_PIECE y antes de ON START)

- ANTES
(no existía nada aquí)

- DESPUÉS
DEFINE SHAPE O_PIECE:
  STATE 1:
    [1, 1]
    [1, 1]
  STATE 2:
    [1, 1]
    [1, 1]
  STATE 3:
    [1, 1]
    [1, 1]
  STATE 4:
    [1, 1]
    [1, 1]
  COLOR: #FFFF00
  CHANCE: 20
END

DEFINE SHAPE S_PIECE:
  STATE 1:
    [0, 1, 1]
    [1, 1, 0]
    [0, 0, 0]
  STATE 2:
    [1, 0, 0]
    [1, 1, 0]
    [0, 1, 0]
  STATE 3:
    [0, 0, 0]
    [0, 1, 1]
    [1, 1, 0]
  STATE 4:
    [0, 1, 0]
    [0, 1, 1]
    [0, 0, 1]
  COLOR: #00FF44
  CHANCE: 17
END

DEFINE SHAPE Z_PIECE:
  STATE 1:
    [1, 1, 0]
    [0, 1, 1]
    [0, 0, 0]
  STATE 2:
    [0, 0, 1]
    [0, 1, 1]
    [0, 1, 0]
  STATE 3:
    [0, 0, 0]
    [1, 1, 0]
    [0, 1, 1]
  STATE 4:
    [0, 1, 0]
    [1, 1, 0]
    [1, 0, 0]
  COLOR: #FF2244
  CHANCE: 18
END

# tetris.bnf

* Cambio 1 — <definicion_shape>: se agrega <atributos_opcionales> antes del "END"

- ANTES
<definicion_shape> ::= "DEFINE" "SHAPE" <identificador> ":" <estados> "END"

- DESPUÉS
<definicion_shape> ::= "DEFINE" "SHAPE" <identificador> ":" <estados> <atributos_opcionales> "END"

* Cambio 2 — Se agregan las reglas de <atributos_opcionales>, <atributo_color>, <atributo_chance>, <color_hex> y <hex_digito> (no existían)

- ANTES
(no existían estas reglas)

- DESPUÉS
<atributos_opcionales> ::= <atributo_color> <atributo_chance>
                         | <atributo_color>
                         | <atributo_chance>
                         | ε

<atributo_color>  ::= "COLOR" ":" <color_hex>
<atributo_chance> ::= "CHANCE" ":" <numero>

<color_hex> ::= "#" <hex_valor>
<hex_valor> ::= <hex_digito> <hex_digito> <hex_digito> <hex_digito> <hex_digito> <hex_digito>
<hex_digito> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
               | "A" | "B" | "C" | "D" | "E" | "F"

# compiler.py -

* Cambio 1 — Regex para eliminar comentarios (línea ~19)

- ANTES
codigo_fuente = re.sub(r'#.*', '', codigo_fuente)

- DESPUÉS
codigo_fuente = re.sub(r'#(?![0-9A-Fa-f]{6}).*', '', codigo_fuente)

* Cambio 2 — Regex del lexer para capturar colores hex (línea ~20)

- ANTES
token_regex = r'\b[A-Z_]+\b|\d+|[\[\](),:]'

- DESPUÉS
token_regex = r'#[0-9A-Fa-f]{6}|\b[A-Z_]+\b|\d+|[\[\](),:]'

* Cambio 3 — Inicialización del AST (línea ~60)

- ANTES
self.ast = {"tipo_juego": None, "config": {}, "shapes": {}, "events": {}}

- DESPUÉS
self.ast = {
    "tipo_juego":    None,
    "config":        {},
    "shapes":        {},
    "shape_colors":  {},   # NUEVO
    "shape_chances": {},   # NUEVO
    "events":        {}
}

* Cambio 4 — Final de parsear_shape(), antes del consumir('END') (línea ~147)

- ANTES
        self.consumir('END')
        self.ast['shapes'][nombre_shape] = estados

- DESPUÉS
        color  = '#00FFFF'
        chance = 1

        while (self.posicion < len(self.tokens) and
               self.tokens[self.posicion] in ('COLOR', 'CHANCE')):
            atributo = self.consumir()
            self.consumir(':')
            if atributo == 'COLOR':
                color = self.consumir()
            elif atributo == 'CHANCE':
                chance = int(self.consumir())

        self.consumir('END')
        self.ast['shapes'][nombre_shape] = estados
        self.ast['shape_colors'][nombre_shape]  = color   # NUEVO
        self.ast['shape_chances'][nombre_shape] = chance  # NUEVO

# runtime.py

* Cambio 1 — __init__(), bloque TETRIS (línea ~85)

- ANTES
        if self.tipo_juego == 'TETRIS':
            self.pieza_actual = None
            self.pieza_x, self.pieza_y, self.pieza_rotacion = 0, 0, 0
            self.velocidad_gravedad = 0.4

- DESPUÉS
        if self.tipo_juego == 'TETRIS':
            self.pieza_actual   = None
            self.pieza_x        = 0
            self.pieza_y        = 0
            self.pieza_rotacion = 0
            self.velocidad_gravedad = 0.4
            self.pieza_color = '#00FFFF'   # NUEVO

* Cambio 2 — dibujar(), bloque TETRIS (línea ~160)

- ANTES
        COLOR_PIEZA = '#00FFFF'
        ...
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            matriz_pieza = self.pieza_actual[self.pieza_rotacion]

- DESPUÉS
        # COLOR_PIEZA ya no se define aquí (se eliminó la línea hardcoded)
        ...
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            COLOR_PIEZA = self.pieza_color   # NUEVO: dinámico en vez de fijo
            matriz_pieza = self.pieza_actual[self.pieza_rotacion]

* Cambio 3 — tetris_spawn_pieza() completo (línea ~230)

- ANTES
    def tetris_spawn_pieza(self):
        nombre_pieza = random.choice(self.datos_juego['shapes'].keys())
        self.pieza_actual = self.datos_juego['shapes'][nombre_pieza]
        self.pieza_x, self.pieza_y, self.pieza_rotacion = self.ancho / 2 - 2, 0, 0
        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True

- DESPUÉS
    def tetris_spawn_pieza(self):
        nombres = list(self.datos_juego['shapes'].keys())
        chances = self.datos_juego.get('shape_chances', {})

        pesos = [chances.get(n, 1) for n in nombres]
        total = sum(pesos)
        r = random.random() * total

        acumulado    = 0
        nombre_pieza = nombres[-1]
        for nombre, peso in zip(nombres, pesos):
            acumulado += peso
            if r < acumulado:
                nombre_pieza = nombre
                break

        self.pieza_actual = self.datos_juego['shapes'][nombre_pieza]

        colores = self.datos_juego.get('shape_colors', {})        # NUEVO
        self.pieza_color = colores.get(nombre_pieza, '#00FFFF')   # NUEVO

        self.pieza_x        = self.ancho / 2 - 2
        self.pieza_y        = 0
        self.pieza_rotacion = 0
        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True

