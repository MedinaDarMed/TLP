# -*- coding: utf-8 -*-
# Cambios (Actividad 3 - Punto B):
# 1. Clase Juego.__init__() - seccion TETRIS:
#    - Se inicializa self.pieza_color = '#00FFFF' como color por defecto.
#    - Esto evita un AttributeError si dibujar() se llama antes de que
#      tetris_spawn_pieza() asigne el color de la primera pieza.
# 2. Metodo tetris_spawn_pieza():
#    - ANTES: elegía la pieza con random.choice() (probabilidad uniforme).
#    - AHORA: usa seleccion ponderada basada en los pesos del campo
#      'shape_chances' del JSON. Si el JSON no tiene ese campo (archivo
#      antiguo), todos los pesos valen 1 y el comportamiento es identico
#      al original.
#    - AHORA: lee el color de la pieza desde 'shape_colors'. Si el campo
#      no existe (JSON antiguo), usa '#00FFFF' como fallback.
# 3. Metodo dibujar() - bloque TETRIS:
#    - ANTES: COLOR_PIEZA = '#00FFFF' (hardcoded).
#    - AHORA: COLOR_PIEZA = self.pieza_color (leido dinamicamente).
#    - RETROCOMPATIBILIDAD: como pieza_color siempre tiene un valor
#      (inicializado en __init__ y actualizado en spawn), el dibujo
#      funciona tanto con JSON nuevos como antiguos.

import sys
import json
import time
import random
import Tkinter as tk
import tkMessageBox


