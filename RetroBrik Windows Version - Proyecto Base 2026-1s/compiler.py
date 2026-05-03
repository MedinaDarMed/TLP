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
            "tipo_juego":    None,
            "config":        {},
            "shapes":        {},
            "shape_colors":  {},
            "shape_chances": {},
            "events":        {}
        }

    def parse(self):
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual == 'GAME_TYPE':
                self.parsear_tipo_juego()
            elif token_actual == 'GAME_GRID':
                self.parsear_grid()
            elif token_actual == 'DEFINE':
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
        color  = '#00FFFF'  # valor por defecto (retrocompatible)
        chance = 1          # valor por defecto (retrocompatible)

        while (self.posicion < len(self.tokens) and
               self.tokens[self.posicion] in ('COLOR', 'CHANCE')):
            atributo = self.consumir()
            self.consumir(':')

            if atributo == 'COLOR':
                # El token es '#RRGGBB' capturado por el lexer como un unico token
                color = self.consumir()

            elif atributo == 'CHANCE':
                # El token es un numero entero que representa el peso relativo
                chance = int(self.consumir())

        self.consumir('END')

        # Guardar estados en el formato original (lista de matrices)
        self.ast['shapes'][nombre_shape] = estados

        # Guardar atributos de personalizacion en campos separados del AST
        self.ast['shape_colors'][nombre_shape]  = color
        self.ast['shape_chances'][nombre_shape] = chance

    # FUNCION CORREGIDA
    def parsear_evento(self):
        self.consumir('ON')
        nombre_evento = 'ON_' + self.consumir()
        self.consumir(':')
        acciones = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] != 'END':
            verbo = self.consumir()

            if verbo == 'GAME_OVER':
                acciones.append({'accion': verbo, 'objeto': None, 'params': []})
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
        ast    = parser.parse()
        generar_codigo(ast, archivo_salida)
        print "Compilacion exitosa! Archivo de juego creado en " + archivo_salida
    except Exception as e:
        print "\n!!! ERROR DE COMPILACION !!!"
        print str(e)
        sys.exit(1)