NOMBRE COMPLETO: ALVARO RODRIGO DE LA BARRA VELASCO 

**Calculadora de Simulaciones y Distribuciones** 
<br>
Un conjunto de aplicaciones de escritorio desarrolladas en Python para la simulación de autómatas celulares, modelos epidemiológicos y la generación interactiva de distribuciones de probabilidad.

**Descripción General**
<br>
Este proyecto es un paquete de herramientas de simulación visual construido en Python. Utiliza Tkinter para crear las interfaces gráficas de usuario (GUI) y Matplotlib para la visualización de datos, grillas y gráficos en tiempo real.

El proyecto se divide en dos aplicaciones principales independientes:

App de Simulaciones (simulaciones_app.py): Una interfaz de pestañas que unifica tres simulaciones complejas: el Juego de la Vida 1D, el Juego de la Vida 2D y una simulación de epidemia (COVID).

App de Distribuciones (distribuciones_app.py): Una herramienta dedicada a generar y graficar histogramas de diversas distribuciones de probabilidad, permitiendo al usuario experimentar con sus parámetros.

**Características Principales**
<br>
Este proyecto modulariza cada simulación y generador en sus propios archivos.

**1. Simulador de Autómatas Celulares**
<br>
Juego de la Vida 2D (game_of_life_2d.py):

Implementación clásica del "Juego de la Vida" de John Conway en una grilla 2D.

Permite crear un estado inicial aleatorio con una probabilidad configurable.

Controles para ejecutar la simulación paso a paso o en un bucle continuo (Ejecutar/Parar).

Botón para limpiar y reiniciar la grilla.

Juego de la Vida 1D (game_of_life_1d.py):

Simulador de autómatas celulares elementales en 1D.

Permite al usuario especificar una Regla (del 0 al 255) para generar patrones complejos (ej. Regla 30, Regla 90, Regla 110).

Visualiza la evolución del autómata a lo largo del tiempo, mostrando cada generación como una nueva fila en la gráfica.

2. Simulación Epidemiológica
Simulador COVID (covid_simulation.py):

Un modelo de simulación de epidemias (tipo SIR/SIRD) basado en una grilla.

Cada celda representa un individuo que puede estar en uno de varios estados: Susceptible, Infectado, Recuperado o Muerto.

Visualización Dual:

Muestra la grilla 2D en tiempo real, coloreando cada celda según su estado.

Muestra un gráfico de líneas que traza el conteo total de cada estado a lo largo del tiempo.

Parámetros totalmente configurables por el usuario:

Tamaño de la población (filas/columnas).

Número inicial de infectados.

Probabilidad de infección, recuperación y muerte.

3. Generador de Distribuciones
Generador Aleatorio (random_generators.py y distribuciones_app.py):

Permite generar conjuntos de datos aleatorios basados en múltiples distribuciones de probabilidad.

Distribuciones Continuas: Normal, Uniforme, Exponencial, Gamma, Weibull, Erlang.

Distribuciones Discretas: Bernoulli, Binomial, Poisson.

Grafica un histograma de densidad de los datos generados usando Matplotlib.

Permite al usuario configurar el tamaño de la muestra (n) y los parámetros específicos de cada distribución (ej. mu y sigma para la Normal, lambda para la Exponencial, p para la Bernoulli).



Matplotlib (para la incrustación de gráficos y visualizaciones en Tkinter)

NumPy (para el manejo eficiente de grillas, cálculos numéricos y generación aleatoria)
