    # -*- coding: utf-8 -*-
# Cambios (Actividad 3 - Punto B):
# 1. LEXER - funcion lexer():
#    - La expresion regular de comentarios ahora preserva los colores hexadecimales
#      (#RRGGBB) antes de eliminar el resto de lineas de comentario.
#    - Se agrega el patron '#[0-9A-Fa-f]{6}' al token_regex para capturar
#      colores hex como un solo token (ej. '#FF5733').
# 2. PARSER - clase Parser.__init__():
#    - Se agregan dos nuevas claves al AST: 'shape_colors' y 'shape_chances'.
#    - Esto permite almacenar los atributos de cada figura de forma separada,
#      manteniendo 'shapes' con el formato original (lista de estados).
# 3. PARSER - metodo parsear_shape():
#    - Despues de leer todos los estados (STATE), se intenta leer los atributos
#      opcionales COLOR y CHANCE.
#    - Si no estan presentes (archivo .brick antiguo), se asignan valores por
#      defecto: color '#00FFFF' y chance 1.

# Cambios (Actividad 3 - Punto C):
# 5. PARSER - metodo parsear_powerup() (Actividad 3 - Punto C):
#    - Se agrega metodo parsear_powerup() que lee bloques DEFINE POWERUP.
#    - Se agrega la clave 'powerups' al AST.
#    - parse() ahora distingue DEFINE SHAPE de DEFINE POWERUP con un lookahead
#      de un token (sin consumir).
#    - Retrocompatibilidad: si el .brick no tiene POWERUP, 'powerups' queda
#      como diccionario vacio {} y el runtime lo ignora.

# NOTA: El resto del codigo (parsear_tipo_juego, parsear_grid, parsear_evento,
# generar_codigo y el bloque __main__) NO fue modificado.

import sys
import re
import json

