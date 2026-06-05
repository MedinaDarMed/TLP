---------------------------------------------------------------------------------------------------------------------
                                            Cambios realizados (Darwin).
---------------------------------------------------------------------------------------------------------------------

He realizado un único cambio en el archivo tetris.json linea 143 para completar las rotaciones de las piezas del Tetris.

Sección afectada: La definición de la pieza "I_PIECE"

# tetris.json

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

---------------------------------------------------------------------------------------------------------------------
                                            Cambios realizados (Santiago).
---------------------------------------------------------------------------------------------------------------------

He modificado tres archivos para implementar los Power-Ups (Actividad 3 - Punto C) y algunas mejoras visuales.

==============================================
BLOQUE 1 — Power-Ups (Punto C)
==============================================

# tetris.brick

* Cambio 1 — Se agregan tres bloques DEFINE POWERUP al final del archivo, antes de ON START.

- ANTES
(no existían bloques DEFINE POWERUP)

- DESPUÉS
DEFINE POWERUP DOUBLE_CLEAR_PU:
  TRIGGER: LINE_CLEAR_EXACT 2
  STATE 1:
    [1, 1, 1]
    [1, 1, 1]
  COLOR: #FF00FF
  CHANCE: 100
END

DEFINE POWERUP TRIPLE_CLEAR_PU:
  TRIGGER: LINE_CLEAR_MIN 3
  STATE 1:
    [1, 0]
    [1, 0]
  STATE 2:
    [1, 1]
    [0, 0]
  COLOR: #FFFFFF
  CHANCE: 100
END

DEFINE POWERUP LINE_PURGE_PU:
  TRIGGER: LINE_CUMULATIVE 8
  STATE 1:
    [0]
  COLOR: #888888
  CHANCE: 100
END

# tetris.bnf

* Cambio 1 — <programa>: se agrega <definiciones_powerup> como elemento opcional del programa
- ANTES
<programa> ::= <tipo_juego> <configuracion> <definiciones_shape> <eventos>
- DESPUÉS
<programa> ::= <tipo_juego> <configuracion> <definiciones_shape> <definiciones_powerup> <eventos>

* Cambio 2 — Se agregan las reglas de powerup (no existían)
- ANTES
(no existían estas reglas)
- DESPUÉS
<definiciones_powerup> ::= <definicion_powerup> <definiciones_powerup> | ε
<definicion_powerup>   ::= "DEFINE" "POWERUP" <identificador> ":" <trigger> <estados> <atributos_opcionales> "END"
<trigger>              ::= "TRIGGER" ":" <tipo_trigger> <numero>
<tipo_trigger>         ::= "LINE_CLEAR_EXACT" | "LINE_CLEAR_MIN" | "LINE_CUMULATIVE"

# compiler.py

* Cambio 1 — Inicialización del AST en Parser.__init__() — se agrega la clave "powerups"

- ANTES
self.ast = {
    "tipo_juego":    None,
    "config":        {},
    "shapes":        {},
    "shape_colors":  {},
    "shape_chances": {},
    "events":        {}
}

- DESPUÉS
self.ast = {
    "tipo_juego":    None,
    "config":        {},
    "shapes":        {},
    "shape_colors":  {},
    "shape_chances": {},
    "powerups":      {},   # NUEVO
    "events":        {}
}

* Cambio 2 — Parser.parse(): distingue DEFINE SHAPE de DEFINE POWERUP con un lookahead de un token

- ANTES
            elif token_actual == 'DEFINE':
                self.parsear_shape()

- DESPUÉS
            elif token_actual == 'DEFINE':
                siguiente = (self.tokens[self.posicion + 1]
                             if self.posicion + 1 < len(self.tokens) else '')
                if siguiente == 'POWERUP':
                    self.parsear_powerup()
                else:
                    self.parsear_shape()

* Cambio 3 — Se agrega el método Parser.parsear_powerup() (no existía)

- ANTES
(no existía)

- DESPUÉS
    def parsear_powerup(self):
        self.consumir('DEFINE')
        self.consumir('POWERUP')
        nombre = self.consumir()
        self.consumir(':')
        self.consumir('TRIGGER')
        self.consumir(':')
        tipo_trigger  = self.consumir()
        valor_trigger = int(self.consumir())
        estados = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] == 'STATE':
            self.consumir('STATE')
            self.consumir()
            self.consumir(':')
            matriz = []
            while self.posicion < len(self.tokens) and self.tokens[self.posicion] == '[':
                fila = []
                self.consumir('[')
                while self.tokens[self.posicion] != ']':
                    fila.append(int(self.consumir()))
                    if self.tokens[self.posicion] == ',':
                        self.consumir(',')
                self.consumir(']')
                matriz.append(fila)
            estados.append(matriz)
        color  = '#FFFFFF'
        chance = 100
        while (self.posicion < len(self.tokens) and
               self.tokens[self.posicion] in ('COLOR', 'CHANCE')):
            atributo = self.consumir()
            self.consumir(':')
            if atributo == 'COLOR':
                color = self.consumir()
            elif atributo == 'CHANCE':
                chance = int(self.consumir())
        self.consumir('END')
        self.ast['powerups'][nombre] = {
            'trigger_type':  tipo_trigger,
            'trigger_value': valor_trigger,
            'states':        estados,
            'color':         color,
            'chance':        chance
        }

