import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Asumo que tienes estos módulos ---
# (Si no los tienes, este código no se ejecutará)
# Crearé clases ficticias para que el código sea ejecutable para demostración
try:
    from game_of_life_2d import GameOfLife2D
    from game_of_life_1d import GameOfLife1D
    from covid_simulation import CovidSimulation
except ImportError:
    print("Advertencia: Módulos de simulación no encontrados. Usando clases ficticias.")


    # --- Clases Ficticias (SOLO PARA DEMOSTRACIÓN) ---
    class GameOfLife2D:
        def __init__(self, rows, cols):
            self.rows, self.cols = rows, cols
            self.grid = np.zeros((rows, cols))

        def randomize(self, p=0.2):
            self.grid = np.random.rand(self.rows, self.cols) < p

        def step(self):
            # Simulación muy simple: solo invierte celdas
            self.grid = 1 - self.grid


    class GameOfLife1D:
        def __init__(self, length, rule):
            self.length, self.rule = length, rule
            self.state = np.zeros(length, dtype=int)

        def reset(self):
            self.state[self.length // 2] = 1

        def step(self):
            # Simulación muy simple: desplaza y añade ruido
            self.state = np.roll(self.state, 1)
            if np.random.rand() < 0.1:
                self.state[np.random.randint(0, self.length)] = 1


    class CovidSimulation:
        # Estado 0: Susceptible, 1: Infectado, 2: Recuperado, 3: Muerto
        def __init__(self, rows, cols, init_infected, p_infect, p_recover, p_die):
            self.rows, self.cols = rows, cols
            self.p_infect, self.p_recover, self.p_die = p_infect, p_recover, p_die
            self.grid = np.zeros((rows, cols), dtype=int)
            self.t = 0
            # Colocar infectados iniciales
            indices = np.random.choice(rows * cols, init_infected, replace=False)
            self.grid.flat[indices] = 1
            self.pop = rows * cols

        def step(self):
            new_grid = self.grid.copy()
            for r in range(self.rows):
                for c in range(self.cols):
                    state = self.grid[r, c]

                    # 1. Susceptibles (0) -> Infectados (1)
                    if state == 0:
                        infected_neighbors = 0
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0: continue
                                nr, nc = (r + dr) % self.rows, (c + dc) % self.cols
                                if self.grid[nr, nc] == 1:
                                    infected_neighbors += 1

                        if infected_neighbors > 0:
                            # Probabilidad de infección basada en vecinos
                            p_no_infection = (1 - self.p_infect) ** infected_neighbors
                            if np.random.rand() > p_no_infection:
                                new_grid[r, c] = 1

                    # 2. Infectados (1) -> Recuperados (2) o Muertos (3)
                    elif state == 1:
                        if np.random.rand() < self.p_die:
                            new_grid[r, c] = 3  # Muere
                        elif np.random.rand() < self.p_recover:
                            new_grid[r, c] = 2  # Se recupera

                    # 3. Recuperados (2) y Muertos (3) no cambian

            self.grid = new_grid
            self.t += 1

        def counts(self):
            s = np.sum(self.grid == 0)
            i = np.sum(self.grid == 1)
            r = np.sum(self.grid == 2)
            d = np.sum(self.grid == 3)
            return (self.pop, s, i, r, d)
    # --- Fin de Clases Ficticias ---


class SimulacionesApp:
    def __init__(self, root):
        self.root = root
        root.title('Simulaciones: Juego de la Vida + COVID')
        root.geometry('1100x700')

        # --- Configuración de Estilos (Tema Oscuro) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Colores
        self.bg_color = '#333333'
        self.frame_bg_color = '#444444'
        self.text_color = '#f0f0f0'
        self.button_bg_color = '#e68a00'
        self.button_fg_color = 'white'
        self.entry_bg_color = '#555555'
        self.border_color = '#666666'
        self.select_color = self.button_bg_color
        self.plot_bg_color = self.entry_bg_color  # Fondo para las áreas de gráfico

        root.configure(bg=self.bg_color)

        # Estilo para Frames
        self.style.configure('TFrame', background=self.frame_bg_color)

        # Estilo para Labels
        self.style.configure('TLabel', background=self.frame_bg_color, foreground=self.text_color,
                             font=('Helvetica', 10))

        # Estilo para Entry
        self.style.configure('TEntry',
                             fieldbackground=self.entry_bg_color,
                             foreground=self.text_color,
                             bordercolor=self.border_color,
                             insertbackground=self.text_color,
                             relief='flat',
                             padding=5)

        # Estilo para Button
        self.style.configure('TButton',
                             background=self.button_bg_color,
                             foreground=self.button_fg_color,
                             font=('Helvetica', 10, 'bold'),
                             relief='flat',
                             padding=8)
        self.style.map('TButton',
                       background=[('active', '#ff9900'), ('pressed', '#cc7a00')],
                       foreground=[('active', self.button_fg_color), ('pressed', self.button_fg_color)])

        # Estilo para Notebook (Pestañas)
        self.style.configure('TNotebook',
                             background=self.bg_color,
                             bordercolor=self.border_color,
                             tabmargins=[5, 5, 5, 0])
        self.style.configure('TNotebook.Tab',
                             background=self.frame_bg_color,
                             foreground=self.text_color,
                             padding=[10, 5],
                             font=('Helvetica', 10, 'bold'))
        self.style.map('TNotebook.Tab',
                       background=[('selected', self.select_color), ('active', self.entry_bg_color)],
                       foreground=[('selected', self.button_fg_color), ('active', self.text_color)])
        # --- Fin de Estilos ---

        self.nb = ttk.Notebook(root, style='TNotebook')
        self.nb.pack(fill='both', expand=True, padx=5, pady=5)

        # Variables de estado
        self.g2 = None
        self.g2_running = False
        self.g1 = None
        self.g1_history = []
        self.cv = None
        self.cv_running = False
        self.cv_history = []

        self._build_gameoflife_tab()
        self._build_gameoflife1d_tab()
        self._build_covid_tab()

    # ---------------- Game of Life 2D (Sin cambios) ----------------
    def _build_gameoflife_tab(self):
        tab = ttk.Frame(self.nb, style='TFrame')
        self.nb.add(tab, text='Juego de la Vida 2D')

        left = ttk.Frame(tab, style='TFrame')
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(tab, style='TFrame')
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(left, text='Filas:').pack(anchor='w')
        self.g2_rows = tk.IntVar(value=50)
        ttk.Entry(left, textvariable=self.g2_rows).pack(fill='x')
        ttk.Label(left, text='Columnas:').pack(anchor='w')
        self.g2_cols = tk.IntVar(value=50)
        ttk.Entry(left, textvariable=self.g2_cols).pack(fill='x')
        ttk.Label(left, text='Prob. vivo inicial:').pack(anchor='w')
        self.g2_p = tk.DoubleVar(value=0.2)
        ttk.Entry(left, textvariable=self.g2_p).pack(fill='x')

        ttk.Button(left, text='Crear aleatorio', command=self._g2_create_random).pack(fill='x', pady=5)
        ttk.Button(left, text='Paso', command=self._g2_step).pack(fill='x')
        ttk.Button(left, text='Ejecutar/Parar', command=self._g2_toggle_run).pack(fill='x', pady=5)
        ttk.Button(left, text='Limpiar', command=self._g2_clear).pack(fill='x')

        fig = Figure(figsize=(6, 6), facecolor=self.frame_bg_color)
        self.g2_ax = fig.add_subplot(111)
        self.g2_canvas = FigureCanvasTkAgg(fig, master=right)
        self.g2_canvas.get_tk_widget().pack(fill='both', expand=True)

        self._g2_draw()  # Dibujar el estado inicial (vacío)

    def _g2_create_random(self):
        rows = max(5, int(self.g2_rows.get()))
        cols = max(5, int(self.g2_cols.get()))
        p = float(self.g2_p.get())
        self.g2 = GameOfLife2D(rows=rows, cols=cols)
        self.g2.randomize(p=p)
        self._g2_draw()

    def _g2_draw(self):
        self.g2_ax.clear()
        self.g2_ax.set_facecolor(self.plot_bg_color)

        if self.g2 is not None:
            # Colormap: 0=fondo oscuro, 1=texto claro
            cmap = ListedColormap([self.frame_bg_color, self.text_color])
            self.g2_ax.imshow(self.g2.grid, interpolation='nearest', cmap=cmap)
            self.g2_ax.set_title('Juego de la Vida 2D', color=self.text_color)
        else:
            self.g2_ax.set_title('Juego de la Vida 2D (Presione "Crear")', color=self.text_color)

        self.g2_ax.tick_params(axis='x', colors=self.text_color)
        self.g2_ax.tick_params(axis='y', colors=self.text_color)
        for spine in self.g2_ax.spines.values():
            spine.set_edgecolor(self.text_color)

        self.g2_canvas.draw()

    def _g2_step(self):
        if self.g2 is None:
            self._g2_create_random()
        self.g2.step()
        self._g2_draw()

    def _g2_toggle_run(self):
        self.g2_running = not self.g2_running
        if self.g2_running:
            if self.g2 is None:
                self._g2_create_random()
            self._g2_run_loop()

    def _g2_run_loop(self):
        def loop():
            while self.g2_running:
                time.sleep(0.1)
                try:
                    # Asegurarse de que el paso ocurra en el hilo principal de Tkinter
                    self.root.after(0, self._g2_step)
                except Exception as e:
                    print('Error en loop GOL2D:', e)
                    self.g2_running = False

        threading.Thread(target=loop, daemon=True).start()

    def _g2_clear(self):
        if self.g2 is None:
            self._g2_create_random()
        self.g2.grid = np.zeros_like(self.g2.grid)
        self._g2_draw()

    # ---------------- Game of Life 1D (Sin cambios) ----------------
    def _build_gameoflife1d_tab(self):
        tab = ttk.Frame(self.nb, style='TFrame')
        self.nb.add(tab, text='Juego de la Vida 1D')

        left = ttk.Frame(tab, style='TFrame')
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(tab, style='TFrame')
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(left, text='Longitud:').pack(anchor='w')
        self.g1_length = tk.IntVar(value=300)
        ttk.Entry(left, textvariable=self.g1_length).pack(fill='x')
        ttk.Label(left, text='Regla (0-255):').pack(anchor='w')
        self.g1_rule = tk.IntVar(value=30)
        ttk.Entry(left, textvariable=self.g1_rule).pack(fill='x')
        ttk.Button(left, text='Crear', command=self._g1_create).pack(fill='x', pady=5)
        ttk.Button(left, text='Siguiente', command=self._g1_step).pack(fill='x')
        ttk.Button(left, text='Ejecutar (200 pasos)', command=self._g1_run).pack(fill='x', pady=5)

        fig = Figure(figsize=(8, 5), facecolor=self.frame_bg_color)
        self.g1_ax = fig.add_subplot(111)
        self.g1_canvas = FigureCanvasTkAgg(fig, master=right)
        self.g1_canvas.get_tk_widget().pack(fill='both', expand=True)

        self._g1_draw()  # Dibujar estado inicial

    def _g1_create(self):
        length = max(10, int(self.g1_length.get()))
        rule = min(255, max(0, int(self.g1_rule.get())))
        self.g1 = GameOfLife1D(length=length, rule=rule)
        self.g1.reset()
        self.g1_history = [self.g1.state.copy()]
        self._g1_draw()

    def _g1_step(self):
        if self.g1 is None:
            self._g1_create()
        self.g1.step()
        self.g1_history.append(self.g1.state.copy())
        if len(self.g1_history) > 200:
            self.g1_history.pop(0)
        self._g1_draw()

    def _g1_draw(self):
        self.g1_ax.clear()
        self.g1_ax.set_facecolor(self.plot_bg_color)

        if self.g1_history and self.g1 is not None:
            img = np.array(self.g1_history)
            # Colormap: 0=fondo oscuro, 1=texto claro
            cmap = ListedColormap([self.frame_bg_color, self.text_color])
            self.g1_ax.imshow(img, aspect='auto', interpolation='nearest', cmap=cmap)
            self.g1_ax.set_title(f'Autómata 1D (Regla {self.g1.rule})', color=self.text_color)
        else:
            self.g1_ax.set_title('Autómata 1D (Presione "Crear")', color=self.text_color)

        self.g1_ax.tick_params(axis='x', colors=self.text_color)
        self.g1_ax.tick_params(axis='y', colors=self.text_color)
        for spine in self.g1_ax.spines.values():
            spine.set_edgecolor(self.text_color)

        self.g1_canvas.draw()

    def _g1_run(self):
        if self.g1 is None:
            self._g1_create()

        def run_loop():
            for _ in range(200):
                time.sleep(0.05)
                # Asegurarse de que el paso ocurra en el hilo principal de Tkinter
                self.root.after(0, self._g1_step)

        threading.Thread(target=run_loop, daemon=True).start()

    # ---------------- COVID Tab (MODIFICADA) ----------------
    def _build_covid_tab(self):
        tab = ttk.Frame(self.nb, style='TFrame')
        self.nb.add(tab, text='Simulación COVID (grid)')

        left = ttk.Frame(tab, style='TFrame')
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(tab, style='TFrame')
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # ... (Entradas de parámetros - sin cambios) ...
        ttk.Label(left, text='Filas:').pack(anchor='w')
        self.cv_rows = tk.IntVar(value=60)
        ttk.Entry(left, textvariable=self.cv_rows).pack(fill='x')
        ttk.Label(left, text='Columnas:').pack(anchor='w')
        self.cv_cols = tk.IntVar(value=60)
        ttk.Entry(left, textvariable=self.cv_cols).pack(fill='x')
        ttk.Label(left, text='Inicial infectados:').pack(anchor='w')
        self.cv_init = tk.IntVar(value=5)
        ttk.Entry(left, textvariable=self.cv_init).pack(fill='x')

        ttk.Label(left, text='P(infect) por vecino:').pack(anchor='w')
        self.cv_pinf = tk.DoubleVar(value=0.25)
        ttk.Entry(left, textvariable=self.cv_pinf).pack(fill='x')
        ttk.Label(left, text='P(recover) por paso:').pack(anchor='w')
        self.cv_prec = tk.DoubleVar(value=0.02)
        ttk.Entry(left, textvariable=self.cv_prec).pack(fill='x')
        ttk.Label(left, text='P(die) por paso:').pack(anchor='w')
        self.cv_pdie = tk.DoubleVar(value=0.005)
        ttk.Entry(left, textvariable=self.cv_pdie).pack(fill='x')

        # --- BOTONES MODIFICADOS ---
        ttk.Button(left, text='Crear simulación', command=self._cv_create).pack(fill='x', pady=5)
        ttk.Button(left, text='Paso', command=self._cv_step).pack(fill='x')

        # Botón de Ejecutar/Parar reemplazado
        ttk.Button(left, text='Ejecutar', command=self._cv_run).pack(fill='x', pady=5)
        ttk.Button(left, text='Parar', command=self._cv_stop).pack(fill='x')

        # Nuevo botón Limpiar
        ttk.Button(left, text='Limpiar', command=self._cv_clear).pack(fill='x', pady=(5, 0))
        # --- FIN DE BOTONES MODIFICADOS ---

        fig = Figure(figsize=(7, 6), facecolor=self.frame_bg_color)
        self.cv_ax_grid = fig.add_subplot(211)
        self.cv_ax_chart = fig.add_subplot(212)
        fig.tight_layout(pad=3.0)

        self.cv_canvas = FigureCanvasTkAgg(fig, master=right)
        self.cv_canvas.get_tk_widget().pack(fill='both', expand=True)

        self._cv_draw()  # Dibujar estado inicial

    def _cv_create(self):
        # Detener simulación anterior si está corriendo
        self._cv_stop()

        rows = max(5, int(self.cv_rows.get()))
        cols = max(5, int(self.cv_cols.get()))
        init = max(1, int(self.cv_init.get()))
        pinf = float(self.cv_pinf.get())
        prec = float(self.cv_prec.get())
        pdie = float(self.cv_pdie.get())
        self.cv = CovidSimulation(rows=rows, cols=cols, init_infected=init, p_infect=pinf, p_recover=prec, p_die=pdie)
        self.cv_history = [self.cv.counts()]
        self._cv_draw()

    def _cv_draw(self):
        # Limpiar y configurar Gráfico de Grid
        self.cv_ax_grid.clear()
        self.cv_ax_grid.set_facecolor(self.plot_bg_color)
        self.cv_ax_grid.tick_params(axis='x', colors=self.text_color)
        self.cv_ax_grid.tick_params(axis='y', colors=self.text_color)
        for spine in self.cv_ax_grid.spines.values():
            spine.set_edgecolor(self.text_color)

        # Limpiar y configurar Gráfico de Líneas
        self.cv_ax_chart.clear()
        self.cv_ax_chart.set_facecolor(self.plot_bg_color)
        self.cv_ax_chart.tick_params(axis='x', colors=self.text_color)
        self.cv_ax_chart.tick_params(axis='y', colors=self.text_color)
        self.cv_ax_chart.set_xlabel('Tiempo', color=self.text_color)  # Añadido por claridad
        self.cv_ax_chart.set_ylabel('Conteo', color=self.text_color)  # Añadido por claridad
        for spine in self.cv_ax_chart.spines.values():
            spine.set_edgecolor(self.text_color)

        if self.cv is not None:
            # Dibujar Grid
            # Estados: 0=S, 1=I, 2=R, 3=D
            # Colores: Fondo, Rojo (I), Verde (R), Gris (D)
            cmap = ListedColormap([self.frame_bg_color, 'red', 'lightgreen', 'gray'])
            self.cv_ax_grid.imshow(self.cv.grid, interpolation='nearest', cmap=cmap, vmin=0, vmax=3)
            self.cv_ax_grid.set_title(f'COVID Sim t={self.cv.t}', color=self.text_color)

            # Dibujar Gráfico de Líneas
            times = list(range(len(self.cv_history)))
            # Asumiendo que counts() devuelve (total, S, I, R, D)
            s = [h[1] for h in self.cv_history]
            i = [h[2] for h in self.cv_history]
            r = [h[3] for h in self.cv_history]
            d = [h[4] for h in self.cv_history]

            self.cv_ax_chart.plot(times, s, label='Susceptibles', color='lightblue')
            self.cv_ax_chart.plot(times, i, label='Infectados', color='red')
            self.cv_ax_chart.plot(times, r, label='Recuperados', color='lightgreen')
            self.cv_ax_chart.plot(times, d, label='Muertos', color='gray')

            legend = self.cv_ax_chart.legend()
            for text in legend.get_texts():
                text.set_color(self.text_color)
            legend.get_frame().set_facecolor(self.frame_bg_color)
            legend.get_frame().set_edgecolor(self.border_color)

        else:
            # Estado inicial vacío
            self.cv_ax_grid.set_title('Simulación COVID (Presione "Crear")', color=self.text_color)

        self.cv_canvas.draw()

    def _cv_step(self):
        if self.cv is None:
            self._cv_create()
            return  # No avanzar el primer paso, solo crear

        self.cv.step()
        self.cv_history.append(self.cv.counts())
        self._cv_draw()

    # --- FUNCIONES DE CONTROL MODIFICADAS ---

    def _cv_run(self):
        """Inicia el bucle de simulación de COVID."""
        if self.cv_running:
            return  # Ya está ejecutándose
        if self.cv is None:
            self._cv_create()

        self.cv_running = True
        self._cv_run_loop()

    def _cv_stop(self):
        """Detiene el bucle de simulación de COVID."""
        self.cv_running = False

    def _cv_clear(self):
        """Detiene la simulación y limpia el lienzo."""
        self._cv_stop()  # Detener la simulación primero
        self.cv = None
        self.cv_history = []
        self._cv_draw()  # Redibujar el lienzo (ahora vacío)

    def _cv_run_loop(self):
        """El bucle que corre en un hilo separado."""

        def loop():
            while self.cv_running:
                time.sleep(0.1)
                try:
                    # Asegurarse de que el paso ocurra en el hilo principal de Tkinter
                    self.root.after(0, self._cv_step)
                except Exception as e:
                    # Si la ventana se cierra, self.root puede dar error
                    print('Error en loop COVID:', e)
                    self.cv_running = False

        # Iniciar el hilo
        threading.Thread(target=loop, daemon=True).start()


def main():
    root = tk.Tk()
    app = SimulacionesApp(root)

    # Manejar el cierre de la ventana limpiamente
    def on_closing():
        # Detener todos los bucles en ejecución
        app.g2_running = False
        app.cv_running = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()