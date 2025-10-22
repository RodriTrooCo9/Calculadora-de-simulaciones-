import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from random_generators import RandomGenerators  # Asumo que tienes este módulo


def plot_histogram(data, ax, bins=50, title='', xlabel='x',
                   facecolor='#555555', text_color='#f0f0f0',
                   hist_color='peru', hist_edge='saddlebrown'):
    """
    Función de ayuda para graficar un histograma con estilo oscuro.
    """
    ax.clear()
    ax.set_facecolor(facecolor)  # Fondo del área de la gráfica (gris oscuro)

    # Graficar el histograma con colores naranja
    ax.hist(data, bins=bins, density=True, alpha=0.8, color=hist_color, edgecolor=hist_edge)

    # Colores del texto (título y etiquetas)
    ax.set_title(title, color=text_color)
    ax.set_xlabel(xlabel, color=text_color)
    ax.set_ylabel('Densidad', color=text_color)

    # Colores de los ejes (ticks y bordes)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)

    # Cambiar el color de los bordes del gráfico (spines)
    ax.spines['top'].set_color(text_color)
    ax.spines['bottom'].set_color(text_color)
    ax.spines['left'].set_color(text_color)
    ax.spines['right'].set_color(text_color)


class DistribucionesApp:
    def __init__(self, root):
        self.root = root
        root.title('Generador de Distribuciones Aleatorias')
        root.geometry('1000x600')

        # --- Configuración de Estilos (Tema Oscuro) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Usar el tema 'clam' como base

        # Colores
        bg_color = '#333333'  # Gris muy oscuro para el fondo general
        frame_bg_color = '#444444'  # Gris oscuro para los frames
        text_color = '#f0f0f0'  # Blanco pálido para el texto
        button_bg_color = '#e68a00'  # Naranja para el botón (contraste)
        button_fg_color = 'white'  # Texto blanco para el botón
        entry_bg_color = '#555555'  # Gris medio para campos de entrada
        border_color = '#666666'  # Color del borde
        select_color = button_bg_color  # Naranja para selección en combobox

        root.configure(bg=bg_color)

        # Estilo para Frames
        self.style.configure('TFrame', background=frame_bg_color)

        # Estilo para Labels
        self.style.configure('TLabel', background=frame_bg_color, foreground=text_color, font=('Helvetica', 10))

        # Estilo para Combobox
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', entry_bg_color)],
                       selectbackground=[('readonly', select_color)],
                       selectforeground=[('readonly', button_fg_color)],
                       foreground=[('readonly', text_color)])
        self.style.configure('TCombobox',
                             bordercolor=border_color,
                             arrowcolor=text_color,
                             background=entry_bg_color)

        # Estilo para Entry
        self.style.configure('TEntry',
                             fieldbackground=entry_bg_color,
                             foreground=text_color,
                             bordercolor=border_color,
                             insertbackground=text_color,  # Color del cursor
                             relief='flat',
                             padding=5)

        # Estilo para Button (mantenemos el naranja)
        self.style.configure('TButton',
                             background=button_bg_color,
                             foreground=button_fg_color,
                             font=('Helvetica', 10, 'bold'),
                             relief='flat',
                             padding=8)
        self.style.map('TButton',
                       background=[('active', '#ff9900'), ('pressed', '#cc7a00')],
                       foreground=[('active', button_fg_color), ('pressed', button_fg_color)])
        # --- Fin de Estilos ---

        left = ttk.Frame(root, style='TFrame')
        left.pack(side='left', fill='y', padx=10, pady=10)
        right = ttk.Frame(root, style='TFrame')
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(left, text='Distribución:', style='TLabel').pack(anchor='w')
        self.dist_var = tk.StringVar(value='normal')
        dists = ['uniform', 'exponential', 'erlang', 'gamma', 'normal', 'weibull', 'bernoulli', 'binomial', 'poisson']
        self.dist_combo = ttk.Combobox(left, values=dists, textvariable=self.dist_var, state='readonly',
                                       style='TCombobox')
        self.dist_combo.pack(fill='x')

        ttk.Label(left, text='Tamaño (n):', style='TLabel').pack(anchor='w')
        self.dist_size = tk.IntVar(value=1000)
        ttk.Entry(left, textvariable=self.dist_size, style='TEntry').pack(fill='x')

        ttk.Label(left, text='Parámetros (coma separados):', style='TLabel').pack(anchor='w', pady=(10, 0))
        self.params_entry = ttk.Entry(left, style='TEntry')
        self.params_entry.insert(0, 'mu=0,sigma=1')
        self.params_entry.pack(fill='x')

        ttk.Button(left, text='Generar y graficar', command=self._generate_and_plot, style='TButton').pack(fill='x',
                                                                                                           pady=5)

        # Matplotlib Figure con fondo oscuro
        fig = Figure(figsize=(7, 5), facecolor=frame_bg_color)
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Inicializa la gráfica vacía con el estilo oscuro
        plot_histogram([], self.ax, title='Seleccione una distribución y genere la gráfica')
        self.canvas.draw()

    def _parse_params(self, text):
        d = {}
        if not text:
            return d
        parts = [p.strip() for p in text.split(',') if p.strip()]
        for p in parts:
            if '=' in p:
                k, v = p.split('=', 1)
                try:
                    d[k.strip()] = float(v)
                except ValueError:
                    try:
                        d[k.strip()] = int(v)
                    except ValueError:
                        d[k.strip()] = v
            else:
                try:
                    d[p] = float(p)
                except ValueError:
                    try:
                        d[p] = int(p)
                    except ValueError:
                        d[p] = p
        return d

    def _generate_and_plot(self):
        dist = self.dist_var.get()
        try:
            n = max(1, int(self.dist_size.get()))
        except ValueError:
            messagebox.showerror('Error', 'El tamaño (n) debe ser un número entero válido.')
            return

        params = self._parse_params(self.params_entry.get())
        try:
            if dist == 'uniform':
                a = params.get('a', 0.0)
                b = params.get('b', 1.0)
                data = RandomGenerators.uniform(a=a, b=b, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Uniforme U({a},{b})')
            elif dist == 'exponential':
                lam = params.get('lam', params.get('lambda', 1.0))
                data = RandomGenerators.exponential(lam=lam, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Exponencial (λ={lam})')
            elif dist == 'erlang':
                k = int(params.get('k', 2))
                lam = params.get('lam', 1.0)
                data = RandomGenerators.erlang(k=k, lam=lam, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Erlang k={k}, λ={lam}')
            elif dist == 'gamma':
                shape = params.get('shape', 2.0)
                scale = params.get('scale', 1.0)
                data = RandomGenerators.gamma(shape=shape, scale=scale, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Gamma(shape={shape}, scale={scale})')
            elif dist == 'normal':
                mu = params.get('mu', 0.0)
                sigma = params.get('sigma', 1.0)
                data = RandomGenerators.normal(mu=mu, sigma=sigma, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Normal N({mu},{sigma ** 2})')
            elif dist == 'weibull':
                k = params.get('k', 1.5)
                lam = params.get('lam', 1.0)
                data = RandomGenerators.weibull(k=k, lam=lam, size=n)
                plot_histogram(data, self.ax, bins=50, title=f'Weibull k={k}, λ={lam}')
            elif dist == 'bernoulli':
                p = params.get('p', 0.5)
                data = RandomGenerators.bernoulli(p=p, size=n)
                plot_histogram(data, self.ax, bins=2, title=f'Bernoulli p={p}')
            elif dist == 'binomial':
                nn = int(params.get('n', 10))
                p = params.get('p', 0.5)
                data = RandomGenerators.binomial(n=nn, p=p, size=n)
                plot_histogram(data, self.ax, bins=range(0, nn + 2), title=f'Binomial n={nn}, p={p}')
            elif dist == 'poisson':
                lam = params.get('lam', 1.0)
                data = RandomGenerators.poisson(lam=lam, size=n)
                plot_histogram(data, self.ax, bins=range(0, int(max(data)) + 2), title=f'Poisson λ={lam}')
            else:
                raise ValueError('Distribución no soportada')

            self.canvas.draw()
        except Exception as e:
            messagebox.showerror('Error', f'Error generando la distribución: {e}')


def main():
    root = tk.Tk()
    app = DistribucionesApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()