# runtime.py

* Cambio 1 — __init__(), bloque TETRIS: se agregan variables de estado para power-ups

- ANTES
            self.pieza_color = '#00FFFF'

- DESPUÉS
            self.pieza_color = '#00FFFF'
            self.lineas_ultimo_clear  = 0
            self.powerup_pendiente    = None
            self.es_powerup_activo    = False
            self.nombre_pieza_actual  = ''
            self.rotaciones_powerup   = 0
            self.modo_bomba_activo    = False
            self.degradado_frame      = 0

* Cambio 2 — tetris_rotar_pieza(): se cuenta la rotacion del TRIPLE_CLEAR_PU y se activa modo bomba

- ANTES
    def tetris_rotar_pieza(self):
        if not self.pieza_actual: return
        nueva_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual)
        if not self.tetris_verificar_colision(self.pieza_x, self.pieza_y, nueva_rotacion):
            self.pieza_rotacion = nueva_rotacion

- DESPUÉS
    def tetris_rotar_pieza(self):
        if not self.pieza_actual: return
        nueva_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual)
        if not self.tetris_verificar_colision(self.pieza_x, self.pieza_y, nueva_rotacion):
            self.pieza_rotacion = nueva_rotacion
            if self.es_powerup_activo and self.nombre_pieza_actual == 'TRIPLE_CLEAR_PU':
                self.rotaciones_powerup += 1
                if self.rotaciones_powerup >= 10 and not self.modo_bomba_activo:
                    self.modo_bomba_activo = True

* Cambio 3 — tetris_fijar_pieza(): si modo_bomba_activo elimina filas ocupadas y suma 500 pts/fila