def lexer(codigo_fuente):
    # CAMBIO 1: Eliminar comentarios preservando colores hexadecimales.
    # Problema original: la expresion r'#.*' borraba todo desde '#' en adelante,
    # incluyendo valores como '#FF5733' usados en el atributo COLOR.
    # Solucion: el patron de comentario ahora usa un negative lookahead
    # (?![0-9A-Fa-f]{6}) para NO eliminar '#' cuando va seguido de exactamente
    # 6 caracteres hexadecimales (formato de color RGB).
    codigo_fuente = re.sub(r'#(?![0-9A-Fa-f]{6}).*', '', codigo_fuente)

    # CAMBIO 2: Capturar colores hexadecimales como un token completo.
    # Se agrega '#[0-9A-Fa-f]{6}' al inicio del alternation del regex para que
    # el lexer devuelva '#FF5733' como un unico token en lugar de fragmentos.
    # El orden importa: este patron debe ir ANTES que los demas para tener
    # prioridad cuando 're.findall' aplica el regex de izquierda a derecha.
    token_regex = r'#[0-9A-Fa-f]{6}|\b[A-Z_]+\b|\d+|[\[\](),:]'
    tokens = re.findall(token_regex, codigo_fuente)
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        # CAMBIO 3: Se agregan 'shape_colors' y 'shape_chances' al AST.
        # - 'shapes'        -> {nombre: [lista_de_estados]}   (sin cambios)
        # - 'shape_colors'  -> {nombre: '#RRGGBB'}             (NUEVO)
        # - 'shape_chances' -> {nombre: peso_entero}           (NUEVO)
        # Mantener 'shapes' en su formato original garantiza que el runtime
        # antiguo siga funcionando.
        self.ast = {
            "version":       "original", # NUEVO: valor por defecto para todos los .brick
            "tipo_juego":    None,
            "config":        {},
            "shapes":        {},
            "shape_colors":  {},
            "shape_chances": {},
            "shape_types":   {},      # NUEVO
            "level":         "BABY",  # NUEVO
            "powerups":      {},   # NUEVO (Actividad 3 - Punto C)
            "levels": {},      # NUEVO — Punto C: configuración de niveles desde gramática
            "events":        {}
        }

    def parse(self):
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual == 'GAME_TYPE':
                self.parsear_tipo_juego()
            elif token_actual == 'GAME_GRID':
                self.parsear_grid()
            elif token_actual == 'LEVEL':
                self.consumir('LEVEL')
                self.ast['level'] = self.consumir()
            elif token_actual == 'DEFINE':
                siguiente = (self.tokens[self.posicion + 1]
                            if self.posicion + 1 < len(self.tokens) else '')
                if siguiente == 'POWERUP':
                    self.parsear_powerup()
                elif siguiente == 'LEVELS':        
                    self.parsear_levels()          
                else:
                    self.parsear_shape()
            elif token_actual == 'ON':
                self.parsear_evento()
            else:
                self.posicion += 1
        return self.ast

    def consumir(self, token_esperado=None):
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            if token_esperado and token != token_esperado:
                raise Exception(
                    "Error de sintaxis: Se esperaba '" + token_esperado +
                    "' pero se encontro '" + token + "'"
                )
            self.posicion += 1
            return token
        if token_esperado:
            raise Exception(
                "Error de sintaxis: Se esperaba '" + token_esperado +
                "' pero se llego al final del archivo."
            )
        return None

    def parsear_tipo_juego(self):
        self.consumir('GAME_TYPE')
        self.ast['tipo_juego'] = self.consumir()

    def parsear_grid(self):
        self.consumir('GAME_GRID')
        self.consumir('(')
        ancho = int(self.consumir())
        self.consumir(',')
        alto = int(self.consumir())
        self.consumir(')')
        self.ast['config']['grid_size'] = [ancho, alto]

    def parsear_shape(self):
        self.consumir('DEFINE')
        self.consumir('SHAPE')
        nombre_shape = self.consumir()
        self.consumir(':')

        # --- Leer los estados de rotacion (sin cambios) ---
        estados = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] == 'STATE':
            self.consumir('STATE')
            self.consumir()   # numero del estado (1, 2, 3, 4)
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

        # CAMBIO 4: Leer atributos opcionales COLOR y CHANCE.
        # Se usan valores por defecto para garantizar retrocompatibilidad:
        # - color   = '#00FFFF' (cyan, igual al valor quemado del runtime original)
        # - chance  = 1         (peso neutro; todas las piezas tendran igual prob.)
        # El bucle lee tokens opcionales antes del END. Si el archivo .brick
        # antiguo no los tiene, se salta directamente al consumir('END').
        shape_type = 'RECTANGULAR'
        color  = '#00FFFF'  # valor por defecto (retrocompatible)
        chance = 1          # valor por defecto (retrocompatible)

        while (self.posicion < len(self.tokens) and
            self.tokens[self.posicion] in ('COLOR', 'CHANCE', 'SHAPE_TYPE')):
            atributo = self.consumir()
            self.consumir(':')

            if atributo == 'COLOR':
                # El token es '#RRGGBB' capturado por el lexer como un unico token
                color = self.consumir()

            elif atributo == 'CHANCE':
                # El token es un numero entero que representa el peso relativo
                chance = int(self.consumir())
            elif atributo == 'SHAPE_TYPE':
                shape_type = self.consumir()

        self.consumir('END')

        # Guardar estados en el formato original (lista de matrices)
        self.ast['shapes'][nombre_shape] = estados

        # Guardar atributos de personalizacion en campos separados del AST
        self.ast['shape_colors'][nombre_shape]  = color
        self.ast['shape_chances'][nombre_shape] = chance
        self.ast['shape_types'][nombre_shape]   = shape_type

    def parsear_powerup(self):
        self.consumir('DEFINE')
        self.consumir('POWERUP')
        nombre_pu = self.consumir()
        self.consumir(':')

        # Atributos de power-up
        tipo_trigger  = None
        valor_trigger = None
        duracion      = None
        estados       = []
        color         = '#FFFFFF'
        chance        = 100
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] != 'END':
            token = self.tokens[self.posicion]
            if token == 'TRIGGER':
                self.consumir('TRIGGER')
                self.consumir(':')
                tipo_trigger  = self.consumir()
                valor_trigger = int(self.consumir())
            elif token == 'DURATION':
                self.consumir('DURATION')
                self.consumir(':')
                duracion      = int(self.consumir())
            # DURATION_SECONDS: duracion del power-up expresada en segundos.
            # Conversion: 1 segundo = 20 ticks (game-loop a 50 ms).
            # Se almacena en 'duration' (ticks) para que el runtime
            # lo consuma igual que si se hubiera usado DURATION.
            elif token == 'DURATION_SECONDS':
                self.consumir('DURATION_SECONDS')
                self.consumir(':')
                segundos = int(self.consumir())
                # Convertir: cada iteracion del game-loop dura 50 ms -> 20 iter/s
                duracion = segundos * 20
            elif token == 'COLOR':
                self.consumir('COLOR')
                self.consumir(':')
                color         = self.consumir()
            elif token == 'CHANCE':
                self.consumir('CHANCE')
                self.consumir(':')
                chance        = int(self.consumir())
            elif token == 'STATE':
                self.consumir('STATE')
                self.consumir() # num estado
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
            else:
                # Si es un token desconocido, lo saltamos
                self.posicion += 1

        self.consumir('END')

        self.ast['powerups'][nombre_pu] = {
            'trigger_type': tipo_trigger,
            'trigger_value': valor_trigger,
            'duration': duracion,
            'states': estados,
            'color': color,
            'chance': chance
        }

    def parsear_levels(self):
        """
        Parsea el bloque:
            DEFINE LEVELS:
                LEVEL BABY:
                    SPEED: 15
                    HAS_POISON: FALSE
                    HAS_OBSTACLES: FALSE
                    MIN_SCORE: 0
                END
                ...
            END
        Resultado en self.ast['levels']:
            {
                "BABY":     {"speed": 15, "has_poison": False, "has_obstacles": False, "min_score": 0},
                "EASY":     {...},
                ...
            }
        """
        self.consumir('DEFINE')
        self.consumir('LEVELS')
        self.consumir(':')

        while self.posicion < len(self.tokens) and self.tokens[self.posicion] != 'END':
            if self.tokens[self.posicion] == 'LEVEL':
                self.consumir('LEVEL')
                nombre_nivel = self.consumir()   # BABY, ENTUSIASTA, NYAN_CAT (y EASY/MEDIUM/HARD por retrocompat)
                self.consumir(':')

                cfg = {
                    'speed':         15,    # valor por defecto (0.15 s/tick)
                    'has_poison':    False,
                    'has_obstacles': False,
                    # has_powerup: controla si el escudo puede aparecer.
                    # Default False -> retrocompatible con .brick sin este atributo.
                    'has_powerup':   False,
                    'min_score':     0,
                }

                while self.posicion < len(self.tokens) and self.tokens[self.posicion] != 'END':
                    atrib = self.tokens[self.posicion]
                    if atrib == 'SPEED':
                        self.consumir('SPEED')
                        self.consumir(':')
                        cfg['speed'] = int(self.consumir())
                    elif atrib == 'HAS_POISON':
                        self.consumir('HAS_POISON')
                        self.consumir(':')
                        cfg['has_poison'] = (self.consumir() == 'TRUE')
                    elif atrib == 'HAS_OBSTACLES':
                        self.consumir('HAS_OBSTACLES')
                        self.consumir(':')
                        cfg['has_obstacles'] = (self.consumir() == 'TRUE')
                    # HAS_POWERUP determina si el escudo aparece en este nivel.
                    # True en ENTUSIASTA y NYAN_CAT; False en BABY.
                    elif atrib == 'HAS_POWERUP':
                        self.consumir('HAS_POWERUP')
                        self.consumir(':')
                        cfg['has_powerup'] = (self.consumir() == 'TRUE')
                    elif atrib == 'MIN_SCORE':
                        self.consumir('MIN_SCORE')
                        self.consumir(':')
                        cfg['min_score'] = int(self.consumir())
                    else:
                        self.posicion += 1   # token desconocido, saltar

                self.consumir('END')   # END del LEVEL interno
                self.ast['levels'][nombre_nivel] = cfg
            else:
                self.posicion += 1

        self.consumir('END')   # END del DEFINE LEVELS

    # FUNCION CORREGIDA
    def parsear_evento(self):
        self.consumir('ON')
        nombre_evento = 'ON_' + self.consumir()
        self.consumir(':')
        acciones = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] != 'END':
            verbo = self.consumir()

            # Verbos que NO requieren objeto ni parametros
            if verbo in ('GAME_OVER', 'RESET_SCORE', 'GRANT_SHIELD'):
                acciones.append({'accion': verbo, 'objeto': None, 'params': []})
                continue

            # Verbos que consumen un valor numerico como "objeto"
            # (INCREASE_SCORE 10, DECREASE_SCORE 5)
            if verbo in ('INCREASE_SCORE', 'DECREASE_SCORE'):
                valor = self.consumir()
                acciones.append({'accion': verbo, 'objeto': valor, 'params': []})
                continue

            objeto = self.consumir()
            params = []
            if self.posicion < len(self.tokens) and self.tokens[self.posicion] == 'AT':
                self.consumir('AT')
                if self.tokens[self.posicion] == 'RANDOM':
                    params.append(self.consumir())
                else:
                    self.consumir('(')
                    x = int(self.consumir())
                    self.consumir(',')
                    y = int(self.consumir())
                    self.consumir(')')
                    params.append([x, y])
            elif (self.posicion < len(self.tokens) and
                  self.tokens[self.posicion] not in [
                      'END', 'ON', 'DEFINE', 'SPAWN', 'MOVE', 'ROTATE',
                      'INCREASE_SCORE', 'SET_DIRECTION', 'GROW', 'GAME_OVER'
                  ]):
                params.append(self.consumir())
            acciones.append({'accion': verbo, 'objeto': objeto, 'params': params})
        self.consumir('END')
        self.ast['events'][nombre_evento] = acciones


