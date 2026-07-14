# -*- coding: utf-8 -*-
# # Cambios (Actividad 3 - Punto B):
# # 1. Clase Juego.__init__() - seccion TETRIS:
# #    - Se inicializa self.pieza_color = '#00FFFF' como color por defecto.
# #    - Esto evita un AttributeError si dibujar() se llama antes de que
# #      tetris_spawn_pieza() asigne el color de la primera pieza.
# # 2. Metodo tetris_spawn_pieza():
# #    - ANTES: elegía la pieza con random.choice() (probabilidad uniforme).
# #    - AHORA: usa seleccion ponderada basada en los pesos del campo
# #      'shape_chances' del JSON. Si el JSON no tiene ese campo (archivo
# #      antiguo), todos los pesos valen 1 y el comportamiento es identico
# #      al original.
# #    - AHORA: lee el color de la pieza desde 'shape_colors'. Si el campo
# #      no existe (JSON antiguo), usa '#00FFFF' como fallback.
# # 3. Metodo dibujar() - bloque TETRIS:
# #    - ANTES: COLOR_PIEZA = '#00FFFF' (hardcoded).
# #    - AHORA: COLOR_PIEZA = self.pieza_color (leido dinamicamente).
# #    - RETROCOMPATIBILIDAD: como pieza_color siempre tiene un valor
# #      (inicializado en __init__ y actualizado en spawn), el dibujo
# #      funciona tanto con JSON nuevos como antiguos.
# #
# # Cambios (Actividad 3 - Punto C - Power-Ups):
# # 1. Juego.__init__() - TETRIS:
# #    - Se agregan variables de estado para power-ups:
# #      lineas_ultimo_clear, powerup_pendiente, es_powerup_activo,
# #      nombre_pieza_actual, rotaciones_powerup, modo_bomba_activo,
# #      degradado_frame.
# # 2. tetris_rotar_pieza():
# #    - Incrementa rotaciones_powerup cuando el TRIPLE_CLEAR_PU esta activo.
# #    - Activa modo_bomba_activo al llegar a 10 rotaciones.
# # 3. tetris_fijar_pieza():
# #    - Si modo_bomba_activo es True, elimina las filas ocupadas por el powerup
# #      y suma 500 puntos por fila. Resetea todos los contadores de powerup.
# # 4. tetris_limpiar_lineas():
# #    - Guarda lineas_ultimo_clear para comunicarse con spawn.
# #    - Evalua los triggers de powerups del JSON y pone powerup_pendiente.
# # 5. tetris_spawn_pieza():
# #    - Si hay powerup_pendiente, spawna el powerup en lugar de pieza normal.
# #    - Resetea es_powerup_activo y nombre_pieza_actual en spawn normal.
# # 6. dibujar():
# #    - Si modo_bomba_activo, calcula color HSV ciclico para el degradado
# #      animado (sin librerias externas, solo aritmetica basica).
# #
# # Cambios (Actividad 3 - Punto C - Extension visual y nuevo PowerUp):
# # 1. __init__() - TETRIS:
# #    - Nuevas variables: lineas_totales_eliminadas (contador acumulado para
# #      LINE_PURGE_PU), pieza_siguiente / siguiente_color (preview del panel),
# #      flash_powerup_timer (contador para parpadeo al spawnear un PU),
# #      borde_arcoiris_frame (animacion de borde cuando modo_bomba_activo).
# # 2. __init__() - GUI:
# #    - Panel lateral rediseñado: fondo oscuro con degradado simulado, label de
# #      nivel, canvas de preview de siguiente pieza, label de controles mejorado.
# #    - Marco principal con borde animable (se actualiza en dibujar()).
# # 3. tetris_spawn_pieza():
# #    - Al generar pieza normal, calcula y guarda la siguiente (para el preview).
# #    - LINE_PURGE_PU no spawna pieza visible: aplica efecto directo y retorna.
# #    - Al spawnear cualquier PU activa flash_powerup_timer = 8.
# # 4. tetris_limpiar_lineas():
# #    - Incrementa lineas_totales_eliminadas.
# #    - Evalua trigger LINE_CUMULATIVE: si acumulado % valor == 0 activa PU.
# # 5. dibujar():
# #    - Dibuja borde del canvas animado en arcoiris cuando modo_bomba_activo.
# #    - Dibuja flash de pantalla (overlay semitransparente) cuando flash_powerup_timer > 0.
# #    - Dibuja letrero "!POWER UP!" animado encima del canvas cuando flash activo.
# #    - Llama a dibujar_preview() para actualizar el canvas lateral.
# # 6. dibujar_preview() (NUEVO):
# #    - Dibuja la siguiente pieza centrada en el canvas de preview del panel.
# # 7. dibujar_celda_canvas() (NUEVO):
# #    - Version de dibujar_celda() que acepta un canvas arbitrario como parametro,
# #      usada por dibujar_preview().
# # 8. Estilo general:
# #    - Colores de celdas fijas mejorados (gradiente simulado por fila).
# #    - Borde biselado en cada celda (highlight claro arriba-izquierda,
# #      sombra oscura abajo-derecha).

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
        # Actividad Final: detectar si la version merece GUI mejorada.
        # Antes se comparaba contra la cadena literal 'remake'. Ahora se
        # acepta cualquier version que NO sea 'original', lo que incluye
        # 'remake' (tetris_remake, snake_evolved) y futuros juegos extendidos.
        # Los JSON sin campo 'version' o con 'original' mantienen la GUI clasica.
        # TANKS tiene su propia GUI dedicada (no usa es_remake).
        self.es_remake = (self.datos_juego.get('version', 'original') not in ('original', 'tanks'))
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

        # TANKS: calcular tamaño de celda automáticamente según pantalla disponible
        if self.datos_juego.get('version') == 'tanks':
            _root_tmp = tk.Tk()
            _root_tmp.withdraw()
            pantalla_w = _root_tmp.winfo_screenwidth()
            pantalla_h = _root_tmp.winfo_screenheight()
            _root_tmp.destroy()
            PANEL_W    = 180          # ancho del panel lateral reservado
            MARGEN     = 32           # márgenes y paddings
            max_w = pantalla_w - PANEL_W - MARGEN
            max_h = pantalla_h - MARGEN - 60   # 60 para barra de título OS
            celda_por_ancho = max_w // self.ancho
            celda_por_alto  = max_h // self.alto
            self.taman_celda = max(20, min(celda_por_ancho, celda_por_alto, 52))
        else:
            self.taman_celda = 25
        self.ancho_canvas = self.ancho * self.taman_celda
        self.alto_canvas  = self.alto  * self.taman_celda

        if self.datos_juego.get('version') == 'tanks':
            # GUI exclusiva de TANKS — se construye aquí para no heredar
            # ni el canvas del bloque remake ni el del bloque original.
            PANEL_BG = '#0E0E1C'
            self.root.configure(bg='#0A0A14')
            self.canvas = tk.Canvas(
                self.root,
                width=self.ancho_canvas, height=self.alto_canvas,
                bg='#0A0A14', highlightthickness=2,
                highlightbackground='#333366'
            )
            self.canvas.pack(side=tk.LEFT, padx=8, pady=8)

            self.marco_score = tk.Frame(self.root, width=170, bg=PANEL_BG)
            self.marco_score.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=8)
            self.marco_score.pack_propagate(False)

            tk.Label(self.marco_score, text='BRICK TANKS',
                     bg=PANEL_BG, fg='#00FFFF',
                     font=('Courier', 12, 'bold')).pack(pady=(14, 6))

            tk.Label(self.marco_score, text='SCORE',
                     bg=PANEL_BG, fg='#888888',
                     font=('Courier', 8)).pack()
            self.lbl_score = tk.Label(self.marco_score, text='0',
                                      bg=PANEL_BG, fg='#FFFFFF',
                                      font=('Courier', 18, 'bold'))
            self.lbl_score.pack(pady=(0, 12))

            tk.Label(self.marco_score, text='PLAYER HP',
                     bg=PANEL_BG, fg='#888888',
                     font=('Courier', 8)).pack()
            # placeholder — se rellena después de que TANKS init cargue player_hp
            self.lbl_player_hp = tk.Label(self.marco_score, text='-- / --',
                                          bg=PANEL_BG, fg='#00FF88',
                                          font=('Courier', 11, 'bold'))
            self.lbl_player_hp.pack(pady=(0, 12))

            tk.Label(self.marco_score, text='ENEMIES',
                     bg=PANEL_BG, fg='#888888',
                     font=('Courier', 8)).pack()
            self.lbl_enemies = tk.Label(self.marco_score, text='--',
                                        bg=PANEL_BG, fg='#FF4444',
                                        font=('Courier', 16, 'bold'))
            self.lbl_enemies.pack(pady=(0, 12))

            tk.Label(self.marco_score, text='OLEADA',
                     bg=PANEL_BG, fg='#888888',
                     font=('Courier', 8)).pack()
            self.lbl_wave = tk.Label(self.marco_score, text='1',
                                     bg=PANEL_BG, fg='#FFDD44',
                                     font=('Courier', 16, 'bold'))
            self.lbl_wave.pack(pady=(0, 12))

            # Actividad 5-B: Etiqueta de HP del boss — solo visible en fase boss
            # Se muestra vacia hasta que el boss aparece (boss_phase_active = True)
            tk.Label(self.marco_score, text='BOSS HP',
                     bg=PANEL_BG, fg='#FF00FF',
                     font=('Courier', 8)).pack()
            self.lbl_boss_hp = tk.Label(self.marco_score, text='',
                                        bg=PANEL_BG, fg='#FF44FF',
                                        font=('Courier', 11, 'bold'))
            self.lbl_boss_hp.pack(pady=(0, 8))

            # Barra de vida del boss (canvas de 120x12 px)
            self.boss_hp_bar = tk.Canvas(
                self.marco_score, width=120, height=10,
                bg='#1A001A', highlightthickness=1, highlightbackground='#440044'
            )
            self.boss_hp_bar.pack(pady=(0, 12))

            tk.Label(self.marco_score,
                     text='[WASD] Mover\n[SPACE] Disparar',
                     bg=PANEL_BG, fg='#555577',
                     font=('Courier', 8), justify=tk.LEFT).pack(pady=(24, 4))

            # Atributos que otros modos usan — poner None para evitar AttributeError
            self.label_score       = None
            self.label_lineas      = None
            self.label_powerup     = None
            self.preview_canvas    = None
            self.label_nivel_actual = None
            self.shield_bar_canvas = None
            # Actividad 5-B: estos atributos solo existen en el GUI de TANKS
            # Se exponen aqui para evitar AttributeError si el runtime llama
            # a metodos de tanks en un contexto inesperado (retrocompat).
            # En el bloque TANKS ya se asignan los widgets reales; aqui no.
            # (No hace falta ponerlos en None, el hasattr() los protege,
            #  pero se documentan para claridad del equipo.)

        elif self.es_remake:
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
            self._init_tetris()
        elif self.tipo_juego == 'SNAKE':
            self._init_snake()
        elif self.tipo_juego == 'TANKS':
            self._init_tanks()

        self.timer_gravedad = 0
        self.ejecutar_evento('ON_START')
        self.timer_id = None

    def _init_tetris(self):
        self.pieza_actual   = None
        self.pieza_x        = 0
        self.pieza_y        = 0
        self.pieza_rotacion = 0
        self.velocidad_gravedad = 0.4
        self.pieza_color = '#00FFFF'
        self.level = 'TETRIS'
        self.colores_nivel = {'TETRIS': '#00FFFF'}
        self.levels_config = {}
        self.lineas_ultimo_clear  = 0
        self.powerup_pendiente    = None
        self.es_powerup_activo    = False
        self.nombre_pieza_actual  = ''
        self.rotaciones_powerup   = 0
        self.modo_bomba_activo    = False
        self.degradado_frame      = 0
        self.lineas_totales_eliminadas = 0
        self.pieza_siguiente    = None
        self.siguiente_color    = '#FFFFFF'
        self.flash_powerup_timer = 0
        self.borde_arcoiris_frame = 0
        self.lineas_eliminadas_total = 0

    def _init_snake(self):
        self.serpiente_cuerpo    = []
        self.serpiente_direccion = (1, 0)
        self.posicion_comida     = None
        self.posiciones_veneno   = []
        self.poison_max          = 3
        self.poison_vida_ticks   = 80
        self.posiciones_nubes    = []
        self.escudo_activo       = False
        self.escudo_fue_activado_alguna_vez = False
        self.escudo_restante     = 0
        self.posicion_escudo     = None
        self.escudo_halo_frame   = 0
        self.snake_shape = self.datos_juego.get('shape_types', {}).get('PIXEL', 'RECTANGULAR')
        self.nivel_maximo  = self.datos_juego.get('level', 'BABY')
        self.secuencia_niveles = ['BABY', 'EASY', 'ENTUSIASTA', 'MEDIUM', 'HARD', 'NYAN_CAT']
        self.umbrales_nivel = {
            'BABY':       0,
            'EASY':       20,
            'ENTUSIASTA': 30,
            'MEDIUM':     50,
            'HARD':       80,
            'NYAN_CAT':   120,
        }
        self.velocidades_nivel = {
            'BABY':       0.15,
            'EASY':       0.10,
            'ENTUSIASTA': 0.08, 
            'MEDIUM':     0.08,
            'HARD':       0.06,
            'NYAN_CAT':   0.03,
        }
        self.level = 'BABY'
        self.velocidad_gravedad = self.velocidades_nivel['BABY']
        self.nyan_colors = [
            '#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3'
        ]
        self.root.title('BrickScript - SNAKE  |  Nivel: BABY')
        self.levels_config = self.datos_juego.get('levels', {})
        if self.levels_config:
            for nombre_nv, cfg in self.levels_config.items():
                self.umbrales_nivel[nombre_nv]   = cfg.get('min_score', self.umbrales_nivel.get(nombre_nv, 0))
                self.velocidades_nivel[nombre_nv] = cfg.get('speed', 15) / 100.0
            self.secuencia_niveles = sorted(
                self.levels_config.keys(),
                key=lambda n: self.levels_config[n].get('min_score', 0)
            )
        self.food_pulse_frame    = 0
        self.poison_flash_frame  = 0
        self.shield_spin_frame   = 0
        self.shield_flash_timer  = 0
        self.nivel_flash_timer   = 0
        self.nivel_anterior      = 'BABY'
        self.nyan_hit_flash_timer = 0

    def _init_tanks(self):
        roles   = self.datos_juego.get('entity_roles', {})
        healths = self.datos_juego.get('entity_health', {})
        speeds  = self.datos_juego.get('entity_speed', {})
        frates  = self.datos_juego.get('entity_fire_rate', {})
        cbh_map = self.datos_juego.get('entity_color_by_health', {})
        self.player_shape_name = next(
            (n for n, r in roles.items() if r == 'PLAYER'), None
        )
        self.player_pos      = [self.ancho // 2, self.alto // 2]
        self.player_dir      = 'UP'
        self.player_hp       = healths.get(self.player_shape_name, 100)
        self.player_hp_max   = self.player_hp
        self.player_speed    = speeds.get(self.player_shape_name, 3)
        self.player_speed_counter = 0
        self.enemies = []
        for shape_name, role in roles.items():
            if role == 'ENEMY':
                self.enemies.append({
                    'shape':        shape_name,
                    'pos':          [0, 0],
                    'hp':           healths.get(shape_name, 30),
                    'hp_max':       healths.get(shape_name, 30),
                    'speed':        speeds.get(shape_name, 1),
                    'speed_counter': 0,
                    'fire_rate':    frates.get(shape_name, 60),
                    'fire_counter': random.randint(0, frates.get(shape_name, 60)),
                    'color':        self.datos_juego.get('shape_colors', {}).get(shape_name, '#FF4444'),
                    'cbh':          cbh_map.get(shape_name, {}),
                    'is_boss':      False,
                    'alive':        False,
                })
        self.bullets = []
        self.walls = []
        self.hammer_pos     = None
        self.hammer_timer   = 0
        self.hammer_heal    = self.datos_juego.get('powerups', {}).get(
                                'HAMMER_PU', {}).get('chance', 15)
        self.hammer_hp_restore = 25
        self.tanks_game_over = False
        self.tanks_player_win = False
        self.tanks_wave = 1
        self.tanks_kill_count = 0
        self.boss_score_threshold = self.datos_juego.get('boss_score_threshold', 500)
        self.boss_phase_active = False
        self.boss_defeated = False
        self.tanks_wave_spawned = False
        self.tanks_enemy_templates = []
        for e in self.enemies:
            if not e['is_boss']:
                self.tanks_enemy_templates.append({
                    'shape':     e['shape'],
                    'hp':        e['hp_max'],
                    'hp_max':    e['hp_max'],
                    'speed':     e['speed'],
                    'fire_rate': e['fire_rate'],
                    'color':     e['color'],
                    'cbh':       e['cbh'],
                    'is_boss':   False,
                })
        if hasattr(self, 'lbl_player_hp'):
            self.lbl_player_hp.config(
                text=str(self.player_hp) + ' / ' + str(self.player_hp_max)
            )
        if hasattr(self, 'lbl_enemies'):
            vivos_init = sum(1 for e in self.enemies if e['alive'])
            self.lbl_enemies.config(text=str(vivos_init))

    def run(self):
        self.root.after(50, self.game_loop)
        self.root.mainloop()

    def game_loop(self):
        if self.juego_terminado:
            self.mostrar_game_over()
            return

        if self.tipo_juego == 'TANKS':
            if self.tanks_game_over:
                self.mostrar_game_over()
                return
            self._loop_tanks()
            self.dibujar()
            self.timer_id = self.root.after(80, self.game_loop)
        elif self.tipo_juego == 'SNAKE':
            self._loop_snake()
            self.dibujar()
            if self.es_remake:
                self.actualizar_marcador()
            self.timer_id = self.root.after(50, self.game_loop)
        elif self.tipo_juego == 'TETRIS':
            self._loop_tetris()
            self.dibujar()
            self.timer_id = self.root.after(50, self.game_loop)

    def _loop_tanks(self):
        if getattr(self, 'player_fire_cooldown', 0) > 0:
            self.player_fire_cooldown -= 1
        if not self.tanks_wave_spawned and any(e['alive'] for e in self.enemies):
            self.tanks_wave_spawned = True
        self.tanks_tick_enemies()
        self.tanks_tick_bullets()
        self.tanks_tick_hammer()
        self.tanks_check_boss_transition()
        self.tanks_check_win()

    def _loop_snake(self):
        if self.escudo_activo:
            self.escudo_restante -= 1
            if self.escudo_restante <= 0:
                self.escudo_activo = False
        
        nuevas = []
        for entrada in self.posiciones_veneno:
            vx, vy, vida = entrada
            vida -= 1
            if vida <= 0:
                nueva_pos = self._veneno_buscar_pos()
                if nueva_pos:
                    nuevas.append([nueva_pos[0], nueva_pos[1], self.poison_vida_ticks])
            else:
                nuevas.append([vx, vy, vida])
        self.posiciones_veneno = nuevas

        self.timer_gravedad += 0.05
        if self.timer_gravedad >= self.velocidad_gravedad:
            self.timer_gravedad = 0
            self.ejecutar_evento('ON_TICK')

    def _loop_tetris(self):
        self.timer_gravedad += 0.05
        if self.timer_gravedad >= self.velocidad_gravedad:
            self.timer_gravedad = 0
            self.ejecutar_evento('ON_TICK')

    def cerrar_ventana(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        sys.exit(0)

    def manejar_input_gui(self, event):
        if self.tipo_juego == 'TETRIS':
            self._input_tetris(event)
        elif self.tipo_juego == 'SNAKE':
            self._input_snake(event)
        elif self.tipo_juego == 'TANKS':
            self._input_tanks(event)

    def _input_tetris(self, event):
        key = event.keysym.upper()
        if key == 'UP':    self.ejecutar_evento('ON_KEY_UP')
        elif key == 'DOWN':  self.ejecutar_evento('ON_KEY_DOWN')
        elif key == 'LEFT':  self.ejecutar_evento('ON_KEY_LEFT')
        elif key == 'RIGHT': self.ejecutar_evento('ON_KEY_RIGHT')

    def _input_snake(self, event):
        key = event.keysym.upper()
        if key == 'UP':    self.snake_cambiar_direccion('UP')
        elif key == 'DOWN':  self.snake_cambiar_direccion('DOWN')
        elif key == 'LEFT':  self.snake_cambiar_direccion('LEFT')
        elif key == 'RIGHT': self.snake_cambiar_direccion('RIGHT')

    def _input_tanks(self, event):
        mapa = {
            'Up': 'UP', 'w': 'UP', 'W': 'UP',
            'Down': 'DOWN', 's': 'DOWN', 'S': 'DOWN',
            'Left': 'LEFT', 'a': 'LEFT', 'A': 'LEFT',
            'Right': 'RIGHT', 'd': 'RIGHT', 'D': 'RIGHT',
        }
        if event.keysym in mapa:
            self.tanks_mover_jugador(mapa[event.keysym])
        elif event.keysym == 'space':
            self.tanks_disparar_jugador()

    def dibujar(self):
        self.canvas.delete("all")
        if self.tipo_juego == 'TETRIS':
            self._dibujar_tetris()
        elif self.tipo_juego == 'SNAKE':
            self._dibujar_snake()
        elif self.tipo_juego == 'TANKS':
            self._dibujar_tanks()

    def _dibujar_tetris(self):
        if self.es_remake:
            self.label_score.config(text=str(self.puntuacion))
            self.label_lineas.config(text=str(self.lineas_eliminadas_total))
        else:
            self.label_score.config(text='PUNTUACION\n' + str(self.puntuacion))

        if self.es_remake:
            if self.modo_bomba_activo:
                self.borde_arcoiris_frame = (self.borde_arcoiris_frame + 6) % 360
                r2, g2, b2 = self._hsv_a_rgb(self.borde_arcoiris_frame)
                color_borde = '#{:02X}{:02X}{:02X}'.format(r2, g2, b2)
                self.canvas.config(highlightbackground=color_borde, highlightthickness=3)
            else:
                self.canvas.config(highlightbackground='#1A1A3A', highlightthickness=2)

        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    if self.es_remake:
                        intensidad = int(40 + (float(y) / self.alto) * 30)
                        color_fija = '#{:02X}{:02X}{:02X}'.format(intensidad + 10, intensidad, intensidad + 25)
                        self.dibujar_celda_estilo(x, y, color_fija)
                    else:
                        self.dibujar_celda(x, y, '#343434')
                else:
                    if self.es_remake:
                        ts = self.taman_celda
                        x1, y1 = x * ts, y * ts
                        x2, y2 = x1 + ts, y1 + ts
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill='', outline='#151525')

        if self.pieza_actual:
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
                            self.dibujar_celda_estilo(self.pieza_x + x_offset, self.pieza_y + y_offset, COLOR_PIEZA)
                        else:
                            self.dibujar_celda(self.pieza_x + x_offset, self.pieza_y + y_offset, COLOR_PIEZA)

        if self.es_remake and self.flash_powerup_timer > 0:
            self.flash_powerup_timer -= 1
            alpha_idx = self.flash_powerup_timer
            if alpha_idx % 2 == 0:
                self.canvas.create_rectangle(0, 0, self.ancho_canvas, self.alto_canvas, fill='#220033', outline='')
            if alpha_idx > 2:
                self.canvas.create_text(self.ancho_canvas / 2, self.alto_canvas / 2 - 16, text='! POWER UP !', fill='#FF00FF', font=('Consolas', 18, 'bold'))
                self.canvas.create_text(self.ancho_canvas / 2, self.alto_canvas / 2 + 12, text=self.nombre_pieza_actual, fill='#FF88FF', font=('Consolas', 10))

        if self.es_remake:
            self.dibujar_preview()

    def _dibujar_snake(self):
        COLOR_SNAKE_CABEZA = '#00FF00'
        COLOR_SNAKE_CUERPO = '#33CC33'
        COLOR_FOOD         = '#FF0000'

        if self.es_remake:
            self.label_score.config(text=str(self.puntuacion))
        else:
            self.label_score.config(text='PUNTUACION\n' + str(self.puntuacion))

        if self.es_remake:
            if hasattr(self, 'escudo_activo') and self.escudo_activo:
                pulso_borde = abs(math.sin(self.escudo_halo_frame * 0.12))
                verde_int = int(150 + pulso_borde * 105)
                color_escudo_borde = '#{:02X}{:02X}{:02X}'.format(0, verde_int, int(verde_int * 0.65))
                self.canvas.config(highlightbackground=color_escudo_borde, highlightthickness=3)
            else:
                self.canvas.config(highlightbackground='#1A1A3A', highlightthickness=2)

        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    pass
                else:
                    if self.es_remake:
                        ts = self.taman_celda
                        x1, y1 = x * ts, y * ts
                        x2, y2 = x1 + ts, y1 + ts
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill='', outline='#151525')

        self.food_pulse_frame   = (self.food_pulse_frame   + 1) % 360
        self.poison_flash_frame = (self.poison_flash_frame + 1) % 60
        self.shield_spin_frame  = (self.shield_spin_frame  + 1) % 360

        if self.posicion_comida:
            x, y = self.posicion_comida
            ts = self.taman_celda
            px, py = x * ts, y * ts
            if self.es_remake:
                pulso = math.sin(self.food_pulse_frame * 0.18)
                radio_extra = int(pulso * 3)
                margen = 3 - radio_extra
                self.canvas.create_oval(px + margen - 2, py + margen - 2, px + ts - margen + 2, py + ts - margen + 2, fill='#880000', outline='')
                self.canvas.create_oval(px + margen, py + margen, px + ts - margen, py + ts - margen, fill='#FF2222', outline='#FF8888', width=1)
                self.canvas.create_oval(px + margen + 2, py + margen + 2, px + margen + 7, py + margen + 7, fill='#FF9999', outline='')
            else:
                self.dibujar_celda(x, y, COLOR_FOOD)

        for entrada in self.posiciones_veneno:
            vx, vy, vida = entrada
            ts = self.taman_celda
            px, py = vx * ts, vy * ts
            fraccion_vida = vida / float(self.poison_vida_ticks)
            if self.es_remake:
                brillo = int(180 + 75 * fraccion_vida)
                brillo = min(255, brillo)
                if (self.poison_flash_frame // 15) % 2 == 0:
                    cv = '#{:02X}00{:02X}'.format(brillo, brillo // 2)
                else:
                    cv = '#CC00CC'
                self.canvas.create_oval(px + 1, py + 1, px + ts - 1, py + ts - 1, fill=cv, outline='#880088', width=2)
                self.canvas.create_line(px+5, py+5, px+ts-5, py+ts-5, fill='white', width=3)
                self.canvas.create_line(px+ts-5, py+5, px+5, py+ts-5, fill='white', width=3)
                self.canvas.create_oval(px+6, py+6, px+10, py+10, fill='black', outline='')
                self.canvas.create_oval(px+ts-10, py+6, px+ts-6, py+10, fill='black', outline='')
            else:
                self.dibujar_celda(vx, vy, '#FF00FF')
                self.canvas.create_line(px+4, py+4, px+ts-4, py+ts-4, fill='black', width=2)
                self.canvas.create_line(px+ts-4, py+4, px+4, py+ts-4, fill='black', width=2)

        for nx, ny in self.posiciones_nubes:
            ts = self.taman_celda
            px, py = nx * ts, ny * ts
            cx, cy = px + ts / 2, py + ts / 2
            if self.es_remake:
                self.canvas.create_oval(px+2, cy-4, px+ts-2, cy+ts//2-2, fill='#777777', outline='')
                self.canvas.create_oval(px+3, py+3, cx+2, cy+4, fill='#999999', outline='')
                self.canvas.create_oval(cx-2, py+2, px+ts-3, cy+5, fill='#AAAAAA', outline='')
                self.canvas.create_oval(px+1, py+1, px+ts-1, py+ts-1, fill='', outline='#555555', width=1)
            else:
                self.canvas.create_oval(px+2, py+2, px+ts-2, py+ts-2, fill='#888888', outline='#555555', width=2)
                self.canvas.create_text(px+ts/2, py+ts/2, text='~', fill='#333333', font=('Consolas', 10, 'bold'))

        if self.posicion_escudo:
            sx, sy = self.posicion_escudo
            ts = self.taman_celda
            px, py = sx * ts, sy * ts
            cx, cy = px + ts / 2, py + ts / 2
            import math as _math
            ang = self.shield_spin_frame * _math.pi / 180
            for i in range(4):
                a = ang + i * (_math.pi / 2)
                rx2 = cx + _math.cos(a) * (ts * 0.48)
                ry2 = cy + _math.sin(a) * (ts * 0.48)
                self.canvas.create_oval(rx2 - 2, ry2 - 2, rx2 + 2, ry2 + 2, fill='#00FFCC', outline='')

            pulso_item = abs(_math.sin(self.shield_spin_frame * 0.06))
            radio_halo = int(ts * 0.52 + pulso_item * ts * 0.1)
            alpha_halo = int(60 + pulso_item * 80)
            color_halo_item = '#{:02X}{:02X}{:02X}'.format(0, alpha_halo, int(alpha_halo * 0.85))
            self.canvas.create_oval(cx - radio_halo, cy - radio_halo, cx + radio_halo, cy + radio_halo, fill='', outline=color_halo_item, width=2)
            self.canvas.create_oval(px + 4, py + 4, px + ts - 4, py + ts - 4, fill='#003322', outline='#00FFAA', width=2)
            self.canvas.create_text(cx, cy, text=u'\u26E8', fill='#00FFAA', font=('Consolas', 12, 'bold'))

        if self.es_remake and self.nivel_flash_timer > 0:
            self.nivel_flash_timer -= 1
            if self.nivel_flash_timer > 5:
                color_nv = self.colores_nivel.get(self.level, '#FFFFFF')
                self.canvas.create_rectangle(0, self.alto_canvas // 2 - 22, self.ancho_canvas, self.alto_canvas // 2 + 22, fill='#050515', outline='')
                self.canvas.create_text(self.ancho_canvas // 2, self.alto_canvas // 2 - 8, text=u'\u2b06 NIVEL NUEVO \u2b06', fill='#888888', font=('Consolas', 9))
                self.canvas.create_text(self.ancho_canvas // 2, self.alto_canvas // 2 + 8, text=self.level, fill=color_nv, font=('Consolas', 16, 'bold'))
            self.actualizar_marcador()

        for i, segmento in enumerate(self.serpiente_cuerpo):
            x, y = segmento
            px = x * self.taman_celda
            py = y * self.taman_celda
            px2 = px + self.taman_celda
            py2 = py + self.taman_celda

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
            elif self.level == 'ENTUSIASTA':
                r = max(150, 255 - i * 5)
                g = max(60,  160 - i * 8)
                color = '#{:02X}{:02X}{:02X}'.format(r, g, 0)
            else:
                color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO

            if i == 0 and self.level == 'NYAN_CAT':
                self.canvas.create_oval(px+2, py+2, px2-2, py2-2, fill='white', outline='black')
                self.canvas.create_polygon(px+5, py+8, px+10, py-2, px+15, py+8, fill='white', outline='black')
                self.canvas.create_polygon(px2-15, py+8, px2-10, py-2, px2-5, py+8, fill='white', outline='black')
                self.canvas.create_oval(px+7, py+10, px+10, py+13, fill='black')
                self.canvas.create_oval(px2-10, py+10, px2-7, py+13, fill='black')
                self.canvas.create_oval(px+11, py+14, px+14, py+17, fill='pink', outline='pink')
                self.canvas.create_line(px+12, py+17, px+10, py+19)
                self.canvas.create_line(px+12, py+17, px+14, py+19)
                self.canvas.create_line(px+3, py+15, px+9, py+15)
                self.canvas.create_line(px+3, py+18, px+9, py+17)
                self.canvas.create_line(px2-9, py+15, px2-3, py+15)
                self.canvas.create_line(px2-9, py+17, px2-3, py+18)
            else:
                forma_activa = self.snake_shape
                if forma_activa != 'RECTANGULAR':
                    if self.level in ('HARD', 'NYAN_CAT'):
                        forma_activa = 'TRIANGULAR'
                    else:
                        forma_activa = 'CIRCULAR'
                if forma_activa == 'CIRCULAR':
                    self.canvas.create_oval(px, py, px2, py2, fill=color, outline='black')
                elif forma_activa == 'TRIANGULAR':
                    self.canvas.create_polygon(px + self.taman_celda / 2, py, px, py2, px2, py2, fill=color, outline='black')
                else:
                    if self.es_remake:
                        self.dibujar_celda_estilo(x, y, color)
                    else:
                        self.dibujar_celda(x, y, color)

        if self.escudo_activo and self.serpiente_cuerpo:
            self.escudo_halo_frame += 1
            hx, hy = self.serpiente_cuerpo[0]
            ts = self.taman_celda
            cx, cy = hx * ts + ts/2, hy * ts + ts/2
            pulso = abs(math.sin(self.escudo_halo_frame * 0.15))

            radio_ext = int(ts * 0.9 + pulso * ts * 0.35)
            int_ext = int(80 + pulso * 70)
            color_ext = '#{:02X}{:02X}{:02X}'.format(0, int_ext, int(int_ext * 0.7))
            self.canvas.create_oval(cx - radio_ext, cy - radio_ext, cx + radio_ext, cy + radio_ext, outline=color_ext, width=1)

            radio_int = int(ts * 0.65 + pulso * ts * 0.2)
            int_int = int(160 + pulso * 95)
            color_int = '#{:02X}{:02X}{:02X}'.format(0, int_int, int(int_int * 0.65))
            self.canvas.create_oval(cx - radio_int, cy - radio_int, cx + radio_int, cy + radio_int, outline=color_int, width=3)

            if self.escudo_restante > 0:
                duracion_max = 150
                fraccion = float(self.escudo_restante) / duracion_max
                for i in range(8):
                    a = math.pi * 2 * i / 8
                    if i / 8 < fraccion:
                        tx = cx + math.cos(a) * (radio_ext + 5)
                        ty = cy + math.sin(a) * (radio_ext + 5)
                        self.canvas.create_oval(tx-2, ty-2, tx+2, ty+2, fill='#00FFAA', outline='')
        
    def _dibujar_tanks(self):
        ts = self.taman_celda

        for y in range(self.alto):
            for x in range(self.ancho):
                base = '#111820' if (x + y) % 2 == 0 else '#0D141C'
                x1c, y1c = x * ts, y * ts
                self.canvas.create_rectangle(x1c, y1c, x1c + ts, y1c + ts, fill=base, outline='')

        for x in range(0, self.ancho * ts, ts):
            self.canvas.create_line(x, 0, x, self.alto * ts, fill='#1A2230', width=1)
        for y in range(0, self.alto * ts, ts):
            self.canvas.create_line(0, y, self.ancho * ts, y, fill='#1A2230', width=1)

        if getattr(self, 'boss_phase_active', False):
            self.canvas.create_rectangle(0, 0, self.ancho_canvas - 1, self.alto_canvas - 1, outline='#FF00FF', width=4)
            self.canvas.create_text(self.ancho_canvas // 2, 20, text=u'!! FINAL BOSS !!', fill='#FF00FF', font=('Courier', max(10, ts // 2), 'bold'))

        oleada_txt = u'OLEADA  ' + str(self.tanks_wave)
        self.canvas.create_text(self.ancho_canvas - 8, 8, text=oleada_txt, anchor='ne', fill='#FFDD44', font=('Courier', max(8, ts // 4), 'bold'))

        if self.hammer_pos:
            hx, hy = self.hammer_pos
            hcx = hx * ts + ts // 2
            hcy = hy * ts + ts // 2
            r_pu = ts // 3
            self.canvas.create_oval(hcx - r_pu, hcy - r_pu, hcx + r_pu, hcy + r_pu, fill='#FFDD00', outline='#FF8800', width=2)
            self.canvas.create_text(hcx, hcy, text=u'\u2665', fill='#AA4400', font=('Courier', max(8, ts // 3), 'bold'))

        for bala in self.bullets:
            bx_px = bala['pos'][0] * ts + ts // 2
            by_px = bala['pos'][1] * ts + ts // 2
            r_bala = max(3, ts // 7)
            col_bala = '#FFFFAA' if bala['owner'] == 'player' else '#FF8800'
            glow = '#FFFFFF' if bala['owner'] == 'player' else '#FFCC66'
            self.canvas.create_oval(bx_px - r_bala - 2, by_px - r_bala - 2, bx_px + r_bala + 2, by_px + r_bala + 2, fill=glow, outline='')
            self.canvas.create_oval(bx_px - r_bala, by_px - r_bala, bx_px + r_bala, by_px + r_bala, fill=col_bala, outline='')

        for muro in self.walls:
            mx, my = muro['pos']
            mx_px = mx * ts
            my_px = my * ts
            pct_m = int(100 * muro['hp'] / max(muro['hp_max'], 1))
            col_m = muro['color']
            cbh_m = muro.get('cbh', {})
            if cbh_m:
                mejor = -1
                for umbral_m, c_m in cbh_m.items():
                    u_m = int(umbral_m)
                    if pct_m <= u_m and u_m > mejor:
                        mejor = u_m
                        col_m = c_m
            self.canvas.create_rectangle(mx_px, my_px, mx_px + ts * 2, my_px + ts * 2, fill=col_m, outline='#444433', width=1)
            self.canvas.create_line(mx_px, my_px + ts, mx_px + ts * 2, my_px + ts, fill='#444433', width=1)
            self.canvas.create_line(mx_px + ts, my_px, mx_px + ts, my_px + ts * 2, fill='#444433', width=1)
            if muro['hp'] < muro['hp_max']:
                cx_m = mx_px + ts
                cy_m = my_px + ts
                self.canvas.create_line(cx_m - 4, cy_m - 6, cx_m + 2, cy_m, cx_m - 2, cy_m + 5, fill='#FF4400', width=2)

        for enemy in self.enemies:
            if not enemy['alive']:
                continue
            col = self.tanks_color_por_vida(enemy)
            ex_px = enemy['pos'][0] * ts + ts // 2
            ey_px = enemy['pos'][1] * ts + ts // 2
            px, py = self.player_pos
            ex_g, ey_g = enemy['pos']
            if abs(px - ex_g) >= abs(py - ey_g):
                dir_enemy = 'RIGHT' if px > ex_g else 'LEFT'
            else:
                dir_enemy = 'DOWN' if py > ey_g else 'UP'
            self.tanks_dibujar_tanque(ex_px, ey_px, col, dir_enemy, es_boss=enemy['is_boss'], es_jugador=False)

        px_px = self.player_pos[0] * ts + ts // 2
        py_px = self.player_pos[1] * ts + ts // 2
        pct_hp = self.player_hp / max(self.player_hp_max, 1)
        col_jugador = '#00FFCC' if pct_hp > 0.5 else ('#FFFF00' if pct_hp > 0.25 else '#FF4444')
        self.tanks_dibujar_tanque(px_px, py_px, col_jugador, self.player_dir, es_boss=False, es_jugador=True)

        if hasattr(self, 'lbl_score'):
            self.lbl_score.config(text=str(self.puntuacion))
        if hasattr(self, 'lbl_player_hp'):
            pct = self.player_hp / max(self.player_hp_max, 1)
            col_hp = '#00FF88' if pct > 0.5 else ('#FFFF00' if pct > 0.25 else '#FF4444')
            self.lbl_player_hp.config(text=str(self.player_hp) + ' / ' + str(self.player_hp_max), fg=col_hp)
        if hasattr(self, 'lbl_enemies'):
            vivos = sum(1 for e in self.enemies if e['alive'])
            muros_vivos = len(self.walls)
            texto_enemies = str(vivos)
            if muros_vivos > 0:
                texto_enemies += u'  \u2588' + str(muros_vivos)
            self.lbl_enemies.config(text=texto_enemies)

        if hasattr(self, 'lbl_boss_hp') and hasattr(self, 'boss_phase_active'):
            boss = next((e for e in self.enemies if e['is_boss'] and e['alive']), None)
            if self.boss_phase_active and boss is not None:
                self.lbl_boss_hp.config(text=str(max(0, boss['hp'])) + ' / ' + str(boss['hp_max']))
                if hasattr(self, 'boss_hp_bar'):
                    self.boss_hp_bar.delete('all')
                    pct_boss = max(0.0, boss['hp'] / float(max(boss['hp_max'], 1)))
                    bar_w = int(120 * pct_boss)
                    col_bar = '#FF00FF' if pct_boss > 0.66 else ('#FF0088' if pct_boss > 0.33 else '#FF2222')
                    if bar_w > 0:
                        self.boss_hp_bar.create_rectangle(0, 0, bar_w, 10, fill=col_bar, outline='')
            elif not self.boss_phase_active:
                restante = max(0, self.boss_score_threshold - self.puntuacion)
                if restante > 0:
                    self.lbl_boss_hp.config(text='Falta: ' + str(restante) + 'pts', fg='#888888')
                else:
                    self.lbl_boss_hp.config(text='LLEGANDO...', fg='#FF88FF')

        if hasattr(self, 'nyan_hit_flash_timer') and self.nyan_hit_flash_timer > 0:
            self.nyan_hit_flash_timer -= 1
            if self.nyan_hit_flash_timer > 5:
                self.canvas.create_rectangle(0, self.alto_canvas // 2 - 32, self.ancho_canvas, self.alto_canvas // 2 + 32, fill='#1A0000', outline='')
                self.canvas.create_text(self.ancho_canvas // 2, self.alto_canvas // 2 - 14, text=u'\u26a0 NYAN CAT \u26a0', fill='#FF00FF', font=('Consolas', 13, 'bold'))
                self.canvas.create_text(self.ancho_canvas // 2, self.alto_canvas // 2 + 10, text=u'PUNTOS PERDIDOS', fill='#FF4444', font=('Consolas', 10, 'bold'))

        if hasattr(self, 'shield_flash_timer') and self.shield_flash_timer > 0:
            self.shield_flash_timer -= 1
            if self.shield_flash_timer % 2 == 0:
                self.canvas.create_rectangle(0, 0, self.ancho_canvas, self.alto_canvas, fill='#003322', outline='')
            if self.shield_flash_timer > 3:
                self.canvas.create_text(self.ancho_canvas / 2, self.alto_canvas / 2 - 14, text=u'\u26E8  ESCUDO ACTIVO  \u26E8', fill='#00FFAA', font=('Consolas', 14, 'bold'))

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
                    self.escudo_fue_activado_alguna_vez = True
                    self.escudo_restante = duracion_ticks
                    self.shield_flash_timer = 12
                elif verbo == 'GAME_OVER': 
                    self.juego_terminado = True
                elif verbo == 'DAMAGE_WALL':
                    self.damage_wall_val = int(objeto)
                elif verbo == 'DAMAGE_ENEMY':
                    self.damage_enemy_val = int(objeto)
                elif verbo == 'DAMAGE_PLAYER':
                    self.damage_player_val = int(objeto)
                elif verbo == 'HEAL_PLAYER':
                    self.heal_player_val = int(objeto)
                elif verbo == 'PLAYER_WIN':
                    self.tanks_player_won = True

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
                
                if self.tipo_juego == 'TANKS' and accion['accion'] == 'SPAWN':
                    nombre = accion['objeto']
                    params = accion.get('params', [])
                    pos = params[0] if params and params[0] not in ('RANDOM', 'PLAYER_DIR') else [
                        random.randint(0, self.ancho - 1),
                        random.randint(0, self.alto - 1)
                    ]
                    roles = self.datos_juego.get('entity_roles', {})
                    # ── Actividad 6: BULLET spawn desde tecla ──────────────────────
                    if nombre == 'BULLET':
                        # SPAWN BULLET AT PLAYER_DIR — se dispara en la dirección del jugador
                        self.tanks_disparar_jugador()
                        continue
                    # ── Actividad 6: WALL_BLOCK spawn ─────────────────────────────
                    if roles.get(nombre) == 'WALL':
                        healths = self.datos_juego.get('entity_health', {})
                        cbh_map = self.datos_juego.get('entity_color_by_health', {})
                        self.walls.append({
                            'pos':    list(pos),
                            'hp':     healths.get(nombre, 2),
                            'hp_max': healths.get(nombre, 2),
                            'color':  self.datos_juego.get('shape_colors', {}).get(nombre, '#888866'),
                            'cbh':    cbh_map.get(nombre, {}),
                        })
                        continue
                    if roles.get(nombre) == 'PLAYER':
                        self.player_pos = list(pos)
                    elif roles.get(nombre) in ('ENEMY', 'FINAL_BOSS'):
                        # Primero intentar reutilizar una entrada existente sin posicion
                        colocado = False
                        for enemy in self.enemies:
                            if enemy['shape'] == nombre and enemy['pos'] == [0, 0]:
                                enemy['pos'] = list(pos)
                                enemy['alive'] = True
                                colocado = True
                                break
                        if not colocado:
                            # Actividad 5-B: El boss se spawnea DESPUES del inicio via
                            # ON_TARGET_SCORE. No tiene entrada previa en self.enemies
                            # (porque no estaba en ON_START). Se crea dinamicamente aqui.
                            healths = self.datos_juego.get('entity_health', {})
                            speeds  = self.datos_juego.get('entity_speed', {})
                            frates  = self.datos_juego.get('entity_fire_rate', {})
                            cbh_map = self.datos_juego.get('entity_color_by_health', {})
                            self.enemies.append({
                                'shape':         nombre,
                                'pos':           list(pos),
                                'hp':            healths.get(nombre, 200),
                                'hp_max':        healths.get(nombre, 200),
                                'speed':         speeds.get(nombre, 1),
                                'speed_counter': 0,
                                'fire_rate':     frates.get(nombre, 30),
                                'fire_counter':  random.randint(0, frates.get(nombre, 30)),
                                'color':         self.datos_juego.get('shape_colors', {}).get(nombre, '#FF00FF'),
                                'cbh':           cbh_map.get(nombre, {}),
                                'is_boss':       (roles.get(nombre) == 'FINAL_BOSS'),
                                'alive':         True,
                            })
                    continue

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
                        self.label_powerup.config(text=u'\u26A1 TRIPLE\n\u00a1BOMBA! \u26A1')
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
        ocupadas.update((v[0], v[1]) for v in self.posiciones_veneno)
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

        # --- SNAKE EVOLVED: Colision con frutas venenosas ---
        for i, entrada in enumerate(self.posiciones_veneno):
            vx, vy, _ = entrada
            if nueva_cabeza == (vx, vy):
                self.posiciones_veneno.pop(i)
                # Respawnear uno nuevo en otro lugar
                nueva_pos = self._veneno_buscar_pos()
                if nueva_pos:
                    self.posiciones_veneno.append([nueva_pos[0], nueva_pos[1], self.poison_vida_ticks])
                if not self.escudo_activo:
                    # En niveles ENTUSIASTA y superiores el veneno solo resta puntos.
                    # En MEDIUM/HARD/NYAN_CAT el veneno es letal ademas de restar.
                    niveles_letales = ('MEDIUM', 'HARD', 'NYAN_CAT')
                    if self.level in niveles_letales:
                        self.juego_terminado = True
                    else:
                        self.ejecutar_evento('ON_EAT_POISON')
                break

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

    def _veneno_buscar_pos(self):
        """Retorna una posición (x, y) libre para un veneno, o None si no hay espacio."""
        ocupadas = set(self.serpiente_cuerpo)
        if self.posicion_comida:  ocupadas.add(self.posicion_comida)
        if self.posicion_escudo:  ocupadas.add(self.posicion_escudo)
        ocupadas.update(self.posiciones_nubes)
        ocupadas.update((v[0], v[1]) for v in self.posiciones_veneno)
        for _ in range(200):
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto  - 1)
            if (x, y) not in ocupadas:
                return (x, y)
        return None

    def snake_spawn_veneno(self):
        """Spawnea venenos hasta llegar a poison_max, respetando has_poison del nivel."""
        cfg_nivel = self.levels_config.get(self.level, {}) if self.levels_config else {}
        if not cfg_nivel.get('has_poison', False):
            return
        while len(self.posiciones_veneno) < self.poison_max:
            pos = self._veneno_buscar_pos()
            if pos:
                self.posiciones_veneno.append([pos[0], pos[1], self.poison_vida_ticks])
            else:
                break

    def snake_spawn_escudo(self):
        ocupadas = set(self.serpiente_cuerpo)
        if self.posicion_comida: ocupadas.add(self.posicion_comida)
        ocupadas.update((v[0], v[1]) for v in self.posiciones_veneno)
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
            if hasattr(self, 'shield_bar_canvas') and self.shield_bar_canvas:
                if not self.escudo_fue_activado_alguna_vez:
                    self.shield_bar_canvas.delete('all')
                else:
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
        if self.tipo_juego == 'TANKS':
            oleada_txt = 'Oleada alcanzada: ' + str(getattr(self, 'tanks_wave', 1))
            tk.Label(ventana_go, text=oleada_txt,
                    bg='#07070E', fg='#FFDD44',
                    font=('Consolas', 9)).pack(pady=(6, 0))
        else:
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

    def mostrar_victoria_tanks(self):
        """Muestra pantalla de victoria cuando todos los enemigos son eliminados.
        
        Actividad 5-B: Si el boss fue derrotado (boss_defeated=True), el mensaje
        indica que el jugador vencio al Final Boss, diferenciando la victoria
        normal (oleadas) de la victoria definitiva (boss muerto).
        """
        if self.juego_terminado:
            return   # Evitar doble llamada si boss_defeated y check_win coinciden
        self.juego_terminado = True
        import tkMessageBox
        if getattr(self, 'boss_defeated', False):
            # Victoria especial: se derroto al Final Boss
            msg = (
                u'\u2605 \u00a1FINAL BOSS DERROTADO! \u2605\n\n'
                u'\u00a1Has destruido la Fortaleza Enemiga!\n'
                u'Puntuaci\u00f3n final: ' + str(self.puntuacion) + u'\n'
                u'Oleada alcanzada: ' + str(self.tanks_wave)
            )
            titulo = u'BRICK TANKS \u2014 JEFE FINAL DERROTADO'
        else:
            # Victoria normal: se eliminaron todos los enemigos
            msg = (
                u'\u00a1Todos los enemigos han sido eliminados!\n'
                u'Puntuaci\u00f3n final: ' + str(self.puntuacion)
            )
            titulo = u'BRICK TANKS \u2014 VICTORIA'
        tkMessageBox.showinfo(titulo, msg)
        self.root.destroy()

    # Actividad 5 - A
    def tanks_color_por_vida(self, enemy):
        """Devuelve el color del enemigo según su porcentaje de vida."""
        if not enemy['cbh']:
            return enemy['color']
        pct = int(100 * enemy['hp'] / max(enemy['hp_max'], 1))
        # Encontrar el umbral más cercano por debajo del porcentaje actual
        umbral_aplicable = enemy['color']  # fallback: color original
        mejor_umbral = -1
        for umbral, col in enemy['cbh'].items():
            umbral = int(umbral)
            if pct <= umbral and umbral > mejor_umbral:
                mejor_umbral = umbral
                umbral_aplicable = col
        return umbral_aplicable

    def tanks_mover_jugador(self, direccion):
        """Mueve el tanque del jugador en la dirección dada."""
        self.player_dir = direccion
        dx, dy = {'UP': (0,-1), 'DOWN': (0,1),
                'LEFT': (-1,0), 'RIGHT': (1,0)}.get(direccion, (0,0))
        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy
        # Colisión con bordes
        # Actividad 6: el jugador no puede atravesar muros
        # Actividad 6 fix: verificar las 4 celdas del muro 2x2
        def _en_muro_jugador(cx, cy, walls):
            for m in walls:
                mx, my = m['pos']
                if mx <= cx <= mx+1 and my <= cy <= my+1:
                    return True
            return False
        pared_bloquea = _en_muro_jugador(nx, ny, self.walls)
        if 0 <= nx < self.ancho and 0 <= ny < self.alto and not pared_bloquea:
            self.player_pos = [nx, ny]

    def tanks_disparar_jugador(self):
        if getattr(self, 'player_fire_cooldown', 0) > 0:
            return
        frates = self.datos_juego.get('entity_fire_rate', {})
        self.player_fire_cooldown = frates.get('PLAYER_TANK', 15)
        self.bullets.append({
            'pos':   list(self.player_pos),
            'dir':   self.player_dir,
            'owner': 'player'
        })
    
    def tanks_tick_enemies(self):
        """IA básica de enemigos: se mueven hacia el jugador y disparan."""
        for enemy in self.enemies:
            if not enemy['alive']:
                continue

            # — Movimiento: acercarse al jugador —
            enemy['speed_counter'] += 1
            if enemy['speed_counter'] >= (11 - enemy['speed']):
                enemy['speed_counter'] = 0
                px, py = self.player_pos
                ex, ey = enemy['pos']
                dx = 0 if px == ex else (1 if px > ex else -1)
                dy = 0 if py == ey else (1 if py > ey else -1)
                # Moverse solo en un eje por tick (evita diagonal)
                if abs(px - ex) >= abs(py - ey):
                    nx, ny = ex + dx, ey
                else:
                    nx, ny = ex, ey + dy
                # Actividad 6: los enemigos no pueden atravesar muros
                # Actividad 6 fix: el muro ocupa 2x2 celdas; verificar las 4
                def _en_muro(cx, cy, walls):
                    for m in walls:
                        mx, my = m['pos']
                        if mx <= cx <= mx+1 and my <= cy <= my+1:
                            return True
                    return False
                pared = _en_muro(nx, ny, self.walls)
                if 0 <= nx < self.ancho and 0 <= ny < self.alto and not pared:
                    enemy['pos'] = [nx, ny]
                else:
                    if abs(px - ex) >= abs(py - ey):
                        alt_nx, alt_ny = ex, ey + dy
                    else:
                        alt_nx, alt_ny = ex + dx, ey
                    if 0 <= alt_nx < self.ancho and 0 <= alt_ny < self.alto and not _en_muro(alt_nx, alt_ny, self.walls):
                        enemy['pos'] = [alt_nx, alt_ny]

            # — Disparo: periódico hacia el jugador —
            enemy['fire_counter'] += 1
            if enemy['fire_counter'] >= enemy['fire_rate']:
                enemy['fire_counter'] = 0
                px, py = self.player_pos
                ex, ey = enemy['pos']
                # Calcular dirección del disparo
                if abs(px - ex) >= abs(py - ey):
                    dir_bala = 'RIGHT' if px > ex else 'LEFT'
                else:
                    dir_bala = 'DOWN' if py > ey else 'UP'
                self.bullets.append({
                    'pos':   [ex, ey],
                    'dir':   dir_bala,
                    'owner': 'enemy'
                })
    def tanks_tick_bullets(self):
        """Mueve proyectiles y resuelve colisiones (Actividad 6).

        Colisiones implementadas:
          1. Bala jugador  → enemigo normal  : descuenta HP, elimina si llega a 0.
          2. Bala jugador  → jefe final       : descuenta HP, activa boss_defeated si muere.
          3. Bala jugador  → muro             : descuenta HP del muro, lo destruye si llega a 0.
          4. Bala enemigo  → jugador          : descuenta HP del jugador, GAME OVER si llega a 0.
          5. Bala (cualq.) → borde del mapa   : proyectil eliminado.
          6. Bala enemigo  → muro             : muro absorbe el disparo (bala eliminada).

        Orden de prioridad: bordes → muros → entidades vivas (jugador/enemigos).
        """
        nuevas = []
        delta = {'UP': (0,-1), 'DOWN': (0,1), 'LEFT': (-1,0), 'RIGHT': (1,0)}

        for bala in self.bullets:
            dx, dy = delta.get(bala['dir'], (0,-1))
            bala['pos'][0] += dx
            bala['pos'][1] += dy
            bx, by = bala['pos']

            # ── 1. Fuera del tablero → eliminar ───────────────────────────────
            if not (0 <= bx < self.ancho and 0 <= by < self.alto):
                continue

            eliminada = False

            # ── 2. Colisión con muro (cualquier bala) ─────────────────────────
            # Los muros absorben disparos de enemigos Y del jugador.
            # Si el muro se destruye, la bala también se elimina (no atraviesa).
            for muro in self.walls:
                mx, my = muro['pos']
                # Actividad 6 fix: verificar las 4 celdas del muro 2x2
                if mx <= bx <= mx+1 and my <= by <= my+1:
                    # Actividad 6 — ON_BULLET_HIT_WALL: descuenta 1 HP al muro
                    self.damage_wall_val = 1
                    self.ejecutar_evento('ON_BULLET_HIT_WALL')
                    muro['hp'] -= self.damage_wall_val
                    eliminada = True
                    break   # un solo muro por celda

            if eliminada:
                continue   # bala consumida por el muro

            # ── 3. Bala del jugador ───────────────────────────────────────────
            if bala['owner'] == 'player':
                for enemy in self.enemies:
                    if not enemy['alive']:
                        continue
                    if enemy['pos'] == [bx, by]:
                        # Actividad 6 — ON_BULLET_HIT_ENEMY / ON_BULLET_HIT_BOSS
                        danio_evento = 'ON_BULLET_HIT_BOSS' if enemy['is_boss'] else 'ON_BULLET_HIT_ENEMY'
                        self.damage_enemy_val = 20
                        self.ejecutar_evento(danio_evento)
                        enemy['hp'] -= self.damage_enemy_val
                        if enemy['hp'] <= 0:
                            enemy['alive'] = False
                            # Puntuación extra delegada a INCREASE_SCORE en los eventos json
                            if enemy['is_boss'] and self.boss_phase_active:
                                self.boss_defeated = True
                        eliminada = True
                        break

            # ── 4. Bala del enemigo ───────────────────────────────────────────
            elif bala['owner'] == 'enemy':
                if [bx, by] == self.player_pos:
                    # Actividad 6 — ON_PLAYER_HIT: descuenta 10 HP al jugador
                    self.damage_player_val = 10
                    self.ejecutar_evento('ON_PLAYER_HIT')
                    self.player_hp -= self.damage_player_val
                    self.player_hp = max(0, self.player_hp)
                    self.actualizar_marcador()
                    if self.player_hp <= 0:
                        self.ejecutar_evento('ON_PLAYER_HEALTH_ZERO')
                        self.tanks_game_over = True
                    eliminada = True

            if not eliminada:
                nuevas.append(bala)

        self.bullets = nuevas
        # Limpiar muros destruidos (hp <= 0) al final del tick
        self.walls = [m for m in self.walls if m['hp'] > 0]

    def tanks_tick_hammer(self):
        """Aparición aleatoria del martillo y recogida por el jugador."""
        # Cada ~200 ticks, el martillo puede aparecer si no está activo
        if self.hammer_pos is None:
            self.hammer_timer += 1
            if self.hammer_timer >= 200:
                self.hammer_timer = 0
                if random.random() < 0.4:   # 40% de chance al llegar al umbral
                    self.hammer_pos = [
                        random.randint(0, self.ancho - 1),
                        random.randint(0, self.alto - 1)
                    ]

        # Comprobar si el jugador lo recogió
        if self.hammer_pos is not None and self.player_pos == self.hammer_pos:
            self.heal_player_val = self.hammer_hp_restore
            self.ejecutar_evento('ON_PICKUP_HAMMER')
            self.player_hp = min(self.player_hp_max,
                                self.player_hp + self.heal_player_val)
            self.hammer_pos = None
            self.hammer_timer = 0
            self.actualizar_marcador()

    def tanks_dibujar_tanque(self, cx, cy, color, direccion='UP', es_boss=False, es_jugador=False):
        """Dibuja un tanque con forma realista centrado en pixel (cx, cy).
        
        Componentes:
          - Cuerpo rectangular con bordes biselados
          - Torreta circular encima
          - Canon apuntando en 'direccion'
          - Orugas (rectángulos laterales más oscuros)
        """
        c = self.canvas
        ts = self.taman_celda

        escala = 1.6 if es_boss else 1.0
        W  = int(ts * 0.78 * escala)   # ancho del cuerpo
        H  = int(ts * 0.68 * escala)   # alto del cuerpo
        TW = int(ts * 0.38 * escala)   # ancho torreta
        TH = int(ts * 0.38 * escala)   # alto torreta
        CL = int(ts * 0.48 * escala)   # longitud del cañón
        CW = int(ts * 0.12 * escala)   # grosor del cañón
        OW = int(ts * 0.14 * escala)   # grosor orugas

        # Colores derivados
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        color_oscuro  = '#{:02X}{:02X}{:02X}'.format(max(0,r-60), max(0,g-60), max(0,b-60))
        color_claro   = '#{:02X}{:02X}{:02X}'.format(min(255,r+50), min(255,g+50), min(255,b+50))
        color_oruga   = '#{:02X}{:02X}{:02X}'.format(max(0,r-80), max(0,g-80), max(0,b-80))
        color_torreta = color_claro
        color_canon   = color_oscuro

        x1b, y1b = cx - W//2, cy - H//2
        x2b, y2b = cx + W//2, cy + H//2

        # 1. Orugas (detrás del cuerpo principal)
        c.create_rectangle(x1b - OW, y1b + 4, x1b,      y2b - 4, fill=color_oruga, outline='')
        c.create_rectangle(x2b,      y1b + 4, x2b + OW, y2b - 4, fill=color_oruga, outline='')
        # Detalle de oruga: líneas horizontales
        paso_oruga = max(4, H // 5)
        for yi in range(y1b + 6, y2b - 4, paso_oruga):
            c.create_line(x1b - OW, yi, x1b, yi, fill=color_oscuro, width=1)
            c.create_line(x2b, yi, x2b + OW, yi, fill=color_oscuro, width=1)

        # 2. Cuerpo principal
        c.create_rectangle(x1b, y1b, x2b, y2b, fill=color, outline=color_oscuro, width=1)
        # Borde highlight superior-izquierdo
        c.create_line(x1b, y2b, x1b, y1b, x2b, y1b, fill=color_claro, width=1)
        # Sombra inferior-derecha
        c.create_line(x1b, y2b, x2b, y2b, x2b, y1b, fill=color_oscuro, width=1)

        # 3. Torreta (círculo/óvalo encima del cuerpo)
        tx1, ty1 = cx - TW//2, cy - TH//2
        tx2, ty2 = cx + TW//2, cy + TH//2
        c.create_oval(tx1, ty1, tx2, ty2, fill=color_torreta, outline=color_oscuro, width=1)

        # 4. Cañón (línea gruesa apuntando en la dirección)
        dirs = {
            'UP':    (0, -1),
            'DOWN':  (0,  1),
            'LEFT':  (-1, 0),
            'RIGHT': ( 1, 0),
        }
        # Para enemigos la dirección es hacia el jugador; aquí simplemente 'DOWN' por defecto
        ddx, ddy = dirs.get(direccion, (0, -1))
        # Base del cañón en el borde de la torreta
        base_x = cx + ddx * (TW // 2)
        base_y = cy + ddy * (TH // 2)
        tip_x  = base_x + ddx * CL
        tip_y  = base_y + ddy * CL
        # Cañón con ancho variable (rectángulo rotado simulado con dos líneas paralelas)
        perp_x, perp_y = -ddy, ddx   # perpendicular al cañón
        hw = CW // 2
        c.create_polygon(
            base_x + perp_x * hw, base_y + perp_y * hw,
            tip_x  + perp_x * hw, tip_y  + perp_y * hw,
            tip_x  - perp_x * hw, tip_y  - perp_y * hw,
            base_x - perp_x * hw, base_y - perp_y * hw,
            fill=color_canon, outline=color_oscuro, width=1
        )

        # 5. Estrella/ícono para el jugador
        if es_jugador:
            c.create_text(cx, cy, text=u'\u2605', fill='#FFFFFF',
                          font=('Courier', max(8, int(ts * 0.25)), 'bold'))

        # 6. Si es boss, añadir símbolo de calavera
        if es_boss:
            c.create_text(cx, cy, text=u'\u2620', fill='#FFFFFF',
                          font=('Courier', max(10, int(ts * 0.30)), 'bold'))
    
    # Actividad 5-B: Metodo de transicion al Final Boss
    def tanks_check_boss_transition(self):
        """Monitorea la puntuacion del jugador y dispara la fase del jefe.

        Logica:
          1. Si boss_phase_active ya es True, no hacer nada (ya se disparo).
          2. Si la puntuacion supera boss_score_threshold:
             a. Marcar boss_phase_active = True.
             b. Eliminar todos los enemigos normales del tablero (limpiar oleada).
             c. Ejecutar el evento ON_TARGET_SCORE del JSON, que spawnea al boss
                en la posicion definida en el .brick (SPAWN BOSS_TANK AT ...).
             d. Actualizar el panel lateral para reflejar el cambio de fase.
        Retrocompatibilidad: si el JSON no tiene ON_TARGET_SCORE (juego sin boss),
        este metodo simplemente no hace nada util (el evento no existe en ast).
        """
        if self.boss_phase_active:
            return   # ya en fase boss; no re-ejecutar

        if self.puntuacion >= self.boss_score_threshold:
            # ── Activar fase boss ──
            self.boss_phase_active = True
            # Resetear el flag de oleada para que check_win no dispare respawn
            # mientras el boss entra en escena.
            self.tanks_wave_spawned = False

            # Limpiar enemigos normales (dejarlos muertos)
            for enemy in self.enemies:
                if not enemy['is_boss']:
                    enemy['alive'] = False

            # Ejecutar el evento ON_TARGET_SCORE definido en el .brick
            # Si el juego no lo define, ejecutar_evento simplemente no hace nada.
            self.ejecutar_evento('ON_TARGET_SCORE')

            # Actualizar el contador de oleada al texto BOSS para el panel
            if hasattr(self, 'lbl_wave'):
                self.lbl_wave.config(text=u'BOSS', fg='#FF00FF')
            if hasattr(self, 'lbl_enemies'):
                self.lbl_enemies.config(text='1', fg='#FF00FF')

    def tanks_check_win(self):
        """Si no quedan enemigos vivos, lanza una nueva oleada mas dificil."""
        vivos = [e for e in self.enemies if e['alive']]

        # Actividad 5-B: Si el boss fue derrotado, mostrar pantalla de victoria especial.
        # boss_defeated se pone True en tanks_tick_bullets cuando el HP del boss llega a 0.
        if getattr(self, 'boss_defeated', False):
            self.mostrar_victoria_tanks()
            return

        # Solo evaluar victoria/respawn si la oleada actual ya tuvo enemigos vivos.
        # Esto evita respawn prematuro antes de que ON_START coloque a los enemigos.
        if len(vivos) == 0 and self.tanks_wave_spawned:
            # Resetear el flag para la siguiente oleada
            self.tanks_wave_spawned = False

            # Actividad 5-B: Si estamos en fase boss y no queda nadie, es victoria por boss.
            if getattr(self, 'boss_phase_active', False):
                self.mostrar_victoria_tanks()
                return

            self.tanks_wave += 1
            # Aumentar dificultad cada oleada: mas velocidad, mas cadencia de fuego
            factor_vel  = 1 + (self.tanks_wave - 1) * 0.15   # +15% velocidad por oleada
            factor_fire = max(0.5, 1 - (self.tanks_wave - 1) * 0.08)  # -8% fire_rate (dispara mas rapido)
            nuevos = []
            for tmpl in self.tanks_enemy_templates:
                # En fase boss NO se respawnean enemigos normales ni el boss:
                # la victoria ya se manejo arriba.
                if getattr(self, 'boss_phase_active', False):
                    continue
                nuevos.append({
                    'shape':         tmpl['shape'],
                    'pos':           [
                        random.randint(1, self.ancho - 2),
                        random.randint(1, self.alto // 3)   # siempre en el tercio superior
                    ],
                    'hp':            tmpl['hp_max'],
                    'hp_max':        tmpl['hp_max'],
                    'speed':         min(10, int(tmpl['speed'] * factor_vel) + 1),
                    'speed_counter': 0,
                    'fire_rate':     max(15, int(tmpl['fire_rate'] * factor_fire)),
                    'fire_counter':  random.randint(0, tmpl['fire_rate']),
                    'color':         tmpl['color'],
                    'cbh':           tmpl['cbh'],
                    'is_boss':       tmpl['is_boss'],
                    'alive':         True,
                })
            self.enemies = nuevos
            # Actividad 6: reponer muros en cada oleada nueva
            # (los muros se destruyen durante el combate; se reinician con HP completo)
            for muro in self.walls:
                muro['hp'] = muro['hp_max']
            # Bonus de vida al jugador por completar oleada (25 HP, máximo hasta hp_max)
            self.player_hp = min(self.player_hp_max, self.player_hp + 25)
            # Actualizar panel
            if hasattr(self, 'lbl_score'):
                self.lbl_score.config(text=str(self.puntuacion))
            if hasattr(self, 'lbl_player_hp'):
                self.lbl_player_hp.config(
                    text=str(self.player_hp) + ' / ' + str(self.player_hp_max)
                )
            if hasattr(self, 'lbl_enemies'):
                self.lbl_enemies.config(text=str(len(nuevos)))
            if hasattr(self, 'lbl_wave'):
                self.lbl_wave.config(text=str(self.tanks_wave))

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