class Juego:
    def __init__(self, datos_juego):
        self.datos_juego = datos_juego
        self.tipo_juego = self.datos_juego.get('tipo_juego', 'TETRIS')
        config = self.datos_juego.get('config', {})
        self.ancho = config.get('grid_size', [10, 20])[0]
        self.alto  = config.get('grid_size', [10, 20])[1]
        self.grid  = [[0 for _ in range(self.ancho)] for _ in range(self.alto)]
        self.puntuacion  = 0
        self.juego_terminado = False

        # Configuracion de la GUI
        self.root = tk.Tk()
        self.root.title("BrickScript - " + self.tipo_juego)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.taman_celda  = 25
        self.ancho_canvas = self.ancho * self.taman_celda
        self.alto_canvas  = self.alto  * self.taman_celda

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

        self.root.bind('<Key>', self.manejar_input_gui)

        if self.tipo_juego == 'TETRIS':
            self.pieza_actual   = None
            self.pieza_x        = 0
            self.pieza_y        = 0
            self.pieza_rotacion = 0
            self.velocidad_gravedad = 0.4
            # CAMBIO 1: Color inicial de la pieza (se sobreescribe en cada spawn).
            # Es necesario inicializarlo aqui para que dibujar() no falle si se
            # llama antes de que ocurra el primer spawn.
            self.pieza_color = '#00FFFF'

        if self.tipo_juego == 'SNAKE':
            self.serpiente_cuerpo     = []
            self.serpiente_direccion  = (1, 0)
            self.posicion_comida      = None
            self.velocidad_gravedad   = 0.15

        self.timer_gravedad = 0
        self.ejecutar_evento('ON_START')
        self.timer_id = None

    def run(self):
        self.root.after(50, self.game_loop)
        self.root.mainloop()

    def game_loop(self):
        if self.juego_terminado:
            self.mostrar_game_over()
            return

        self.timer_gravedad += 0.05
        if self.timer_gravedad >= self.velocidad_gravedad:
            self.timer_gravedad = 0
            self.ejecutar_evento('ON_TICK')

        self.dibujar()
        self.timer_id = self.root.after(50, self.game_loop)

    def cerrar_ventana(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        sys.exit(0)

    def manejar_input_gui(self, event):
        key = event.keysym.upper()
        if self.tipo_juego == 'TETRIS':
            if key == 'UP':    self.ejecutar_evento('ON_KEY_UP')
            elif key == 'DOWN':  self.ejecutar_evento('ON_KEY_DOWN')
            elif key == 'LEFT':  self.ejecutar_evento('ON_KEY_LEFT')
            elif key == 'RIGHT': self.ejecutar_evento('ON_KEY_RIGHT')
        elif self.tipo_juego == 'SNAKE':
            if key == 'UP':    self.snake_cambiar_direccion('UP')
            elif key == 'DOWN':  self.snake_cambiar_direccion('DOWN')
            elif key == 'LEFT':  self.snake_cambiar_direccion('LEFT')
            elif key == 'RIGHT': self.snake_cambiar_direccion('RIGHT')

    def dibujar(self):
        self.canvas.delete("all")
        self.label_score.config(text="PUNTUACION\n" + str(self.puntuacion))

        COLOR_GRID_FIJA    = '#343434'
        COLOR_SNAKE_CABEZA = '#00FF00'
        COLOR_SNAKE_CUERPO = '#33CC33'
        COLOR_FOOD         = '#FF0000'

        # 1. Cuadricula estatica
        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    self.dibujar_celda(x, y, COLOR_GRID_FIJA)

        # 2. Pieza activa de Tetris
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            # CAMBIO 2: Usar self.pieza_color en lugar del valor quemado '#00FFFF'.
            # pieza_color es asignado en tetris_spawn_pieza() con el color leido
            # del JSON. Si el JSON es antiguo y no tiene 'shape_colors', el valor
            # por defecto '#00FFFF' inicializado en __init__ garantiza que el
            # dibujo siga funcionando exactamente igual que antes.
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

        # 3. Snake y Comida
        if self.tipo_juego == 'SNAKE':
            if self.posicion_comida:
                x, y = self.posicion_comida
                self.dibujar_celda(x, y, COLOR_FOOD)
            for i, segmento in enumerate(self.serpiente_cuerpo):
                x, y = segmento
                color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO
                self.dibujar_celda(x, y, color)

    def dibujar_celda(self, x, y, color):
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#000000')

    def ejecutar_evento(self, nombre_evento):
        if nombre_evento in self.datos_juego['events']:
            for accion in self.datos_juego['events'][nombre_evento]:
                verbo, objeto = accion.get('accion'), accion.get('objeto')

                if verbo == 'INCREASE_SCORE': self.puntuacion += int(objeto)
                if verbo == 'GAME_OVER': self.juego_terminado = True

                if self.tipo_juego == 'TETRIS':
                    if verbo == 'SPAWN': self.tetris_spawn_pieza()
                    if verbo == 'MOVE':  self.tetris_mover_pieza(accion['params'][0])
                    if verbo == 'ROTATE': self.tetris_rotar_pieza()

                if self.tipo_juego == 'SNAKE':
                    if verbo == 'SPAWN' and objeto == 'PLAYER': self.snake_spawn_jugador(accion)
                    if verbo == 'SPAWN' and objeto == 'FOOD':   self.snake_spawn_comida()
                    if verbo == 'MOVE'  and objeto == 'PLAYER': self.snake_mover_jugador()
                    if verbo == 'GROW': self.snake_crecer()

    # METODOS DE LOGICA DE JUEGO - TETRIS

    def tetris_spawn_pieza(self):
        # CAMBIO 3: Seleccion ponderada de pieza basada en CHANCE.
        # Algoritmo (Python 2.7, sin librerias externas):
        #   1. Obtener la lista de nombres de piezas y sus pesos.
        #   2. Si el JSON no tiene 'shape_chances' (archivo antiguo), usar peso 1
        #      para todas -> probabilidad uniforme, identica al random.choice original.
        #   3. Generar un numero aleatorio en [0, suma_total_de_pesos).
        #   4. Recorrer las piezas acumulando pesos hasta superar el numero aleatorio.
        #      La pieza que lo supera es la seleccionada.
        nombres = list(self.datos_juego['shapes'].keys())
        chances = self.datos_juego.get('shape_chances', {})

        # Peso de cada pieza; si no tiene CHANCE definido, usa 1 (equitativo)
        pesos = [chances.get(n, 1) for n in nombres]
        total = sum(pesos)

        # Numero aleatorio en el intervalo [0, total)
        r = random.random() * total

        # Recorrer acumulando hasta encontrar la pieza ganadora
        acumulado    = 0
        nombre_pieza = nombres[-1]  # fallback por si acaso (raro con floats)
        for nombre, peso in zip(nombres, pesos):
            acumulado += peso
            if r < acumulado:
                nombre_pieza = nombre
                break

        self.pieza_actual = self.datos_juego['shapes'][nombre_pieza]

        # CAMBIO 4: Leer el color de la pieza seleccionada.
        # - Si el JSON tiene 'shape_colors', usa el color definido en el .brick.
        # - Si no (JSON antiguo), usa '#00FFFF' (cyan), identico al valor original.
        colores = self.datos_juego.get('shape_colors', {})
        self.pieza_color = colores.get(nombre_pieza, '#00FFFF')

        self.pieza_x        = self.ancho / 2 - 2
        self.pieza_y        = 0
        self.pieza_rotacion = 0

        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True

    def tetris_mover_pieza(self, direccion):
        if not self.pieza_actual: return
        dx, dy = 0, 0
        if direccion == 'LEFT':  dx = -1
        elif direccion == 'RIGHT': dx = 1
        elif direccion == 'DOWN':  dy = 1
        if not self.tetris_verificar_colision(
            self.pieza_x + dx, self.pieza_y + dy, self.pieza_rotacion
        ):
            self.pieza_x += dx
            self.pieza_y += dy
        elif dy > 0:
            self.tetris_fijar_pieza()

    def tetris_rotar_pieza(self):
        if not self.pieza_actual: return
        nueva_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual)
        if not self.tetris_verificar_colision(self.pieza_x, self.pieza_y, nueva_rotacion):
            self.pieza_rotacion = nueva_rotacion

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

    def tetris_verificar_colision(self, x, y, rotacion):
        if not self.pieza_actual: return False
        matriz_pieza = self.pieza_actual[rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    nuevo_x = x + x_offset
                    nuevo_y = y + y_offset
                    if not (0 <= nuevo_x < self.ancho and
                            0 <= nuevo_y < self.alto and
                            self.grid[nuevo_y][nuevo_x] == 0):
                        return True
        return False

    def tetris_limpiar_lineas(self):
        nuevo_grid = [fila for fila in self.grid if not all(fila)]
        lineas_limpias = self.alto - len(nuevo_grid)
        if lineas_limpias > 0:
            self.grid = [[0] * self.ancho for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias):
                self.ejecutar_evento('ON_LINE_CLEAR')

    # METODOS DE LOGICA DE JUEGO - SNAKE

    def snake_spawn_jugador(self, accion):
        coords = accion['params'][0] if accion['params'] else [self.ancho / 2, self.alto / 2]
        self.serpiente_cuerpo    = [(coords[0], coords[1])]
        self.serpiente_direccion = (1, 0)

    def snake_spawn_comida(self):
        while True:
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto  - 1)
            if (x, y) not in self.serpiente_cuerpo:
                self.posicion_comida = (x, y)
                break

    def snake_mover_jugador(self):
        if not self.serpiente_cuerpo: return
        cabeza_x, cabeza_y = self.serpiente_cuerpo[0]
        dir_x,    dir_y    = self.serpiente_direccion
        nueva_cabeza = (cabeza_x + dir_x, cabeza_y + dir_y)

        if not (0 <= nueva_cabeza[0] < self.ancho and 0 <= nueva_cabeza[1] < self.alto):
            self.ejecutar_evento('ON_COLLISION_WALL')
            return

        if nueva_cabeza in self.serpiente_cuerpo[:-1]:
            self.ejecutar_evento('ON_COLLISION_SELF')
            return

        self.serpiente_cuerpo.insert(0, nueva_cabeza)

        if nueva_cabeza == self.posicion_comida:
            self.ejecutar_evento('ON_EAT_FOOD')
        else:
            self.serpiente_cuerpo.pop()

    def snake_cambiar_direccion(self, direccion):
        if direccion == 'UP'    and self.serpiente_direccion[1] != 1:  self.serpiente_direccion = (0, -1)
        elif direccion == 'DOWN'  and self.serpiente_direccion[1] != -1: self.serpiente_direccion = (0,  1)
        elif direccion == 'LEFT'  and self.serpiente_direccion[0] != 1:  self.serpiente_direccion = (-1, 0)
        elif direccion == 'RIGHT' and self.serpiente_direccion[0] != -1: self.serpiente_direccion = (1,  0)

    def snake_crecer(self):
        pass

    # SALIDA

    def mostrar_game_over(self):
        tkMessageBox.showinfo("Juego Terminado", "Puntuacion Final: " + str(self.puntuacion))
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Uso: python runtime.py <archivo_juego.json>"
        sys.exit(1)
    archivo_juego = sys.argv[1]
    try:
        with open(archivo_juego, 'r') as f:
            datos_juego = json.load(f)
    except IOError:
        print "Error: No se pudo encontrar el archivo " + archivo_juego
        sys.exit(1)
    juego = Juego(datos_juego)
    juego.run()
    