- ANTES
    def tetris_fijar_pieza(self):
        matriz_pieza = self.pieza_actual[self.pieza_rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    ny = self.pieza_y + y_offset
                    nx = self.pieza_x + x_offset
                    if 0 <= ny < self.alto and 0 <= nx < self.ancho:
                        self.grid[ny][nx] = 1
        self.pieza_actual = None
        self.tetris_limpiar_lineas()
        self.ejecutar_evento('ON_START')

- DESPUÉS
    def tetris_fijar_pieza(self):
        matriz_pieza = self.pieza_actual[self.pieza_rotacion]
        filas_ocupadas = set()
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    ny = self.pieza_y + y_offset
                    nx = self.pieza_x + x_offset
                    if 0 <= ny < self.alto and 0 <= nx < self.ancho:
                        self.grid[ny][nx] = 1
                        filas_ocupadas.add(ny)
        self.pieza_actual = None
        if self.es_powerup_activo and self.modo_bomba_activo:
            filas_a_eliminar = sorted(filas_ocupadas)
            nuevo_grid = [fila for i, fila in enumerate(self.grid)
                          if i not in filas_a_eliminar]
            filas_borradas = len(filas_a_eliminar)
            self.grid = ([[0] * self.ancho for _ in range(filas_borradas)]
                         + nuevo_grid)
            self.puntuacion += 500 * filas_borradas
        self.es_powerup_activo   = False
        self.nombre_pieza_actual = ''
        self.rotaciones_powerup  = 0
        self.modo_bomba_activo   = False
        self.degradado_frame     = 0
        self.tetris_limpiar_lineas()
        self.ejecutar_evento('ON_START')

* Cambio 4 — tetris_limpiar_lineas(): guarda lineas_ultimo_clear y evalua triggers de powerups

- ANTES
    def tetris_limpiar_lineas(self):
        nuevo_grid = [fila for fila in self.grid if not all(fila)]
        lineas_limpias = self.alto - len(nuevo_grid)
        if lineas_limpias > 0:
            self.grid = [[0] * self.ancho for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias):
                self.ejecutar_evento('ON_LINE_CLEAR')

- DESPUÉS
    def tetris_limpiar_lineas(self):
        nuevo_grid = [fila for fila in self.grid if not all(fila)]
        lineas_limpias = self.alto - len(nuevo_grid)
        self.lineas_ultimo_clear = lineas_limpias
        if lineas_limpias > 0:
            self.grid = [[0] * self.ancho for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias):
                self.ejecutar_evento('ON_LINE_CLEAR')
            self.lineas_eliminadas_total  += lineas_limpias
            self.lineas_totales_eliminadas += lineas_limpias
            powerups = self.datos_juego.get('powerups', {})
            for nombre_pu, datos_pu in powerups.items():
                tipo  = datos_pu.get('trigger_type', '')
                valor = datos_pu.get('trigger_value', 0)
                activar = False
                if tipo == 'LINE_CUMULATIVE' and valor > 0:
                    if self.lineas_totales_eliminadas % valor == 0:
                        activar = True
                elif tipo == 'LINE_CLEAR_EXACT' and lineas_limpias == valor:
                    activar = True
                elif tipo == 'LINE_CLEAR_MIN' and lineas_limpias >= valor:
                    activar = True
                if activar:
                    self.powerup_pendiente = nombre_pu

* Cambio 5 — tetris_spawn_pieza(): si hay powerup_pendiente lo spawnea; LINE_PURGE_PU es efecto directo

- ANTES
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
        colores = self.datos_juego.get('shape_colors', {})
        self.pieza_color = colores.get(nombre_pieza, '#00FFFF')
        self.pieza_x        = self.ancho / 2 - 2
        self.pieza_y        = 0
        self.pieza_rotacion = 0
        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True

- DESPUÉS
    def tetris_spawn_pieza(self):
        if self.powerup_pendiente is not None:
            nombre_pu = self.powerup_pendiente
            self.powerup_pendiente = None
            if nombre_pu == 'LINE_PURGE_PU':
                self.flash_powerup_timer = 8
                self.nombre_pieza_actual = 'LINE_PURGE_PU'
                self.label_powerup.config(text=u'\u26A1 PURGA DE\nLINEAS \u26A1')
                filas_con_contenido = [i for i in range(self.alto) if any(self.grid[i])]
                filas_a_borrar = filas_con_contenido[-2:] if len(filas_con_contenido) >= 2 \
                                 else filas_con_contenido
                if filas_a_borrar:
                    self.grid = [fila for i, fila in enumerate(self.grid)
                                 if i not in filas_a_borrar]
                    vacias = [[0] * self.ancho for _ in range(len(filas_a_borrar))]
                    self.grid = vacias + self.grid
                self.root.after(1200, lambda: self.label_powerup.config(text=''))
            else:
                powerups = self.datos_juego.get('powerups', {})
                if nombre_pu in powerups:
                    datos_pu = powerups[nombre_pu]
                    self.pieza_actual        = datos_pu['states']
                    self.pieza_color         = datos_pu.get('color', '#FFFFFF')
                    self.es_powerup_activo   = True
                    self.nombre_pieza_actual = nombre_pu
                    self.rotaciones_powerup  = 0
                    self.modo_bomba_activo   = False
                    self.degradado_frame     = 0
                    self.flash_powerup_timer = 8
                    if nombre_pu == 'DOUBLE_CLEAR_PU':
                        self.label_powerup.config(text=u'\u2605 DOBLE\nLIMPIEZA \u2605')
                    elif nombre_pu == 'TRIPLE_CLEAR_PU':
                        self.label_powerup.config(text=u'\u26A1 TRIPLE\n\u00a1BOMBA! \u26A1')
                    else:
                        self.label_powerup.config(text=u'\u2605 POWER UP \u2605')
                    self.root.after(1800, lambda: self.label_powerup.config(text=''))
                    self.pieza_x        = self.ancho / 2 - 1
                    self.pieza_y        = 0
                    self.pieza_rotacion = 0
                    if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
                        self.juego_terminado = True
                    return
        self.es_powerup_activo   = False
        self.nombre_pieza_actual = ''
        nombres = list(self.datos_juego['shapes'].keys())
        chances = self.datos_juego.get('shape_chances', {})
        pesos   = [chances.get(n, 1) for n in nombres]
        total   = sum(pesos)
        def seleccionar_pieza_aleatoria():
            r2   = random.random() * total
            acum = 0
            elegida = nombres[-1]
            for nm, ps in zip(nombres, pesos):
                acum += ps
                if r2 < acum:
                    elegida = nm
                    break
            return elegida
        if self.pieza_siguiente is None:
            nombre_actual    = seleccionar_pieza_aleatoria()
            nombre_siguiente = seleccionar_pieza_aleatoria()
        else:
            nombre_actual    = self._nombre_siguiente
            nombre_siguiente = seleccionar_pieza_aleatoria()
        self._nombre_siguiente = nombre_siguiente
        colores = self.datos_juego.get('shape_colors', {})
        self.pieza_actual    = self.datos_juego['shapes'][nombre_actual]
        self.pieza_color     = colores.get(nombre_actual, '#00FFFF')
        self.pieza_siguiente = self.datos_juego['shapes'][nombre_siguiente]
        self.siguiente_color = colores.get(nombre_siguiente, '#00FFFF')
        self.pieza_x        = self.ancho / 2 - 2
        self.pieza_y        = 0
        self.pieza_rotacion = 0
        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True

* Cambio 6 — dibujar(): degradado animado en modo bomba

- ANTES
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            COLOR_PIEZA = self.pieza_color
            matriz_pieza = self.pieza_actual[self.pieza_rotacion]
            for y_offset, fila in enumerate(matriz_pieza):
                for x_offset, celda in enumerate(fila):
                    if celda == 1:
                        self.dibujar_celda(
                            self.pieza_x + x_offset,
                            self.pieza_y + y_offset,
                            COLOR_PIEZA
                        )

- DESPUÉS
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            if self.modo_bomba_activo:
                self.degradado_frame = (self.degradado_frame + 8) % 360
                r2, g2, b2 = self._hsv_a_rgb(self.degradado_frame)
                COLOR_PIEZA = '#{:02X}{:02X}{:02X}'.format(r2, g2, b2)
            else:
                COLOR_PIEZA = self.pieza_color
            matriz_pieza = self.pieza_actual[self.pieza_rotacion]
            for y_offset, fila in enumerate(matriz_pieza):
                for x_offset, celda in enumerate(fila):
                    if celda == 1:
                        self.dibujar_celda_estilo(
                            self.pieza_x + x_offset,
                            self.pieza_y + y_offset,
                            COLOR_PIEZA
                        )

==============================================
BLOQUE 2 — Mejoras visuales y nuevo PowerUp LINE_PURGE_PU
==============================================

# tetris.brick

* Cambio 1 — Se agrega LINE_PURGE_PU (el tercer powerup, ya mostrado arriba en el Bloque 1)
  No hay cambio adicional en este archivo más allá del bloque DEFINE POWERUP LINE_PURGE_PU.

# tetris.bnf

* Cambio 1 — <tipo_trigger>: se agrega LINE_CUMULATIVE como tipo valido
- ANTES
<tipo_trigger> ::= "LINE_CLEAR_EXACT" | "LINE_CLEAR_MIN"
- DESPUÉS
<tipo_trigger> ::= "LINE_CLEAR_EXACT" | "LINE_CLEAR_MIN" | "LINE_CUMULATIVE"

# compiler.py

  No se realizan cambios adicionales. El token LINE_CUMULATIVE es reconocido
  automaticamente por el lexer existente como palabra en mayusculas, y queda
  almacenado en trigger_type dentro del JSON sin modificacion alguna.

# runtime.py

* Cambio 1 — __init__(), GUI: panel lateral rediseñado con fondo oscuro, acento violeta,
  label de lineas, canvas de preview y label de powerup activo

- ANTES
        self.canvas = tk.Canvas(
            self.root,
            width=self.ancho_canvas,
            height=self.alto_canvas,
            bg='#111111'
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.marco_score = tk.Frame(
            self.root, width=150, height=self.alto_canvas, bg='#222222'
        )
        self.marco_score.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.label_score = tk.Label(
            self.marco_score,
            text="PUNTUACION\n0",
            bg='#222222', fg='white',
            font=('Consolas', 16, 'bold')
        )
        self.label_score.pack(pady=40, padx=10)
        self.label_controles = tk.Label(
            self.marco_score,
            text="CONTROLES\nFlechas: Mover/Rotar",
            bg='#222222', fg='gray',
            font=('Consolas', 10)
        )
        self.label_controles.pack(pady=20, padx=10)

- DESPUÉS
        self.root.configure(bg='#0A0A0F')
        self.canvas = tk.Canvas(
            self.root,
            width=self.ancho_canvas,
            height=self.alto_canvas,
            bg='#0D0D1A',
            highlightthickness=3,
            highlightbackground='#1A1A3A'
        )
        self.canvas.pack(side=tk.LEFT, padx=12, pady=12)
        PANEL_BG  = '#111120'
        self.marco_score = tk.Frame(self.root, width=160, bg=PANEL_BG)
        self.marco_score.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=12)
        self.marco_score.pack_propagate(False)
        tk.Label(self.marco_score, text='RETROBRIK',
                 bg=PANEL_BG, fg='#7B2FBE',
                 font=('Consolas', 13, 'bold')).pack(pady=(18, 2))
        tk.Label(self.marco_score, text=u'\u2500' * 14,
                 bg=PANEL_BG, fg='#333355', font=('Consolas', 9)).pack()
        tk.Label(self.marco_score, text='PUNTUACION',
                 bg=PANEL_BG, fg='#AAAACC',
                 font=('Consolas', 9, 'bold')).pack(pady=(14, 0))
        self.label_score = tk.Label(self.marco_score, text='0',
                                    bg=PANEL_BG, fg='#FFFFFF',
                                    font=('Consolas', 22, 'bold'))
        self.label_score.pack(pady=(2, 8))
        tk.Label(self.marco_score, text='LINEAS',
                 bg=PANEL_BG, fg='#AAAACC',
                 font=('Consolas', 9, 'bold')).pack(pady=(4, 0))
        self.label_lineas = tk.Label(self.marco_score, text='0',
                                     bg=PANEL_BG, fg='#00FFCC',
                                     font=('Consolas', 16, 'bold'))
        self.label_lineas.pack(pady=(2, 8))
        tk.Label(self.marco_score, text=u'\u2500' * 14,
                 bg=PANEL_BG, fg='#333355', font=('Consolas', 9)).pack()
        tk.Label(self.marco_score, text='SIGUIENTE',
                 bg=PANEL_BG, fg='#AAAACC',
                 font=('Consolas', 9, 'bold')).pack(pady=(10, 4))
        self.preview_canvas = tk.Canvas(self.marco_score,
                                        width=5 * 22, height=5 * 22,
                                        bg='#0A0A18',
                                        highlightthickness=1,
                                        highlightbackground='#333366')
        self.preview_canvas.pack(pady=(0, 10))
        tk.Label(self.marco_score, text=u'\u2500' * 14,
                 bg=PANEL_BG, fg='#333355', font=('Consolas', 9)).pack()
        self.label_powerup = tk.Label(self.marco_score, text='',
                                      bg=PANEL_BG, fg='#FF00FF',
                                      font=('Consolas', 8, 'bold'),
                                      wraplength=140, justify=tk.CENTER)
        self.label_powerup.pack(pady=(8, 4))
        tk.Label(self.marco_score, text=u'\u2500' * 14,
                 bg=PANEL_BG, fg='#333355', font=('Consolas', 9)).pack(pady=(4, 0))
        tk.Label(self.marco_score,
                 text=u'\u2190\u2192  Mover\n\u2191     Rotar\n\u2193     Bajar',
                 bg=PANEL_BG, fg='#555577',
                 font=('Consolas', 9)).pack(pady=(8, 16))

* Cambio 2 — __init__(), bloque TETRIS: se agregan variables para visual y preview

- ANTES
            self.degradado_frame      = 0

- DESPUÉS
            self.degradado_frame          = 0
            self.lineas_totales_eliminadas = 0
            self.pieza_siguiente           = None
            self.siguiente_color           = '#FFFFFF'
            self.flash_powerup_timer       = 0
            self.borde_arcoiris_frame      = 0
            self.lineas_eliminadas_total   = 0
            self._nombre_siguiente         = None

* Cambio 3 — dibujar(): borde arcoiris, rejilla de fondo, celdas con profundidad,

  flash de pantalla, letrero POWER UP y llamada a dibujar_preview()
- ANTES
    def dibujar(self):
        self.canvas.delete("all")
        self.label_score.config(text="PUNTUACION\n" + str(self.puntuacion))
        COLOR_GRID_FIJA    = '#343434'
        ...
        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    self.dibujar_celda(x, y, COLOR_GRID_FIJA)

- DESPUÉS
    def dibujar(self):
        self.canvas.delete("all")
        self.label_score.config(text=str(self.puntuacion))
        if self.tipo_juego == 'TETRIS':
            self.label_lineas.config(text=str(self.lineas_eliminadas_total))
        if self.tipo_juego == 'TETRIS' and self.modo_bomba_activo:
            self.borde_arcoiris_frame = (self.borde_arcoiris_frame + 6) % 360
            r2, g2, b2 = self._hsv_a_rgb(self.borde_arcoiris_frame)
            self.canvas.config(
                highlightbackground='#{:02X}{:02X}{:02X}'.format(r2, g2, b2)
            )
        else:
            self.canvas.config(highlightbackground='#1A1A3A')
        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    intensidad = int(40 + (float(y) / self.alto) * 30)
                    color_fija = '#{:02X}{:02X}{:02X}'.format(
                        intensidad + 10, intensidad, intensidad + 25
                    )
                    self.dibujar_celda_estilo(x, y, color_fija)
                else:
                    ts = self.taman_celda
                    self.canvas.create_rectangle(
                        x * ts, y * ts, x * ts + ts, y * ts + ts,
                        fill='', outline='#151525'
                    )
        ...
        if self.tipo_juego == 'TETRIS' and self.flash_powerup_timer > 0:
            self.flash_powerup_timer -= 1
            if self.flash_powerup_timer % 2 == 0:
                self.canvas.create_rectangle(
                    0, 0, self.ancho_canvas, self.alto_canvas,
                    fill='#220033', outline=''
                )
            if self.flash_powerup_timer > 2:
                self.canvas.create_text(
                    self.ancho_canvas / 2, self.alto_canvas / 2 - 16,
                    text='! POWER UP !', fill='#FF00FF',
                    font=('Consolas', 18, 'bold')
                )
                self.canvas.create_text(
                    self.ancho_canvas / 2, self.alto_canvas / 2 + 12,
                    text=self.nombre_pieza_actual, fill='#FF88FF',
                    font=('Consolas', 10)
                )
        if self.tipo_juego == 'TETRIS':
            self.dibujar_preview()

* Cambio 4 — dibujar_celda(): se mantiene sin modificar (retrocompatibilidad).
  Se agregan tres metodos nuevos a continuacion:

- ANTES
(solo existia dibujar_celda)
- DESPUÉS (metodos nuevos agregados)
    def dibujar_celda_estilo(self, x, y, color, canvas=None, tam=None):
        c  = canvas if canvas else self.canvas
        ts = tam    if tam    else self.taman_celda
        x1, y1 = x * ts + 1, y * ts + 1
        x2, y2 = x1 + ts - 2, y1 + ts - 2
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        hl = '#{:02X}{:02X}{:02X}'.format(
            min(255, r + 60), min(255, g + 60), min(255, b + 60)
        )
        sh = '#{:02X}{:02X}{:02X}'.format(
            max(0, r - 50), max(0, g - 50), max(0, b - 50)
        )
        c.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        c.create_line(x1, y2, x1, y1, fill=hl, width=2)
        c.create_line(x1, y1, x2, y1, fill=hl, width=2)
        c.create_line(x2, y1, x2, y2, fill=sh, width=2)
        c.create_line(x1, y2, x2, y2, fill=sh, width=2)

    def dibujar_preview(self):
        self.preview_canvas.delete("all")
        if not self.pieza_siguiente:
            return
        tam_cel = 22
        matriz  = self.pieza_siguiente[0]
        alto_m  = len(matriz)
        ancho_m = len(matriz[0]) if alto_m > 0 else 0
        offset_x = (5 - ancho_m) / 2
        offset_y = (5 - alto_m)  / 2
        for fy, fila in enumerate(matriz):
            for fx, celda in enumerate(fila):
                if celda == 1:
                    self.dibujar_celda_estilo(
                        offset_x + fx, offset_y + fy,
                        self.siguiente_color,
                        canvas=self.preview_canvas,
                        tam=tam_cel
                    )

    def _hsv_a_rgb(self, h):
        sector = int(h / 60) % 6
        f      = (h / 60.0) - int(h / 60)
        if sector == 0:   return 255,            int(255 * f),     0
        elif sector == 1: return int(255*(1-f)), 255,              0
        elif sector == 2: return 0,              255,              int(255 * f)
        elif sector == 3: return 0,              int(255 * (1-f)), 255
        elif sector == 4: return int(255 * f),   0,                255
        else:             return 255,             0,                int(255*(1-f))

* Cambio 5 — tetris_fijar_pieza(): al terminar un powerup se limpia borde y label del panel

- ANTES
        self.modo_bomba_activo   = False
        self.degradado_frame     = 0
        
- DESPUÉS
        self.modo_bomba_activo   = False
        self.degradado_frame     = 0
        self.canvas.config(highlightbackground='#1A1A3A')
        self.label_powerup.config(text='')

---------------------------------------------------------------------------------------------------------------------
                                Retrocompatibilidad — Separación Visual Original vs Remake
---------------------------------------------------------------------------------------------------------------------

Se identificó que las mejoras visuales del Punto C (panel rediseñado, preview de siguiente pieza,
celdas con borde biselado, borde arcoiris, flash de power-up) se aplicaban también al tetris.json
original y al snake.json, rompiendo la Regla de Oro de retrocompatibilidad.

Para corregirlo se introdujo un campo "version" en el JSON y una bandera self.es_remake en el
runtime que actúa como interruptor: los archivos originales ejecutan exactamente la GUI clásica,
y solo los archivos remake activan el estilo mejorado.

# compiler.py

* Cambio 1 — Parser.__init__(): se agrega "version" al AST con valor por defecto "original"

- ANTES
        self.ast = {
            "tipo_juego":    None,
            "config":        {},
            "shapes":        {},
            "shape_colors":  {},
            "shape_chances": {},
            "powerups":      {},
            "events":        {}
        }
- DESPUÉS
        self.ast = {
            "version":       "original",   # NUEVO: valor por defecto para todos los .brick
            "tipo_juego":    None,
            "config":        {},
            "shapes":        {},
            "shape_colors":  {},
            "shape_chances": {},
            "powerups":      {},
            "events":        {}
        }

* Cambio 2 — bloque __main__: detectar 'remake' en el nombre del archivo y sobreescribir
  el campo "version" antes de llamar a parser.parse()

- ANTES
        tokens = lexer(codigo)
        parser = Parser(tokens)
        ast    = parser.parse()
- DESPUÉS
        tokens = lexer(codigo)
        parser = Parser(tokens)
        if 'remake' in archivo_entrada:
            parser.ast['version'] = 'remake'
        ast    = parser.parse()

# games/tetris.json

* Cambio 1 — se agrega el campo "version" manualmente (el archivo ya existia compilado)

- ANTES
{
  "tipo_juego": "TETRIS",
  ...
}
- DESPUÉS
{
  "version": "original",
  "tipo_juego": "TETRIS",
  ...
}

# games/tetris_remake.json

* Cambio 1 — se agrega el campo "version" manualmente
- ANTES
{
  "tipo_juego": "TETRIS",
  ...
}
- DESPUÉS
{
  "version": "remake",
  "tipo_juego": "TETRIS",
  ...
}

# games/snake.json

* Cambio 1 — se agrega el campo "version" manualmente

- ANTES
{
  "tipo_juego": "SNAKE",
  ...
}
- DESPUÉS
{
  "version": "original",
  "tipo_juego": "SNAKE",
  ...
}

# runtime.py

* Cambio 1 — __init__(): leer el campo "version" del JSON y definir self.es_remake

- ANTES
        self.tipo_juego = self.datos_juego.get('tipo_juego', 'TETRIS')
        config = self.datos_juego.get('config', {})
- DESPUÉS
        self.tipo_juego = self.datos_juego.get('tipo_juego', 'TETRIS')
        self.es_remake  = (self.datos_juego.get('version', 'original') == 'remake')
        config = self.datos_juego.get('config', {})

* Cambio 2 — __init__(), GUI: el bloque de construccion del panel se divide en dos

  caminos segun self.es_remake. El camino False reconstruye la GUI clasica exacta;
  el camino True construye el panel mejorado. Al final del bloque False se inicializan
  label_lineas, label_powerup y preview_canvas como None para evitar AttributeError.
- ANTES
        self.root.configure(bg='#0A0A0F')
        self.canvas = tk.Canvas(..., bg='#0D0D1A', highlightthickness=3, ...)
        ... (panel mejorado siempre)
- DESPUÉS
        if self.es_remake:
            self.root.configure(bg='#0A0A0F')
            self.canvas = tk.Canvas(..., bg='#0D0D1A', highlightthickness=3, ...)
            ... (panel mejorado)
        else:
            self.canvas = tk.Canvas(..., bg='#111111')
            ... (panel clasico original)
            self.label_lineas   = None
            self.label_powerup  = None
            self.preview_canvas = None

* Cambio 3 — dibujar(): cada efecto visual exclusivo del remake se guarda con

  if self.es_remake. El camino original usa dibujar_celda() con color fijo '#343434'.
  Cambios puntuales aplicados:
  - label_score: el original usa formato 'PUNTUACION\n0'; el remake muestra solo el numero.
  - Borde arcoiris: envuelto en if self.es_remake.
  - Loop de cuadricula: celdas fijas usan dibujar_celda('#343434') en original y
    dibujar_celda_estilo() con profundidad de color en remake. Rejilla sutil solo en remake.
  - Pieza activa: dibujar_celda() en original, dibujar_celda_estilo() en remake.
  - Snake y comida: dibujar_celda() en original, dibujar_celda_estilo() en remake.
  - Flash de power-up y llamada a dibujar_preview(): envueltos en if self.es_remake.

* Cambio 4 — tetris_spawn_pieza() y tetris_fijar_pieza(): todas las referencias a
  self.label_powerup.config() se protegen con:
        if self.es_remake and self.label_powerup:
            self.label_powerup.config(...)
  y el reset del borde del canvas se protege con:
        if self.es_remake:
            self.canvas.config(highlightbackground='#1A1A3A')

Resultado final:
  jugar tetris        -> GUI clasica, sin ningun efecto del remake.
  jugar snake         -> GUI clasica, sin ningun efecto del remake.
  jugar tetris_remake -> Panel mejorado, preview, power-ups visuales y borde arcoiris.
  jugar snake_remake  -> (cuando exista) activara automaticamente el estilo mejorado
                         solo por tener 'remake' en el nombre del archivo.

---------------------------------------------------------------------------------------------------------------------
                                    Cambios realizados (Actividad 4 - Snake).
---------------------------------------------------------------------------------------------------------------------

Se implemento la Actividad 4: Evolucion del Lenguaje y Logica de Niveles (Caso Snake).
Los cambios garantizan retrocompatibilidad: el snake.brick original sigue siendo compilable
y ejecutable sin errores.

==============================================
A. Personalizacion Geometrica de la Serpiente
==============================================

# snake.brick

* Cambio 1 — Se agrega un segundo SHAPE de tipo TRIANGULAR para demostrar la nueva forma:

- ANTES
(solo existia PIXEL con SHAPE_TYPE: CIRCULAR)

- DESPUES
DEFINE SHAPE PIXEL_TRI:
  STATE 1:
    [1]
  SHAPE_TYPE: TRIANGULAR
END

* Cambio 2 — Se mantiene LEVEL NYAN_CAT en el archivo para activar el nivel mas alto.

# snake.bnf

* Cambio 1 — <programa>: se agrega <nivel_opcional> como elemento del programa

- ANTES
<programa> ::= <tipo_juego> <grid> <definiciones> <eventos>

- DESPUES
<programa> ::= <tipo_juego> <grid> <nivel_opcional> <definiciones> <eventos>

* Cambio 2 — Se agrega la regla <nivel_opcional> y <nombre_nivel> (no existian)

- ANTES
(no existian estas reglas)

- DESPUES
<nivel_opcional> ::= "LEVEL" <nombre_nivel> | e
<nombre_nivel>   ::= "BABY" | "EASY" | "MEDIUM" | "HARD" | "NYAN_CAT"

* Cambio 3 — <definicion_shape>: se agrega <atributos_shape_opcionales> antes del END

- ANTES
<definicion_shape> ::= "DEFINE" "SHAPE" <identificador> ":" <estados> "END"

- DESPUES
<definicion_shape> ::= "DEFINE" "SHAPE" <identificador> ":" <estados> <atributos_shape_opcionales> "END"

* Cambio 4 — Se agregan reglas para SHAPE_TYPE (no existian)

- ANTES
(no existian estas reglas)

- DESPUES
<atributos_shape_opcionales> ::= <atributo_shape> <atributos_shape_opcionales> | e
<atributo_shape>             ::= <atributo_shape_type>
<atributo_shape_type>        ::= "SHAPE_TYPE" ":" <tipo_forma>
<tipo_forma>                 ::= "RECTANGULAR" | "CIRCULAR" | "TRIANGULAR"

# runtime.py — Seccion de dibujo del Snake

* Cambio 1 — Se corrigio un bug critico de indentacion en el bloque de dibujo del cuerpo.
  El codigo anterior usaba 'if / if / elif / elif / else' donde el segundo 'if' nunca
  pasaba al 'elif' cuando la cabeza ya habia sido dibujada. Ahora la estructura es
  'if (cabeza NYAN_CAT) / elif CIRCULAR / elif TRIANGULAR / else (RECTANGULAR)'.

- ANTES (estructura incorrecta)
                if self.level == 'NYAN_CAT':
                    color = self.nyan_colors[...]
                if i == 0 and self.level == 'NYAN_CAT':   # segundo 'if', no 'elif'
                    [dibuja cara]
                # Oreja izquierda
                    [...]
                # Snake circular
                elif self.snake_shape == 'CIRCULAR':      # nunca se ejecuta si i==0
                    [...]

- DESPUES (estructura corregida)
                if i == 0 and self.level == 'NYAN_CAT':
                    [dibuja cara de gato]
                elif self.snake_shape == 'CIRCULAR':
                    self.canvas.create_oval(px, py, px2, py2, fill=color, ...)
                elif self.snake_shape == 'TRIANGULAR':
                    self.canvas.create_polygon(..., fill=color, ...)
                else:
                    self.dibujar_celda / self.dibujar_celda_estilo (RECTANGULAR)

* Cambio 2 — Se implementa la forma TRIANGULAR para los segmentos del cuerpo.
  Usa create_polygon() con tres vertices: punta superior centrada, esquina inferior
  izquierda y esquina inferior derecha de la celda.

==============================================
B. Logica de Niveles (BABY, EASY, MEDIUM, HARD, NYAN_CAT)
==============================================

# runtime.py — Bloque SNAKE en __init__()

* Cambio 1 — Se elimina la velocidad fija (0.15) y se reemplaza por un mapa de velocidades
  indexado por nivel. Cada nivel tiene su propia velocidad de ON_TICK:

- ANTES
            self.velocidad_gravedad = 0.15

- DESPUES
            velocidades_nivel = {
                'BABY':     0.20,   # muy lenta
                'EASY':     0.15,   # velocidad original (retrocompat)
                'MEDIUM':   0.10,   # moderada
                'HARD':     0.06,   # rapida
                'NYAN_CAT': 0.08,   # similar a HARD con efectos visuales
            }
            self.velocidad_gravedad = velocidades_nivel.get(self.level, 0.15)

  RETROCOMPATIBILIDAD: si el JSON no tiene campo 'level', get() devuelve 'BABY'
  (ya inicializado con ese default) y velocidades_nivel.get() devuelve 0.15, que es
  exactamente la velocidad que tenia el snake original.

* Cambio 2 — Se muestra el nivel activo en el titulo de la ventana:

- ANTES
        self.root.title("BrickScript - " + self.tipo_juego)

- DESPUES (solo para SNAKE)
            self.root.title('BrickScript - SNAKE  |  Nivel: ' + self.level)

* Cambio 3 — Color de los segmentos indexado por nivel:

- ANTES
                color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO

- DESPUES
                if self.level == 'NYAN_CAT':
                    color = self.nyan_colors[i % len(self.nyan_colors)]
                elif self.level == 'HARD':
                    intensidad = max(80, 255 - i * 8)
                    color = '#{:02X}{:02X}{:02X}'.format(intensidad, 0, 0)
                elif self.level == 'MEDIUM':
                    intensidad = max(60, 220 - i * 6)
                    color = '#{:02X}{:02X}{:02X}'.format(intensidad, intensidad // 2, 0)
                elif self.level == 'EASY':
                    intensidad = max(80, 200 - i * 5)
                    color = '#{:02X}{:02X}{:02X}'.format(0, intensidad, 0)
                else:  # BABY
                    color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO

# games/snake.json

* Cambio 1 — Se agrega el shape PIXEL_TRI con SHAPE_TYPE TRIANGULAR al JSON compilado:
  "shape_types": { "PIXEL": "CIRCULAR", "PIXEL_TRI": "TRIANGULAR" }

==============================================
Retrocompatibilidad garantizada
==============================================

- El snake.brick original (sin LEVEL ni SHAPE_TYPE) se compila y ejecuta sin errores:
  el campo 'level' tiene default 'BABY' en el compiler y en el runtime, y el campo
  'shape_types' devuelve {} si no existe, por lo que snake_shape queda 'RECTANGULAR'.
- El tetris.brick y tetris_remake.brick no son afectados por ningun cambio del Snake.


==============================================
Correcciones post-entrega (Actividad 4)
==============================================

# games/snake.brick y games/snake.json

* Correccion: se restauraron a su estado ORIGINAL sin LEVEL ni SHAPE_TYPE, garantizando
  retrocompatibilidad total. El snake original sigue ejecutandose exactamente igual que antes.

# games/snake_evolved.brick (NUEVO) y games/snake_evolved.json (NUEVO)

* Se crean los archivos snake_evolved.brick y snake_evolved.json como la version evolucionada
  del Snake. Estos son los archivos que implementan la Actividad 4 completa:
  - LEVEL NYAN_CAT (nivel maximo alcanzable)
  - DEFINE SHAPE PIXEL con SHAPE_TYPE: CIRCULAR
  - DEFINE SHAPE PIXEL_TRI con SHAPE_TYPE: TRIANGULAR
  El campo "version": "remake" en el JSON activa el estilo visual mejorado.

# runtime.py — logica de forma segun nivel

* Correccion critica: la forma del segmento ahora cambia dinamicamente segun el nivel
  actual (no el definido en el .brick), lo que hace visible la progresion:
  - BABY / EASY / MEDIUM -> CIRCULAR (suave, amigable)
  - HARD / NYAN_CAT      -> TRIANGULAR (agresivo, avanzado)

  Si el JSON no tiene shape_type (snake.json original), la forma queda RECTANGULAR
  y el comportamiento es identico al original.

* La cara de gato (cabeza especial) solo aparece cuando self.level == 'NYAN_CAT',
  es decir, solo despues de acumular 500 puntos al jugar snake_evolved.
  Al jugar snake.json (original), self.level nunca llega a NYAN_CAT
  (nivel maximo = BABY), por lo que la cabeza jamas aparece.