def generar_codigo(ast, archivo_salida):
    with open(archivo_salida, 'w') as f:
        json.dump(ast, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Uso: python compiler.py <archivo_entrada.brick>"
        sys.exit(1)
    archivo_entrada = sys.argv[1]
    archivo_salida  = archivo_entrada.replace('.brick', '.json')
    print "Compilando " + archivo_entrada + "..."
    try:
        with open(archivo_entrada, 'r') as f:
            codigo = f.read()
        tokens = lexer(codigo)
        parser = Parser(tokens)
         # RETROCOMPAT (Punto C - Visual): detectar si el .brick es un remake
        # o un evolved por el nombre del archivo. Si contiene 'remake' o 'evolved',
        # el JSON generado llevara "version": "remake" y el runtime activara
        # el estilo mejorado. Cualquier archivo sin estas palabras mantiene
        # "version": "original" (valor por defecto ya puesto en Parser.__init__)
        # y ejecuta la GUI clasica.
        if 'remake' in archivo_entrada or 'evolved' in archivo_entrada:
            parser.ast['version'] = 'remake'
        ast    = parser.parse()
        generar_codigo(ast, archivo_salida)
        print "Compilacion exitosa! Archivo de juego creado en " + archivo_salida
    except Exception as e:
        print "\n!!! ERROR DE COMPILACION !!!"
        print str(e)
        sys.exit(1)
