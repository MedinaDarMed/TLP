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
import math
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
            # CAMBIO (Interfaz): fondo general más oscuro y acento neón más
            # saturado para darle personalidad retro-arcade al panel.
            # ============================================================
            self.root.configure(bg='#07070E')
            self.canvas = tk.Canvas(
                self.root,
                width=self.ancho_canvas, height=self.alto_canvas,
                # CAMBIO (Interfaz): borde del canvas más brillante para
                # separarlo visualmente del panel lateral.
                bg='#0B0B18', highlightthickness=2, highlightbackground='#2A1A5A'
            )
            self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

            # CAMBIO (Interfaz): panel lateral con fondo ligeramente más oscuro
            # y ancho reducido a 150 px para ahorrar espacio horizontal.
            PANEL_BG = '#0E0E1C'
            ACCENT    = '#9B3FEE'   # violeta neón principal
            SUBTEXT   = '#8888AA'   # etiquetas secundarias
            NEON_GRN  = '#00FFAA'   # valor de líneas / snake

            self.colores_nivel = {
                'BABY':       '#00FF88',   # verde menta — tranquilo
                'EASY':       '#88FF00',   # verde lima
                'ENTUSIASTA': '#FF9900',   # naranja vibrante — nivel intermedio energico
                'MEDIUM':     '#FFCC00',   # amarillo — atencion
                'HARD':       '#FF4400',   # naranja rojo — peligro
                'NYAN_CAT':   '#FF00FF',   # magenta — modo especial
            }

            self.marco_score = tk.Frame(self.root, width=150, bg=PANEL_BG)
            self.marco_score.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=10)
            self.marco_score.pack_propagate(False)

            # — Título del motor —
            tk.Label(self.marco_score, text='RETROBRIK',
                     bg=PANEL_BG, fg=ACCENT,
                     font=('Consolas', 12, 'bold')).pack(pady=(16, 0))
            # CAMBIO (Interfaz): subtítulo con el tipo de juego para que el
            # panel sea informativo desde el primer vistazo.
            tk.Label(self.marco_score, text=self.tipo_juego,
                     bg=PANEL_BG, fg='#44446A',
                     font=('Consolas', 8)).pack(pady=(0, 6))
            tk.Label(self.marco_score, text=u'\u2550' * 13,
                     bg=PANEL_BG, fg='#2A1A5A', font=('Consolas', 8)).pack()
            
            # — Puntuación —
            tk.Label(self.marco_score, text='PUNTUACION',
                     bg=PANEL_BG, fg=SUBTEXT,
                     font=('Consolas', 8, 'bold')).pack(pady=(12, 0))
            self.label_score = tk.Label(self.marco_score, text='0',
                                        bg=PANEL_BG, fg='#FFFFFF',
                                        font=('Consolas', 24, 'bold'))
            self.label_score.pack(pady=(2, 6))

            # — Líneas / segmentos —
            # CAMBIO (Interfaz): la etiqueta cambia según el tipo de juego;
            # en SNAKE es más natural hablar de "SEGMENTOS" que de "LINEAS".
            lineas_label = 'SEGMENTOS' if self.tipo_juego == 'SNAKE' else 'LINEAS'
            tk.Label(self.marco_score, text=lineas_label,
                     bg=PANEL_BG, fg=SUBTEXT,
                     font=('Consolas', 8, 'bold')).pack(pady=(4, 0))
            self.label_lineas = tk.Label(self.marco_score, text='0',
                                         bg=PANEL_BG, fg=NEON_GRN,
                                         font=('Consolas', 18, 'bold'))
            self.label_lineas.pack(pady=(2, 6))

            tk.Label(self.marco_score, text=u'\u2550' * 13,
                     bg=PANEL_BG, fg='#2A1A5A', font=('Consolas', 8)).pack()
            
            # --- Badge de nivel actual --- solo para SNAKE
            if self.tipo_juego == 'SNAKE':
                tk.Label(self.marco_score, text='NIVEL',
                        bg=PANEL_BG, fg=SUBTEXT,
                        font=('Consolas', 8, 'bold')).pack(pady=(10, 0))

                self.label_nivel_actual = tk.Label(
                    self.marco_score, text='BABY',
                    bg=PANEL_BG, fg='#00FF88',
                    font=('Consolas', 14, 'bold')
                )
                self.label_nivel_actual.pack(pady=(2, 6))
            else:
                self.label_nivel_actual = None

           # --- Barra de escudo (Power-Up "No Morir") --- solo para SNAKE
            if self.tipo_juego == 'SNAKE':
                tk.Label(self.marco_score, text='ESCUDO',
                        bg=PANEL_BG, fg=SUBTEXT,
                        font=('Consolas', 8, 'bold')).pack(pady=(4, 0))

                self.shield_bar_canvas = tk.Canvas(
                    self.marco_score, width=120, height=12,
                    bg='#0E0E1C', highlightthickness=1, highlightbackground='#2A1A5A'
                )
                self.shield_bar_canvas.pack(pady=(2, 8))
            else:
                self.shield_bar_canvas = None

            # — Preview "SIGUIENTE" — solo relevante para juegos con piezas
            # CAMBIO: se oculta completamente en SNAKE porque la serpiente
            # no tiene pieza siguiente; así se elimina el hueco vacío.
            if self.tipo_juego != 'SNAKE':
                tk.Label(self.marco_score, text='SIGUIENTE',
                         bg=PANEL_BG, fg=SUBTEXT,
                         font=('Consolas', 8, 'bold')).pack(pady=(10, 4))
                self.preview_canvas = tk.Canvas(
                    self.marco_score, width=5 * 22, height=5 * 22,
                    bg='#080816', highlightthickness=1, highlightbackground='#2A1A5A'
                )
                self.preview_canvas.pack(pady=(0, 8))
                tk.Label(self.marco_score, text=u'\u2550' * 13,
                         bg=PANEL_BG, fg='#2A1A5A', font=('Consolas', 8)).pack()
            else:
                # CAMBIO: en SNAKE no existe pieza siguiente, se asigna None
                # para que los métodos que lo usan fallen silenciosamente
                # igual que antes, sin romper ninguna lógica existente.
                self.preview_canvas = None

            # — Power-up activo —
            self.label_powerup = tk.Label(
                self.marco_score, text='', bg=PANEL_BG, fg='#FF44FF',
                font=('Consolas', 8, 'bold'), wraplength=138, justify=tk.CENTER
            )
            self.label_powerup.pack(pady=(8, 4))

            tk.Label(self.marco_score, text=u'\u2550' * 13,
                     bg=PANEL_BG, fg='#2A1A5A', font=('Consolas', 8)).pack(pady=(4, 0))

            # CAMBIO (Interfaz): texto de controles adaptado al tipo de juego;
            # SNAKE usa flechas para moverse, no para rotar ni bajar.
            if self.tipo_juego == 'SNAKE':
                controles_txt = u'\u2190\u2191\u2192\u2193  Mover'
            else:
                controles_txt = u'\u2190\u2192  Mover\n\u2191     Rotar\n\u2193     Bajar'
            tk.Label(self.marco_score, text=controles_txt,
                     bg=PANEL_BG, fg='#3A3A5A',
                     font=('Consolas', 9)).pack(pady=(10, 16))

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
            self.label_nivel_actual = None
            self.shield_bar_canvas  = None

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
            self.serpiente_cuerpo    = []
            self.serpiente_direccion = (1, 0)
            self.posicion_comida     = None

            # --- SNAKE EVOLVED: Estado de nuevas entidades ---
            self.posicion_veneno     = None
            self.posiciones_nubes    = []
            self.escudo_activo       = False
            self.escudo_restante     = 0     # Ticks restantes de invulnerabilidad
            self.posicion_escudo     = None
            self.escudo_halo_frame   = 0     # Para la animacion del halo

            self.snake_shape = self.datos_juego.get('shape_types', {}).get('PIXEL', 'RECTANGULAR')
            # ACTIVIDAD 4 - Logica de niveles progresivos:
            # El .brick define el nivel MAXIMO alcanzable.
            # El juego siempre comienza en BABY y sube segun puntuacion acumulada.
            # RETROCOMPAT: si el JSON no tiene campo 'level', el nivel maximo es BABY
            # y el juego se queda en ese nivel sin progresar (comportamiento original).
            self.nivel_maximo  = self.datos_juego.get('level', 'BABY')
            # secuencia_niveles se reconstruye dinamicamente desde levels_config
            # (ordenando por MIN_SCORE). Este fallback cubre archivos sin DEFINE LEVELS.
            # Se incluye ENTUSIASTA para que la progresion funcione sin config.
            self.secuencia_niveles = ['BABY', 'EASY', 'ENTUSIASTA', 'MEDIUM', 'HARD', 'NYAN_CAT']
            # Umbrales de puntuacion para subir de nivel (puntos acumulados).
            # Fallback si el .brick no tiene DEFINE LEVELS (retrocompat).
            self.umbrales_nivel = {
                'BABY':       0,
                'EASY':       20,
                'ENTUSIASTA': 30,
                'MEDIUM':     50,
                'HARD':       80,
                'NYAN_CAT':   120,
            }
            # Velocidades de tick por nivel (segundos por iteracion).
            # NYAN_CAT baja a 0.03 para velocidad significativamente mas alta.
            self.velocidades_nivel = {
                'BABY':       0.15,
                'EASY':       0.10,
                'ENTUSIASTA': 0.08, 
                'MEDIUM':     0.08,
                'HARD':       0.06,
                'NYAN_CAT':   0.03,
            }
            # Nivel actual siempre empieza en BABY
            self.level = 'BABY'
            self.velocidad_gravedad = self.velocidades_nivel['BABY']
            self.nyan_colors = [
                '#FF0000',
                '#FF7F00',
                '#FFFF00',
                '#00FF00',
                '#0000FF',
                '#4B0082',
                '#9400D3'
            ]
            # Mostrar el nivel activo en el titulo de la ventana
            self.root.title('BrickScript - SNAKE  |  Nivel: BABY')

            # --- Punto C: leer configuración de niveles desde JSON ---
            self.levels_config = self.datos_juego.get('levels', {})

            # Reconstruir umbrales y velocidades desde levels_config si existen,
            # o mantener los valores hardcodeados como fallback (retrocompat).
            if self.levels_config:
                for nombre_nv, cfg in self.levels_config.items():
                    self.umbrales_nivel[nombre_nv]   = cfg.get('min_score', self.umbrales_nivel.get(nombre_nv, 0))
                    self.velocidades_nivel[nombre_nv] = cfg.get('speed', 15) / 100.0
                # Construir secuencia_niveles dinamicamente ordenando por MIN_SCORE.
                self.secuencia_niveles = sorted(
                    self.levels_config.keys(),
                    key=lambda n: self.levels_config[n].get('min_score', 0)
                )

            # --- Power-Up "No Morir": wrap-around al chocar con pared con escudo ---

            # --- Animaciones visuales: contadores de frame ---
            self.food_pulse_frame    = 0   # Para pulso de la comida
            self.poison_flash_frame  = 0   # Para parpadeo del veneno
            self.shield_spin_frame   = 0   # Para rotacion del escudo
            self.shield_flash_timer  = 0   # Flash verde al recoger escudo
            self.nivel_flash_timer   = 0   # Frames restantes del flash de subida de nivel
            self.nivel_anterior      = 'BABY'  # Para detectar cuando cambia el nivel
            # Timer para el mensaje de colision sin muerte en NYAN_CAT.
            # Se activa cuando la serpiente choca (pared/cuerpo) y pierde
            # todos los puntos pero sigue viva.
            self.nyan_hit_flash_timer = 0

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
            
            if self.tipo_juego == 'SNAKE':
                # --- SNAKE EVOLVED: Gestion del escudo ---
                if self.escudo_activo:
                    self.escudo_restante -= 1
                    if self.escudo_restante <= 0:
                        self.escudo_activo = False
            
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
                self.canvas.config(highlightbackground=color_borde,
                                   highlightthickness=3)
            elif hasattr(self, 'escudo_activo') and self.escudo_activo:
                pulso_borde = abs(math.sin(self.escudo_halo_frame * 0.12))
                verde_int = int(150 + pulso_borde * 105)
                color_escudo_borde = '#{:02X}{:02X}{:02X}'.format(
                    0, verde_int, int(verde_int * 0.65))
                self.canvas.config(highlightbackground=color_escudo_borde,
                                   highlightthickness=3)
            else:
                self.canvas.config(highlightbackground='#1A1A3A',
                                   highlightthickness=2)

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
            # Contadores de animación (se incrementan cada frame)
            self.food_pulse_frame   = (self.food_pulse_frame   + 1) % 360
            self.poison_flash_frame = (self.poison_flash_frame + 1) % 60
            self.shield_spin_frame  = (self.shield_spin_frame  + 1) % 360

            # Dibujar comida
            if self.posicion_comida:
                x, y = self.posicion_comida
                ts = self.taman_celda
                px, py = x * ts, y * ts

                if self.es_remake:
                    # Pulso: el radio oscila ±3px con una onda seno
                    pulso = math.sin(self.food_pulse_frame * 0.18)
                    radio_extra = int(pulso * 3)
                    margen = 3 - radio_extra
                    # Sombra/halo exterior
                    self.canvas.create_oval(
                        px + margen - 2, py + margen - 2,
                        px + ts - margen + 2, py + ts - margen + 2,
                        fill='#880000', outline=''
                    )
                    # Círculo principal
                    self.canvas.create_oval(
                        px + margen, py + margen,
                        px + ts - margen, py + ts - margen,
                        fill='#FF2222', outline='#FF8888', width=1
                    )
                    # Brillo superior izquierdo
                    self.canvas.create_oval(
                        px + margen + 2, py + margen + 2,
                        px + margen + 7, py + margen + 7,
                        fill='#FF9999', outline=''
                    )
                else:
                    self.dibujar_celda(x, y, COLOR_FOOD)

            # --- SNAKE EVOLVED: Dibujar fruta venenosa (magenta + X) ---
            if self.posicion_veneno:
                vx, vy = self.posicion_veneno
                ts = self.taman_celda
                px, py = vx * ts, vy * ts

                if self.es_remake:
                    # Parpadeo: alterna entre dos tonos de magenta cada 15 frames
                    cv = '#FF00FF' if (self.poison_flash_frame // 15) % 2 == 0 else '#CC00CC'
                    # Halo exterior amenazante
                    self.canvas.create_oval(
                        px + 1, py + 1, px + ts - 1, py + ts - 1,
                        fill=cv, outline='#880088', width=2
                    )
                    # X en blanco (más gruesa y visible)
                    self.canvas.create_line(px+5, py+5, px+ts-5, py+ts-5,
                                            fill='white', width=3)
                    self.canvas.create_line(px+ts-5, py+5, px+5, py+ts-5,
                                            fill='white', width=3)
                    # Calavera simplificada: dos puntos (ojos)
                    self.canvas.create_oval(px+6, py+6, px+10, py+10, fill='black', outline='')
                    self.canvas.create_oval(px+ts-10, py+6, px+ts-6, py+10, fill='black', outline='')
                else:
                    self.dibujar_celda(vx, vy, '#FF00FF')
                    self.canvas.create_line(px+4, py+4, px+ts-4, py+ts-4, fill='black', width=2)
                    self.canvas.create_line(px+ts-4, py+4, px+4, py+ts-4, fill='black', width=2)

            # --- SNAKE EVOLVED: Dibujar nubes (gris + ~) ---
            for nx, ny in self.posiciones_nubes:
                ts = self.taman_celda
                px, py = nx * ts, ny * ts
                cx, cy = px + ts / 2, py + ts / 2

                if self.es_remake:
                    # Nube "esponjosa": tres óvalos superpuestos
                    self.canvas.create_oval(px+2,       cy-4,   px+ts-2, cy+ts//2-2,
                                            fill='#777777', outline='')           # base
                    self.canvas.create_oval(px+3,       py+3,   cx+2,    cy+4,
                                            fill='#999999', outline='')           # izq arriba
                    self.canvas.create_oval(cx-2,       py+2,   px+ts-3, cy+5,
                                            fill='#AAAAAA', outline='')           # der arriba
                    # Borde unificador
                    self.canvas.create_oval(px+1, py+1, px+ts-1, py+ts-1,
                                            fill='', outline='#555555', width=1)
                else:
                    self.canvas.create_oval(px+2, py+2, px+ts-2, py+ts-2,
                                            fill='#888888', outline='#555555', width=2)
                    self.canvas.create_text(px+ts/2, py+ts/2, text='~',
                                            fill='#333333', font=('Consolas', 10, 'bold'))

            # --- SNAKE EVOLVED: Dibujar escudo animado ---
            if self.posicion_escudo:
                sx, sy = self.posicion_escudo
                ts = self.taman_celda
                px, py = sx * ts, sy * ts
                cx, cy = px + ts / 2, py + ts / 2

                # Anillo externo giratorio (rota con shield_spin_frame)
                import math as _math
                ang = self.shield_spin_frame * _math.pi / 180
                for i in range(4):
                    a = ang + i * (_math.pi / 2)
                    rx2 = cx + _math.cos(a) * (ts * 0.48)
                    ry2 = cy + _math.sin(a) * (ts * 0.48)
                    self.canvas.create_oval(
                        rx2 - 2, ry2 - 2, rx2 + 2, ry2 + 2,
                        fill='#00FFCC', outline=''
                    )

                # Halo exterior pulsante
                pulso_item = abs(_math.sin(self.shield_spin_frame * 0.06))
                radio_halo = int(ts * 0.52 + pulso_item * ts * 0.1)
                alpha_halo = int(60 + pulso_item * 80)
                color_halo_item = '#{:02X}{:02X}{:02X}'.format(0, alpha_halo, int(alpha_halo * 0.85))
                self.canvas.create_oval(
                    cx - radio_halo, cy - radio_halo,
                    cx + radio_halo, cy + radio_halo,
                    fill='', outline=color_halo_item, width=2
                )

                # Cuerpo del escudo (fondo oscuro + borde brillante)
                self.canvas.create_oval(
                    px + 4, py + 4, px + ts - 4, py + ts - 4,
                    fill='#003322', outline='#00FFAA', width=2
                )
                # Símbolo ⛨ más grande y visible
                self.canvas.create_text(
                    cx, cy, text=u'\u26E8',
                    fill='#00FFAA', font=('Consolas', 12, 'bold')
                )

            # --- Notificación visual de subida de nivel ---
            if self.es_remake and self.nivel_flash_timer > 0:
                self.nivel_flash_timer -= 1
                # Solo mostrar durante los primeros 30 frames
                if self.nivel_flash_timer > 5:
                    color_nv = self.colores_nivel.get(self.level, '#FFFFFF')
                    alpha_t  = float(self.nivel_flash_timer) / 30.0

                    # Fondo semitransparente (simulado con un rectángulo oscuro)
                    self.canvas.create_rectangle(
                        0, self.alto_canvas // 2 - 22,
                        self.ancho_canvas, self.alto_canvas // 2 + 22,
                        fill='#050515', outline=''
                    )
                    # Texto del nuevo nivel
                    self.canvas.create_text(
                        self.ancho_canvas // 2, self.alto_canvas // 2 - 8,
                        text=u'\u2b06 NIVEL NUEVO \u2b06',
                        fill='#888888', font=('Consolas', 9)
                    )
                    self.canvas.create_text(
                        self.ancho_canvas // 2, self.alto_canvas // 2 + 8,
                        text=self.level,
                        fill=color_nv, font=('Consolas', 16, 'bold')
                    )
                # Actualizar badge de nivel en panel
                self.actualizar_marcador()

            # Dibujar serpiente
            # ACTIVIDAD 4 - Logica de niveles y formas:
            # El nivel define el comportamiento visual de la serpiente.
            # BABY/EASY/MEDIUM/HARD: forma geometrica segun SHAPE_TYPE del .brick
            # NYAN_CAT: cola multicolor + cabeza especial con cara de gato
            for i, segmento in enumerate(self.serpiente_cuerpo):
                x, y = segmento
                px = x * self.taman_celda
                py = y * self.taman_celda
                px2 = px + self.taman_celda
                py2 = py + self.taman_celda

                # Color base segun nivel
                if self.level == 'NYAN_CAT':
                    # Cola arcoiris: cada segmento usa un color diferente
                    color = self.nyan_colors[i % len(self.nyan_colors)]
                elif self.level == 'HARD':
                    # Nivel HARD: serpiente en rojo intenso como advertencia
                    intensidad = max(80, 255 - i * 8)
                    color = '#{:02X}{:02X}{:02X}'.format(intensidad, 0, 0)
                elif self.level == 'MEDIUM':
                    # Nivel MEDIUM: degradado naranja -> amarillo
                    intensidad = max(60, 220 - i * 6)
                    color = '#{:02X}{:02X}{:02X}'.format(intensidad, intensidad // 2, 0)
                elif self.level == 'EASY':
                    # Nivel EASY: verde clasico con degradado suave
                    intensidad = max(80, 200 - i * 5)
                    color = '#{:02X}{:02X}{:02X}'.format(0, intensidad, 0)
                elif self.level == 'ENTUSIASTA':
                    # Nivel Entusiasta: Naranja dorado con degradado — nivel intermedio energico
                    r = max(150, 255 - i * 5)
                    g = max(60,  160 - i * 8)
                    color = '#{:02X}{:02X}{:02X}'.format(r, g, 0)
                else:
                    # BABY (default): verde clasico sin degradado
                    color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO

                # Nivel NYAN_CAT: cabeza especial con cara de gato
                if i == 0 and self.level == 'NYAN_CAT':
                    # Cara (circulo blanco base)
                    self.canvas.create_oval(
                        px+2, py+2, px2-2, py2-2,
                        fill='white', outline='black'
                    )
                    # Oreja izquierda
                    self.canvas.create_polygon(
                        px+5, py+8, px+10, py-2, px+15, py+8,
                        fill='white', outline='black'
                    )
                    # Oreja derecha
                    self.canvas.create_polygon(
                        px2-15, py+8, px2-10, py-2, px2-5, py+8,
                        fill='white', outline='black'
                    )
                    # Ojo izquierdo
                    self.canvas.create_oval(
                        px+7, py+10, px+10, py+13, fill='black'
                    )
                    # Ojo derecho
                    self.canvas.create_oval(
                        px2-10, py+10, px2-7, py+13, fill='black'
                    )
                    # Nariz
                    self.canvas.create_oval(
                        px+11, py+14, px+14, py+17,
                        fill='pink', outline='pink'
                    )
                    # Boca
                    self.canvas.create_line(px+12, py+17, px+10, py+19)
                    self.canvas.create_line(px+12, py+17, px+14, py+19)
                    # Bigotes izquierdos
                    self.canvas.create_line(px+3, py+15, px+9, py+15)
                    self.canvas.create_line(px+3, py+18, px+9, py+17)
                    # Bigotes derechos
                    self.canvas.create_line(px2-9, py+15, px2-3, py+15)
                    self.canvas.create_line(px2-9, py+17, px2-3, py+18)

                # Resto del cuerpo + todos los segmentos en niveles sin cabeza especial.
                # ACTIVIDAD 4: la forma del segmento depende del nivel actual:
                #   BABY / EASY / MEDIUM  -> CIRCULAR
                #   HARD / NYAN_CAT (cuerpo) -> TRIANGULAR
                # Si el .brick no define shape_type (snake original), se usa RECTANGULAR.
                else:
                    forma_activa = self.snake_shape
                    if forma_activa != 'RECTANGULAR':
                        # Escalar forma segun nivel cuando hay shape_type definido
                        if self.level in ('HARD', 'NYAN_CAT'):
                            forma_activa = 'TRIANGULAR'
                        else:
                            forma_activa = 'CIRCULAR'

                    if forma_activa == 'CIRCULAR':
                        # ACTIVIDAD 4 - Forma CIRCULAR: niveles BABY / EASY / MEDIUM
                        self.canvas.create_oval(
                            px, py, px2, py2,
                            fill=color, outline='black'
                        )
                    elif forma_activa == 'TRIANGULAR':
                        # ACTIVIDAD 4 - Forma TRIANGULAR: niveles HARD / NYAN_CAT
                        self.canvas.create_polygon(
                            px + self.taman_celda / 2, py,
                            px, py2,
                            px2, py2,
                            fill=color, outline='black'
                        )
                    else:
                        # Forma RECTANGULAR: snake original sin SHAPE_TYPE
                        if self.es_remake:
                            self.dibujar_celda_estilo(x, y, color)
                        else:
                            self.dibujar_celda(x, y, color)

            # --- SNAKE EVOLVED: Halo del escudo ---
            if self.escudo_activo and self.serpiente_cuerpo:
                self.escudo_halo_frame += 1
                hx, hy = self.serpiente_cuerpo[0]
                ts = self.taman_celda
                cx, cy = hx * ts + ts/2, hy * ts + ts/2
                pulso = abs(math.sin(self.escudo_halo_frame * 0.15))

                # Anillo exterior (más grande, más tenue)
                radio_ext = int(ts * 0.9 + pulso * ts * 0.35)
                int_ext = int(80 + pulso * 70)
                color_ext = '#{:02X}{:02X}{:02X}'.format(0, int_ext, int(int_ext * 0.7))
                self.canvas.create_oval(
                    cx - radio_ext, cy - radio_ext,
                    cx + radio_ext, cy + radio_ext,
                    outline=color_ext, width=1
                )

                # Anillo interior (más pequeño, más brillante)
                radio_int = int(ts * 0.65 + pulso * ts * 0.2)
                int_int = int(160 + pulso * 95)
                color_int = '#{:02X}{:02X}{:02X}'.format(0, int_int, int(int_int * 0.65))
                self.canvas.create_oval(
                    cx - radio_int, cy - radio_int,
                    cx + radio_int, cy + radio_int,
                    outline=color_int, width=3
                )

                # Ticks de tiempo restante (arco que se va vaciando)
                if self.escudo_restante > 0:
                    duracion_max = 150
                    fraccion = float(self.escudo_restante) / duracion_max
                    for i in range(8):
                        a = math.pi * 2 * i / 8
                        if i / 8 < fraccion:
                            tx = cx + math.cos(a) * (radio_ext + 5)
                            ty = cy + math.sin(a) * (radio_ext + 5)
                            self.canvas.create_oval(tx-2, ty-2, tx+2, ty+2,
                                                    fill='#00FFAA', outline='')

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

        # Mensaje de colision sin muerte: muestra un aviso cuando la serpiente
        # pierde todos sus puntos pero sigue viva en nivel NYAN_CAT.
        if hasattr(self, 'nyan_hit_flash_timer') and self.nyan_hit_flash_timer > 0:
            self.nyan_hit_flash_timer -= 1
            if self.nyan_hit_flash_timer > 5:
                # Fondo rojo semitransparente (simula un flash de dano)
                self.canvas.create_rectangle(
                    0, self.alto_canvas // 2 - 32,
                    self.ancho_canvas, self.alto_canvas // 2 + 32,
                    fill='#1A0000', outline=''
                )
                # Icono y texto de aviso
                self.canvas.create_text(
                    self.ancho_canvas // 2, self.alto_canvas // 2 - 14,
                    text=u'⚠ NYAN CAT ⚠',
                    fill='#FF00FF', font=('Consolas', 13, 'bold')
                )
                self.canvas.create_text(
                    self.ancho_canvas // 2, self.alto_canvas // 2 + 10,
                    text=u'PUNTOS PERDIDOS',
                    fill='#FF4444', font=('Consolas', 10, 'bold')
                )

        # Flash verde al recoger el escudo
        if hasattr(self, 'shield_flash_timer') and self.shield_flash_timer > 0:
            self.shield_flash_timer -= 1
            if self.shield_flash_timer % 2 == 0:
                self.canvas.create_rectangle(
                    0, 0, self.ancho_canvas, self.alto_canvas,
                    fill='#003322', outline=''
                )
            if self.shield_flash_timer > 3:
                self.canvas.create_text(
                    self.ancho_canvas / 2, self.alto_canvas / 2 - 14,
                    text=u'\u26E8  ESCUDO ACTIVO  \u26E8',
                    fill='#00FFAA', font=('Consolas', 14, 'bold')
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
                verbo, objeto, params = accion.get('accion'), accion.get('objeto'), accion.get('params', [])

                if verbo == 'INCREASE_SCORE': 
                    self.puntuacion += int(objeto)
                    self.actualizar_marcador()
                elif verbo == 'DECREASE_SCORE':
                    self.puntuacion = max(0, self.puntuacion - int(objeto))
                    self.actualizar_marcador()
                elif verbo == 'RESET_SCORE':
                    self.puntuacion = 0
                    self.actualizar_marcador()
                elif verbo == 'GRANT_SHIELD':
                    # Buscar la duracion en cualquier powerup definido
                    duracion_ticks = 150  # Valor por defecto (7.5 segundos)
                    powerups = self.datos_juego.get('powerups', {})
                    for pu_nombre in powerups:
                        if 'duration' in powerups[pu_nombre] and powerups[pu_nombre]['duration'] is not None:
                            duracion_ticks = powerups[pu_nombre]['duration']
                            break
                    self.escudo_activo = True
                    self.escudo_restante = duracion_ticks
                    self.shield_flash_timer = 12
                elif verbo == 'GAME_OVER': 
                    self.juego_terminado = True

                if self.tipo_juego == 'TETRIS':
                    if verbo == 'SPAWN': self.tetris_spawn_pieza()
                    if verbo == 'MOVE':  self.tetris_mover_pieza(params[0])
                    if verbo == 'ROTATE': self.tetris_rotar_pieza()

                if self.tipo_juego == 'SNAKE':
                    if verbo == 'SPAWN':
                        if objeto == 'PLAYER': self.snake_spawn_jugador(accion)
                        elif objeto == 'FOOD': self.snake_spawn_comida()
                        elif objeto == 'POISON':
                            # Punto C: solo spawnear veneno si el nivel actual lo permite
                            cfg_nivel = self.levels_config.get(self.level, {})
                            if cfg_nivel.get('has_poison', True):  # True = fallback sin config
                                self.snake_spawn_veneno()
                            # Si has_poison es False, simplemente no se crea la fruta
                        elif objeto == 'CLOUD':
                            # Punto C: solo spawnear nubes si el nivel actual lo permite
                            cfg_nivel = self.levels_config.get(self.level, {})
                            if cfg_nivel.get('has_obstacles', True):
                                coords = params[0] if params else [0, 0]
                                self.posiciones_nubes.append((coords[0], coords[1]))
                        elif objeto == 'SHIELD':
                            # El escudo solo aparece si el nivel actual
                            # tiene HAS_POWERUP: TRUE en su configuracion.
                            # BABY -> False (sin escudo).
                            # ENTUSIASTA y NYAN_CAT -> True (escudo habilitado).
                            # Fallback True para archivos sin levels_config (retrocompat).
                            cfg_nivel_actual = self.levels_config.get(self.level, {})
                            if cfg_nivel_actual.get('has_powerup', True):
                                self.snake_spawn_escudo()
                    
                    if verbo == 'MOVE'  and objeto == 'PLAYER': self.snake_mover_jugador()
                    if verbo == 'GROW': self.snake_crecer()
                    if verbo == 'SET_DIRECTION': self.snake_cambiar_direccion(objeto)

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
        # Evitar posiciones ocupadas por serpiente, veneno, nubes y escudo
        ocupadas = set(self.serpiente_cuerpo)
        if self.posicion_veneno:
            ocupadas.add(self.posicion_veneno)
        if self.posicion_escudo:
            ocupadas.add(self.posicion_escudo)
        ocupadas.update(self.posiciones_nubes)
        while True:
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto  - 1)
            if (x, y) not in ocupadas:
                self.posicion_comida = (x, y)
                break

    def snake_mover_jugador(self):
        if not self.serpiente_cuerpo: return
        cabeza_x, cabeza_y = self.serpiente_cuerpo[0]
        dir_x,    dir_y    = self.serpiente_direccion
        nueva_cabeza = (cabeza_x + dir_x, cabeza_y + dir_y)

        # Colision con paredes
        if not (0 <= nueva_cabeza[0] < self.ancho and 0 <= nueva_cabeza[1] < self.alto):
            if self.escudo_activo:
                # Power-Up activo: wrap-around en lugar de muerte
                nueva_cabeza = (nueva_cabeza[0] % self.ancho,
                                nueva_cabeza[1] % self.alto)
            elif self.level == 'NYAN_CAT':
                # Colision con pared en NYAN_CAT -> logica especial:
                #   - Si tiene puntos: pierde TODOS los puntos, sigue vivo.
                #   - Si ya no tiene puntos: GAME OVER definitivo.
                # La serpiente hace wrap-around para continuar el movimiento.
                if self.puntuacion <= 0:
                    self.juego_terminado = True
                    return
                else:
                    self.puntuacion = 0
                    self.actualizar_marcador()
                    self.nyan_hit_flash_timer = 40   # activar mensaje visual
                    nueva_cabeza = (nueva_cabeza[0] % self.ancho,
                                    nueva_cabeza[1] % self.alto)
            else:
                self.ejecutar_evento('ON_COLLISION_WALL')
                return

        # Colision consigo misma
        if nueva_cabeza in self.serpiente_cuerpo[:-1]:
            if not self.escudo_activo:
                if self.level == 'NYAN_CAT':
                    # Colision con cuerpo propio en NYAN_CAT -> logica especial:
                    #   - Si tiene puntos: pierde TODOS los puntos, sigue vivo.
                    #   - Si ya no tiene puntos: GAME OVER definitivo.
                    # La serpiente continua moviendose (atraviesa su cuerpo).
                    if self.puntuacion <= 0:
                        self.juego_terminado = True
                        return
                    else:
                        self.puntuacion = 0
                        self.actualizar_marcador()
                        self.nyan_hit_flash_timer = 40   # activar mensaje visual
                    # No retornamos: la serpiente sigue viva
                else:
                    self.ejecutar_evento('ON_COLLISION_SELF')
                    return
            # Con escudo: se ignora la colision (la serpiente sigue)

        self.serpiente_cuerpo.insert(0, nueva_cabeza)

        # --- Colision con comida normal ---
        if nueva_cabeza == self.posicion_comida:
            self.ejecutar_evento('ON_EAT_FOOD')
        else:
            self.serpiente_cuerpo.pop()

        # --- SNAKE EVOLVED: Colision con fruta venenosa ---
        if self.posicion_veneno and nueva_cabeza == self.posicion_veneno:
            self.posicion_veneno = None  # consumir la fruta venenosa
            if not self.escudo_activo:
                # En niveles ENTUSIASTA y superiores el veneno solo resta puntos
                # (ON_EAT_POISON ya hace DECREASE_SCORE 5).
                # En MEDIUM/HARD/NYAN_CAT el veneno es letal ademas de restar.
                niveles_letales = ('MEDIUM', 'HARD', 'NYAN_CAT')
                if self.level in niveles_letales:
                    self.juego_terminado = True
                else:
                    self.ejecutar_evento('ON_EAT_POISON')

        # --- SNAKE EVOLVED: Colision con nube obstaculo ---
        if nueva_cabeza in self.posiciones_nubes:
            if not self.escudo_activo:
                if self.puntuacion <= 0:
                    self.juego_terminado = True
                else:
                    self.ejecutar_evento('ON_COLLISION_CLOUD')

        # --- SNAKE EVOLVED: Colision con escudo ---
        if self.posicion_escudo and nueva_cabeza == self.posicion_escudo:
            self.posicion_escudo = None  # consumir el escudo
            self.ejecutar_evento('ON_EAT_SHIELD')

    def snake_spawn_veneno(self):
        ocupadas = set(self.serpiente_cuerpo)
        if self.posicion_comida: ocupadas.add(self.posicion_comida)
        if self.posicion_escudo: ocupadas.add(self.posicion_escudo)
        ocupadas.update(self.posiciones_nubes)
        intentos = 0
        while intentos < 200:
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto  - 1)
            if (x, y) not in ocupadas:
                self.posicion_veneno = (x, y)
                return
            intentos += 1

    def snake_spawn_escudo(self):
        ocupadas = set(self.serpiente_cuerpo)
        if self.posicion_comida: ocupadas.add(self.posicion_comida)
        if self.posicion_veneno: ocupadas.add(self.posicion_veneno)
        ocupadas.update(self.posiciones_nubes)
        intentos = 0
        while intentos < 200:
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto  - 1)
            if (x, y) not in ocupadas:
                self.posicion_escudo = (x, y)
                return
            intentos += 1

    def snake_cambiar_direccion(self, direccion):
        if direccion == 'UP'    and self.serpiente_direccion[1] != 1:  self.serpiente_direccion = (0, -1)
        elif direccion == 'DOWN'  and self.serpiente_direccion[1] != -1: self.serpiente_direccion = (0,  1)
        elif direccion == 'LEFT'  and self.serpiente_direccion[0] != 1:  self.serpiente_direccion = (-1, 0)
        elif direccion == 'RIGHT' and self.serpiente_direccion[0] != -1: self.serpiente_direccion = (1,  0)

    def snake_crecer(self):
        # ACTIVIDAD 4 - Al crecer, verificar si se debe subir de nivel.
        # La serpiente crece duplicando el ultimo segmento del cuerpo.
        if self.serpiente_cuerpo:
            self.serpiente_cuerpo.append(self.serpiente_cuerpo[-1])

        # Subida de nivel progresiva: se evalua cada vez que el jugador come.
        # Solo se sube hasta el nivel_maximo definido en el .brick.
        idx_maximo = self.secuencia_niveles.index(self.nivel_maximo)                      if self.nivel_maximo in self.secuencia_niveles                      else len(self.secuencia_niveles) - 1

        nivel_nuevo = self.level
        for nombre_nivel in self.secuencia_niveles[:idx_maximo + 1]:
            if self.puntuacion >= self.umbrales_nivel[nombre_nivel]:
                nivel_nuevo = nombre_nivel

        if nivel_nuevo != self.level:
            self.level = nivel_nuevo
            self.velocidad_gravedad = self.velocidades_nivel.get(self.level, 0.15)
            self.root.title('BrickScript - SNAKE  |  Nivel: ' + self.level)
            # NUEVO: activar flash de subida de nivel
            self.nivel_flash_timer = 30    # 30 frames ≈ 1.5 segundos de notificación
            self.nivel_anterior    = self.level
            # NUEVO: limpiar nubes si el nivel nuevo no las admite
            if self.levels_config:
                cfg = self.levels_config.get(self.level, {})

                # Separamos la gestion de nubes (has_obstacles) de la del escudo
                # (has_powerup). Antes estaban acopladas: al entrar en ENTUSIASTA
                # (sin nubes pero CON escudo) se eliminaba el escudo tambien.

                # Gestionar nubes segun HAS_OBSTACLES
                if cfg.get('has_obstacles', True):
                    # Nivel con obstaculos: reponer nubes
                    self.posiciones_nubes = [(5, 5), (15, 15), (5, 15), (15, 5)]
                else:
                    # Nivel sin obstaculos: eliminar nubes
                    self.posiciones_nubes = []

                # Gestionar escudo segun HAS_POWERUP (independiente de nubes)
                if cfg.get('has_powerup', True):
                    # Nivel con power-up habilitado: spawnear escudo si no existe
                    if self.posicion_escudo is None:
                        self.snake_spawn_escudo()
                else:
                    # Nivel sin power-up: eliminar escudo si existe
                    self.posicion_escudo = None

    def actualizar_marcador(self):
        if self.es_remake:
            if self.label_score: self.label_score.config(text=str(self.puntuacion))
            # Actualizar badge de nivel
            if hasattr(self, 'label_nivel_actual') and self.label_nivel_actual:
                color_nv = self.colores_nivel.get(self.level, '#FFFFFF')
                self.label_nivel_actual.config(text=self.level, fg=color_nv)

            # Actualizar barra de escudo
            # Actualizar barra de escudo
            if hasattr(self, 'shield_bar_canvas') and self.shield_bar_canvas:
                self.shield_bar_canvas.delete('all')
                # Calcular duración máxima (siempre, no solo cuando está activo)
                duracion_max = 150
                powerups = self.datos_juego.get('powerups', {})
                for pu in powerups.values():
                    if pu.get('duration'):
                        duracion_max = pu['duration']
                        break

                if self.escudo_activo and self.escudo_restante > 0:
                    # Fondo con borde verde
                    self.shield_bar_canvas.create_rectangle(
                        0, 0, 120, 12, fill='#0A1A10', outline='#00AA66', width=1
                    )
                    # Segmentos de la barra (10 segmentos)
                    num_seg = 10
                    seg_activos = int(num_seg * (float(self.escudo_restante) / duracion_max))
                    for s in range(num_seg):
                        sx1 = s * 12 + 1
                        sx2 = sx1 + 10
                        if s < seg_activos:
                            verde = min(255, 180 + s * 6)
                            col_seg = '#{:02X}{:02X}{:02X}'.format(0, verde, int(verde * 0.6))
                            self.shield_bar_canvas.create_rectangle(
                                sx1, 2, sx2, 10, fill=col_seg, outline=''
                            )
                        else:
                            self.shield_bar_canvas.create_rectangle(
                                sx1, 2, sx2, 10, fill='#0D1A10', outline=''
                            )
                else:
                    # Sin escudo: barra vacía con borde gris
                    self.shield_bar_canvas.create_rectangle(
                        0, 0, 120, 12, fill='#0A0A15', outline='#2A2A3A', width=1
                    )
                    for s in range(10):
                        self.shield_bar_canvas.create_rectangle(
                            s * 12 + 1, 2, s * 12 + 11, 10,
                            fill='#111122', outline=''
                        )
            if self.label_lineas and self.tipo_juego == 'TETRIS':
                self.label_lineas.config(text=str(self.lineas_eliminadas_total))
        else:
            if self.label_score: self.label_score.config(text='PUNTUACION\n' + str(self.puntuacion))

    # SALIDA

    def mostrar_game_over(self):
        """Muestra una ventana de Game Over estilizada en lugar del messagebox genérico."""
        ventana_go = tk.Toplevel(self.root)
        ventana_go.title('GAME OVER')
        ventana_go.resizable(False, False)
        ventana_go.configure(bg='#07070E')
        ventana_go.grab_set()  # Modal

        # Centrar sobre la ventana principal
        ventana_go.geometry('280x200+{}+{}'.format(
            self.root.winfo_x() + 60,
            self.root.winfo_y() + 80
        ))

        tk.Label(ventana_go, text='GAME OVER',
                bg='#07070E', fg='#FF2222',
                font=('Consolas', 22, 'bold')).pack(pady=(24, 4))

        tk.Label(ventana_go, text=u'\u2550' * 22,
                bg='#07070E', fg='#2A1A5A',
                font=('Consolas', 8)).pack()

        tk.Label(ventana_go, text='PUNTUACION FINAL',
                bg='#07070E', fg='#888888',
                font=('Consolas', 9)).pack(pady=(12, 2))

        tk.Label(ventana_go, text=str(self.puntuacion),
                bg='#07070E', fg='#FFFFFF',
                font=('Consolas', 28, 'bold')).pack()

        color_nv = self.colores_nivel.get(self.level, '#FFFFFF') if hasattr(self, 'colores_nivel') else '#FFFFFF'
        tk.Label(ventana_go, text='Nivel alcanzado: ' + self.level,
                bg='#07070E', fg=color_nv,
                font=('Consolas', 9)).pack(pady=(6, 0))

        def salir():
            ventana_go.destroy()
            self.root.destroy()
            sys.exit(0)

        tk.Button(ventana_go, text='  SALIR  ',
                bg='#1A0033', fg='#FF44FF',
                activebackground='#330055', activeforeground='white',
                font=('Consolas', 11, 'bold'),
                relief=tk.FLAT, cursor='hand2',
                command=salir).pack(pady=(16, 0))

        ventana_go.protocol('WM_DELETE_WINDOW', salir)
        self.root.wait_window(ventana_go)


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
    