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
#
# Cambios (Actividad 3 - Punto C - Power-Ups):
# 1. Juego.__init__() - TETRIS:
#    - Se agregan variables de estado para power-ups:
#      lineas_ultimo_clear, powerup_pendiente, es_powerup_activo,
#      nombre_pieza_actual, rotaciones_powerup, modo_bomba_activo,
#      degradado_frame.
# 2. tetris_rotar_pieza():
#    - Incrementa rotaciones_powerup cuando el TRIPLE_CLEAR_PU esta activo.
#    - Activa modo_bomba_activo al llegar a 10 rotaciones.
# 3. tetris_fijar_pieza():
#    - Si modo_bomba_activo es True, elimina las filas ocupadas por el powerup
#      y suma 500 puntos por fila. Resetea todos los contadores de powerup.
# 4. tetris_limpiar_lineas():
#    - Guarda lineas_ultimo_clear para comunicarse con spawn.
#    - Evalua los triggers de powerups del JSON y pone powerup_pendiente.
# 5. tetris_spawn_pieza():
#    - Si hay powerup_pendiente, spawna el powerup en lugar de pieza normal.
#    - Resetea es_powerup_activo y nombre_pieza_actual en spawn normal.
# 6. dibujar():
#    - Si modo_bomba_activo, calcula color HSV ciclico para el degradado
#      animado (sin librerias externas, solo aritmetica basica).
#
# Cambios (Actividad 3 - Punto C - Extension visual y nuevo PowerUp):
# 1. __init__() - TETRIS:
#    - Nuevas variables: lineas_totales_eliminadas (contador acumulado para
#      LINE_PURGE_PU), pieza_siguiente / siguiente_color (preview del panel),
#      flash_powerup_timer (contador para parpadeo al spawnear un PU),
#      borde_arcoiris_frame (animacion de borde cuando modo_bomba_activo).
# 2. __init__() - GUI:
#    - Panel lateral rediseñado: fondo oscuro con degradado simulado, label de
#      nivel, canvas de preview de siguiente pieza, label de controles mejorado.
#    - Marco principal con borde animable (se actualiza en dibujar()).
# 3. tetris_spawn_pieza():
#    - Al generar pieza normal, calcula y guarda la siguiente (para el preview).
#    - LINE_PURGE_PU no spawna pieza visible: aplica efecto directo y retorna.
#    - Al spawnear cualquier PU activa flash_powerup_timer = 8.
# 4. tetris_limpiar_lineas():
#    - Incrementa lineas_totales_eliminadas.
#    - Evalua trigger LINE_CUMULATIVE: si acumulado % valor == 0 activa PU.
# 5. dibujar():
#    - Dibuja borde del canvas animado en arcoiris cuando modo_bomba_activo.
#    - Dibuja flash de pantalla (overlay semitransparente) cuando flash_powerup_timer > 0.
#    - Dibuja letrero "!POWER UP!" animado encima del canvas cuando flash activo.
#    - Llama a dibujar_preview() para actualizar el canvas lateral.
# 6. dibujar_preview() (NUEVO):
#    - Dibuja la siguiente pieza centrada en el canvas de preview del panel.
# 7. dibujar_celda_canvas() (NUEVO):
#    - Version de dibujar_celda() que acepta un canvas arbitrario como parametro,
#      usada por dibujar_preview().
# 8. Estilo general:
#    - Colores de celdas fijas mejorados (gradiente simulado por fila).
#    - Borde biselado en cada celda (highlight claro arriba-izquierda,
#      sombra oscura abajo-derecha).

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
        # RETROCOMPAT (Punto C - Visual): detectar si es el remake o el original.
        # El campo 'version' es 'remake' solo en tetris_remake.json y snake_remake.json.
        # Cualquier JSON sin ese campo (archivos anteriores o de terceros) se trata
        # como 'original' y NO recibe el estilo mejorado.
        self.es_remake = (self.datos_juego.get('version', 'original') == 'remake')
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

        self._nombre_siguiente  = None   # cache interno del nombre de la siguiente pieza

        self.taman_celda  = 25
        self.ancho_canvas = self.ancho * self.taman_celda
        self.alto_canvas  = self.alto  * self.taman_celda

        if self.es_remake:
            # ============================================================
            # GUI MEJORADA — solo para tetris_remake y futuros remakes
            # ============================================================
            self.root.configure(bg='#0A0A0F')
            self.canvas = tk.Canvas(
                self.root,
                width=self.ancho_canvas, height=self.alto_canvas,
                bg='#0D0D1A', highlightthickness=3, highlightbackground='#1A1A3A'
            )
            self.canvas.pack(side=tk.LEFT, padx=12, pady=12)

            PANEL_BG = '#111120'
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

            self.preview_canvas = tk.Canvas(
                self.marco_score, width=5 * 22, height=5 * 22,
                bg='#0A0A18', highlightthickness=1, highlightbackground='#333366'
            )
            self.preview_canvas.pack(pady=(0, 10))

            tk.Label(self.marco_score, text=u'\u2500' * 14,
                     bg=PANEL_BG, fg='#333355', font=('Consolas', 9)).pack()
            self.label_powerup = tk.Label(
                self.marco_score, text='', bg=PANEL_BG, fg='#FF00FF',
                font=('Consolas', 8, 'bold'), wraplength=140, justify=tk.CENTER
            )
            self.label_powerup.pack(pady=(8, 4))
            tk.Label(self.marco_score, text=u'\u2500' * 14,
                     bg=PANEL_BG, fg='#333355', font=('Consolas', 9)).pack(pady=(4, 0))
            tk.Label(self.marco_score,
                     text=u'\u2190\u2192  Mover\n\u2191     Rotar\n\u2193     Bajar',
                     bg=PANEL_BG, fg='#555577',
                     font=('Consolas', 9)).pack(pady=(8, 16))

        else:
            # ============================================================
            # GUI ORIGINAL — para tetris.json, snake.json y cualquier
            # archivo sin campo "version": "remake"
            # ============================================================
            self.canvas = tk.Canvas(
                self.root,
                width=self.ancho_canvas, height=self.alto_canvas,
                bg='#111111'
            )
            self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

            self.marco_score = tk.Frame(
                self.root, width=150, height=self.alto_canvas, bg='#222222'
            )
            self.marco_score.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

            self.label_score = tk.Label(
                self.marco_score,
                text='PUNTUACION\n0',
                bg='#222222', fg='white',
                font=('Consolas', 16, 'bold')
            )
            self.label_score.pack(pady=40, padx=10)

            self.label_controles = tk.Label(
                self.marco_score,
                text='CONTROLES\nFlechas: Mover/Rotar',
                bg='#222222', fg='gray',
                font=('Consolas', 10)
            )
            self.label_controles.pack(pady=20, padx=10)

            # Atributos que el modo remake usa pero el original no tiene:
            # se crean como None para que los metodos no fallen con AttributeError
            # si alguna rama de codigo los referencia por error.
            self.label_lineas   = None
            self.label_powerup  = None
            self.preview_canvas = None

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

            # --- POWER-UPS (Actividad 3 - Punto C) ---
            # Contadores de estado para disparar los power-ups.
            self.lineas_ultimo_clear  = 0   # cuantas lineas se borraron en el ultimo tetris_limpiar_lineas()
            self.powerup_pendiente    = None # nombre del powerup que debe spawnear en el siguiente ON_START
            self.es_powerup_activo    = False # True si la pieza actual es un powerup
            self.nombre_pieza_actual  = ''   # nombre de la pieza/powerup en juego

            # Estado exclusivo del TRIPLE_CLEAR_PU (rectangulo 1x2 con modo bomba)
            self.rotaciones_powerup   = 0    # cuantas veces rotó el powerup mientras cae
            self.modo_bomba_activo    = False # True cuando el 1x2 giró 10+ veces
            self.degradado_frame      = 0    # frame actual de la animacion del degradado

            # CAMBIO (Punto C - Extension Visual):
            # lineas_totales_eliminadas: contador acumulado para el trigger LINE_CUMULATIVE.
            # pieza_siguiente / siguiente_color: datos de la proxima pieza para el preview.
            # flash_powerup_timer: cuantos frames dura el efecto de flash al spawnear un PU.
            # borde_arcoiris_frame: frame de animacion del borde cuando modo_bomba esta activo.
            # lineas_eliminadas_total: contador publico para el label del panel.
            self.lineas_totales_eliminadas = 0
            self.pieza_siguiente    = None
            self.siguiente_color    = '#FFFFFF'
            self.flash_powerup_timer = 0
            self.borde_arcoiris_frame = 0
            self.lineas_eliminadas_total = 0

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

        # CAMBIO (Punto C - Visual): actualizar labels del panel
        if self.es_remake:
            self.label_score.config(text=str(self.puntuacion))
            if self.tipo_juego == 'TETRIS':
                self.label_lineas.config(text=str(self.lineas_eliminadas_total))
        else:
            self.label_score.config(text='PUNTUACION\n' + str(self.puntuacion))

        # --- Colores base ---
        COLOR_SNAKE_CABEZA = '#00FF00'
        COLOR_SNAKE_CUERPO = '#33CC33'
        COLOR_FOOD         = '#FF0000'

        # CAMBIO (Punto C - Visual): borde del canvas animado en arcoiris
        # cuando el modo bomba del TRIPLE_CLEAR_PU esta activo.
        if self.es_remake:
            if self.tipo_juego == 'TETRIS' and self.modo_bomba_activo:
                self.borde_arcoiris_frame = (self.borde_arcoiris_frame + 6) % 360
                r2, g2, b2 = self._hsv_a_rgb(self.borde_arcoiris_frame)
                color_borde = '#{:02X}{:02X}{:02X}'.format(r2, g2, b2)
                self.canvas.config(highlightbackground=color_borde)
            else:
                self.canvas.config(highlightbackground='#1A1A3A')

        # 1. Cuadricula estatica con estilo mejorado
        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    if self.es_remake:
                        intensidad = int(40 + (float(y) / self.alto) * 30)
                        color_fija = '#{:02X}{:02X}{:02X}'.format(
                            intensidad + 10, intensidad, intensidad + 25
                        )
                        self.dibujar_celda_estilo(x, y, color_fija)
                    else:
                        self.dibujar_celda(x, y, '#343434')
                else:
                    if self.es_remake:
                        ts = self.taman_celda
                        x1, y1 = x * ts, y * ts
                        x2, y2 = x1 + ts, y1 + ts
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2, fill='', outline='#151525'
                        )

        # 2. Pieza activa de Tetris
        if self.tipo_juego == 'TETRIS' and self.pieza_actual:
            # CAMBIO (Punto C - Visual): degradado animado en modo bomba
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
                        if self.es_remake:
                            self.dibujar_celda_estilo(
                                self.pieza_x + x_offset,
                                self.pieza_y + y_offset,
                                COLOR_PIEZA
                            )
                        else:
                            self.dibujar_celda(
                                self.pieza_x + x_offset,
                                self.pieza_y + y_offset,
                                COLOR_PIEZA
                            )

        # 3. Snake y Comida
        if self.tipo_juego == 'SNAKE':
            if self.posicion_comida:
                x, y = self.posicion_comida
                if self.es_remake:
                    self.dibujar_celda_estilo(x, y, COLOR_FOOD)
                else:
                    self.dibujar_celda(x, y, COLOR_FOOD)
            for i, segmento in enumerate(self.serpiente_cuerpo):
                x, y = segmento
                color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO
                if self.es_remake:
                    self.dibujar_celda_estilo(x, y, color)
                else:
                    self.dibujar_celda(x, y, color)

        # CAMBIO (Punto C - Visual): flash de pantalla al spawnear un power-up.
        # Se dibuja un rectangulo semitransparente encima de todo el canvas
        # y un letrero "!POWER UP!" parpadeando.
        if self.es_remake and self.tipo_juego == 'TETRIS' and self.flash_powerup_timer > 0:
            self.flash_powerup_timer -= 1
            alpha_idx = self.flash_powerup_timer
            if alpha_idx % 2 == 0:
                self.canvas.create_rectangle(
                    0, 0, self.ancho_canvas, self.alto_canvas,
                    fill='#220033', outline=''
                )
            if alpha_idx > 2:
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

        if self.es_remake and self.tipo_juego == 'TETRIS':
            self.dibujar_preview()

    def dibujar_celda(self, x, y, color):
        # Metodo original mantenido por retrocompatibilidad.
        # El estilo mejorado usa dibujar_celda_estilo().
        ts = self.taman_celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#000000')

    def dibujar_celda_estilo(self, x, y, color, canvas=None, tam=None):
        # CAMBIO (Punto C - Visual): celda con borde biselado.
        # Highlight claro en arista superior-izquierda, sombra en inferior-derecha.
        # El parametro canvas permite reutilizar el metodo en el preview lateral.
        c  = canvas if canvas else self.canvas
        ts = tam    if tam    else self.taman_celda
        x1, y1 = x * ts + 1, y * ts + 1
        x2, y2 = x1 + ts - 2, y1 + ts - 2

        # Color mas claro para el highlight (simular luz arriba-izquierda)
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        hl = '#{:02X}{:02X}{:02X}'.format(
            min(255, r + 60), min(255, g + 60), min(255, b + 60)
        )
        sh = '#{:02X}{:02X}{:02X}'.format(
            max(0, r - 50), max(0, g - 50), max(0, b - 50)
        )

        # Relleno principal
        c.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        # Highlight superior e izquierdo
        c.create_line(x1, y2, x1, y1, fill=hl, width=2)
        c.create_line(x1, y1, x2, y1, fill=hl, width=2)
        # Sombra inferior y derecha
        c.create_line(x2, y1, x2, y2, fill=sh, width=2)
        c.create_line(x1, y2, x2, y2, fill=sh, width=2)

    def dibujar_preview(self):
        # CAMBIO (Punto C - Visual): dibuja la siguiente pieza en el canvas lateral.
        # Solo muestra piezas normales (no powerups) para no revelar el tipo de PU.
        self.preview_canvas.delete("all")
        if not self.pieza_siguiente:
            return
        tam_cel = 22
        # Usar el primer estado de la siguiente pieza
        matriz = self.pieza_siguiente[0]
        alto_m = len(matriz)
        ancho_m = len(matriz[0]) if alto_m > 0 else 0
        # Centrar en el canvas de 5x5 celdas
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
        # CAMBIO (Punto C - Visual): conversion HSV (S=1,V=1) a RGB sin librerias.
        # h: angulo en grados [0, 360). Retorna (r, g, b) enteros en [0, 255].
        sector = int(h / 60) % 6
        f      = (h / 60.0) - int(h / 60)
        if sector == 0:   return 255,        int(255*f),    0
        elif sector == 1: return int(255*(1-f)), 255,        0
        elif sector == 2: return 0,           255,        int(255*f)
        elif sector == 3: return 0,           int(255*(1-f)), 255
        elif sector == 4: return int(255*f),  0,           255
        else:             return 255,         0,           int(255*(1-f))

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
        # CAMBIO (Punto C - Power-Ups): si hay un power-up pendiente, procesarlo.
        if self.powerup_pendiente is not None:
            nombre_pu = self.powerup_pendiente
            self.powerup_pendiente = None

            # LINE_PURGE_PU: efecto silencioso, sin pieza visible.
            # Elimina las 2 ultimas filas del tablero sin otorgar puntaje.
            if nombre_pu == 'LINE_PURGE_PU':
                # Activar flash visual aunque no haya pieza que caiga
                self.flash_powerup_timer = 8
                self.nombre_pieza_actual = 'LINE_PURGE_PU'
                if self.es_remake and self.label_powerup:
                    self.label_powerup.config(text=u'\u26A1 PURGA DE\nLINEAS \u26A1')
                # Eliminar las 2 filas mas bajas que tengan al menos una celda
                filas_con_contenido = [
                    i for i in range(self.alto) if any(self.grid[i])
                ]
                filas_a_borrar = filas_con_contenido[-2:] if len(filas_con_contenido) >= 2 \
                                 else filas_con_contenido
                if filas_a_borrar:
                    self.grid = [
                        fila for i, fila in enumerate(self.grid)
                        if i not in filas_a_borrar
                    ]
                    vacias = [[0] * self.ancho for _ in range(len(filas_a_borrar))]
                    self.grid = vacias + self.grid
                # Continuar con spawn normal (no retornar: el juego debe seguir)
                # Limpiar el label despues de un momento diferido
                self.root.after(1200, lambda: self.label_powerup.config(text=''))
                # No retornar: despues de la purga, spawnear pieza normal
                # (se deja caer al flujo siguiente)

            else:
                # Otros powerups que si spawnean pieza visible
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

                    # Texto descriptivo en el panel segun el tipo de PU
                    if nombre_pu == 'DOUBLE_CLEAR_PU':
                        self.label_powerup.config(text=u'\u2605 DOBLE\nLIMPIEZA \u2605')
                    elif nombre_pu == 'TRIPLE_CLEAR_PU':
                        self.label_powerup.config(text=u'\u26A1 TRIPLE\n¡BOMBA! \u26A1')
                    else:
                        self.label_powerup.config(text=u'\u2605 POWER UP \u2605')
                    self.root.after(1800, lambda: self.label_powerup.config(text=''))

                    self.pieza_x        = self.ancho / 2 - 1
                    self.pieza_y        = 0
                    self.pieza_rotacion = 0
                    if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
                        self.juego_terminado = True
                    return  # salir: ya se spawneo el powerup

        # --- Flujo normal: seleccion ponderada de pieza ---
        # CAMBIO (Punto C - Visual): calcular TAMBIEN la siguiente pieza
        # para mostrarla en el preview. Si ya existia una pieza_siguiente
        # pre-calculada, usarla como pieza actual y calcular la nueva siguiente.
        self.es_powerup_activo   = False
        self.nombre_pieza_actual = ''

        nombres = list(self.datos_juego['shapes'].keys())
        chances = self.datos_juego.get('shape_chances', {})
        pesos   = [chances.get(n, 1) for n in nombres]
        total   = sum(pesos)

        def seleccionar_pieza_aleatoria():
            # Funcion auxiliar de seleccion ponderada (Python 2.7 compatible)
            r2     = random.random() * total
            acum   = 0
            elegida = nombres[-1]
            for nm, ps in zip(nombres, pesos):
                acum += ps
                if r2 < acum:
                    elegida = nm
                    break
            return elegida

        if self.pieza_siguiente is None:
            # Primera vez: generar pieza actual y la siguiente
            nombre_actual   = seleccionar_pieza_aleatoria()
            nombre_siguiente = seleccionar_pieza_aleatoria()
        else:
            # Usar la pieza pre-calculada como actual
            nombre_actual    = self._nombre_siguiente
            nombre_siguiente = seleccionar_pieza_aleatoria()

        self._nombre_siguiente = nombre_siguiente

        colores = self.datos_juego.get('shape_colors', {})

        self.pieza_actual  = self.datos_juego['shapes'][nombre_actual]
        self.pieza_color   = colores.get(nombre_actual, '#00FFFF')

        # Guardar la siguiente para el preview
        self.pieza_siguiente  = self.datos_juego['shapes'][nombre_siguiente]
        self.siguiente_color  = colores.get(nombre_siguiente, '#00FFFF')

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

            # CAMBIO (Actividad 3 - Punto C):
            # Si el powerup TRIPLE_CLEAR_PU esta activo, contar rotaciones.
            # Al llegar a 10, activar el modo bomba (degradado + limpieza de filas).
            if self.es_powerup_activo and self.nombre_pieza_actual == 'TRIPLE_CLEAR_PU':
                self.rotaciones_powerup += 1
                if self.rotaciones_powerup >= 10 and not self.modo_bomba_activo:
                    self.modo_bomba_activo = True

    def tetris_fijar_pieza(self):
        matriz_pieza = self.pieza_actual[self.pieza_rotacion]

        # Recolectar las filas que ocupa la pieza antes de fijarla
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

        # CAMBIO (Actividad 3 - Punto C):
        # Si el TRIPLE_CLEAR_PU se fijo en modo bomba, eliminar todas las filas
        # que toca y sumar puntaje extra (500 por fila eliminada).
        if self.es_powerup_activo and self.modo_bomba_activo:
            filas_a_eliminar = sorted(filas_ocupadas)
            nuevo_grid = [fila for i, fila in enumerate(self.grid)
                          if i not in filas_a_eliminar]
            filas_borradas = len(filas_a_eliminar)
            self.grid = ([[0] * self.ancho for _ in range(filas_borradas)]
                         + nuevo_grid)
            self.puntuacion += 500 * filas_borradas

        # Resetear estado del powerup sin importar cual era
        self.es_powerup_activo   = False
        self.nombre_pieza_actual = ''
        self.rotaciones_powerup  = 0
        self.modo_bomba_activo   = False
        self.degradado_frame     = 0

        # CAMBIO (Punto C - Visual): limpiar borde y label al terminar el powerup
        if self.es_remake:
            self.canvas.config(highlightbackground='#1A1A3A')
        if self.es_remake and self.label_powerup:
            self.label_powerup.config(text='')

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

        # CAMBIO (Punto C - Power-Ups): guardar cuantas lineas se limpiaron
        self.lineas_ultimo_clear = lineas_limpias

        if lineas_limpias > 0:
            self.grid = [[0] * self.ancho for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias):
                self.ejecutar_evento('ON_LINE_CLEAR')

            # CAMBIO (Punto C - Visual): actualizar contador publico de lineas
            self.lineas_eliminadas_total += lineas_limpias

            # CAMBIO (Punto C - Extension): contador acumulado para LINE_PURGE_PU
            self.lineas_totales_eliminadas += lineas_limpias

            # Evaluar triggers de powerups.
            # Prioridad: LINE_CUMULATIVE se evalua primero; si no aplica,
            # se evaluan LINE_CLEAR_EXACT y LINE_CLEAR_MIN.
            # Si varios aplican, gana el ultimo en el dict (orden del .brick).
            powerups = self.datos_juego.get('powerups', {})
            for nombre_pu, datos_pu in powerups.items():
                tipo  = datos_pu.get('trigger_type', '')
                valor = datos_pu.get('trigger_value', 0)
                activar = False

                if tipo == 'LINE_CUMULATIVE' and valor > 0:
                    # Se activa cada vez que el acumulado llega a un multiplo de valor.
                    # Se usa el contador antes de sumar para evitar doble disparo.
                    if self.lineas_totales_eliminadas % valor == 0:
                        activar = True

                elif tipo == 'LINE_CLEAR_EXACT' and lineas_limpias == valor:
                    activar = True

                elif tipo == 'LINE_CLEAR_MIN' and lineas_limpias >= valor:
                    activar = True

                if activar:
                    self.powerup_pendiente = nombre_pu

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
    