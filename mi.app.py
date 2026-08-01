import streamlit as st
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Simulador de Atajadas de Portero", layout="wide")

st.title("⚽ Simulador de Atajadas y Física del Tiro")
st.write("Ajusta los parámetros del tiro y del portero para calcular el tiempo de reacción, la dirección y la probabilidad de atajar el balón.")

# --- BARRA LATERAL: PARÁMETROS ---
st.sidebar.header("⚙️ Configuración")

# 1. Medidas de la Portería
st.sidebar.subheader("📐 Portería")
ancho_porteria = st.sidebar.slider("Ancho de la portería (m)", 3.0, 7.32, 7.32, step=0.1)
alto_porteria = st.sidebar.slider("Alto de la portería (m)", 1.5, 2.44, 2.44, step=0.05)

# 2. Datos del Portero
st.sidebar.subheader("🧤 Portero")
altura_portero = st.sidebar.slider("Altura del portero (m)", 1.50, 2.10, 1.85, step=0.01)

# 3. Datos del Tiro
st.sidebar.subheader("🎯 Tiro")
distancia_tiro = st.sidebar.slider("Distancia del tiro (m)", 9.15, 30.0, 11.0, step=0.5) # 11m es el punto penal
velocidad_kmh = st.sidebar.slider("Velocidad del balón (km/h)", 40, 140, 90, step=5)

# Dirección del tiro
st.sidebar.markdown("**Ubicación del Tiro en la Portería:**")
pos_x = st.sidebar.slider("Posición horizontal X (0 = Izquierda, 100 = Derecha)", 0, 100, 50)
pos_y = st.sidebar.slider("Posición vertical Y (0 = Suelo, 100 = Travesaño)", 0, 100, 50)

# --- CÁLCULOS FÍSICOS Y LÓGICA ---

# Convertir velocidad a m/s
velocidad_ms = velocidad_kmh / 3.6

# Tiempo de vuelo del balón (Tiempo de reacción disponible)
tiempo_reaccion = distancia_tiro / velocidad_ms

# Coordenadas reales del impacto dentro de la portería (en metros)
coordenada_x = (pos_x / 100) * ancho_porteria
coordenada_y = (pos_y / 100) * alto_porteria

# Coordenadas del centro de la portería
centro_x = ancho_porteria / 2

# Recomendación de la atajada según la altura vertical (Y)
if pos_y <= 33:
    zona_altura = "Abajo (Raza / Al suelo)"
    recomendacion = "El portero debe lanzarse arrastrado o colocar la mano abajo de rápido alcance."
elif pos_y <= 66:
    zona_altura = "A media altura"
    recomendacion = "El portero debe realizar un salto lateral a media altura extendiendo los brazos firmes."
else:
    zona_altura = "Arriba (Cerca del travesaño)"
    recomendacion = "El portero debe realizar un salto explosivo hacia arriba/diagonal buscando el manotazo."

# Cálculo simplificado de la Probabilidad de Atajada
# 1. Distancia desde el centro (asumiendo que el portero arranca centrado)
distancia_desde_centro = np.sqrt((coordenada_x - centro_x)**2 + coordenada_y**2)

# 2. Alcance máximo estimado del portero con salto (relacionado con su altura)
alcance_maximo = altura_portero * 1.45

# 3. Factor de tiempo (Un humano necesita ~0.25s solo para reaccionar antes de moverse)
tiempo_util = tiempo_reaccion - 0.25 

if tiempo_util <= 0:
    probabilidad = 0.0
else:
    # Velocidad de cobertura requerida por el portero en m/s
    velocidad_requerida = distancia_desde_centro / tiempo_util
    
    # Evaluar la probabilidad según qué tan rápido tendría que moverse el arquero
    if velocidad_requerida <= (alcance_maximo * 2.0):
        probabilidad = 95 - (velocidad_requerida * 15)
    else:
        probabilidad = 20 - (velocidad_requerida * 5)

# Ajustes de bordes y esquinas (ángulos muertos)
if (pos_x < 10 or pos_x > 90) and pos_y > 80:
    probabilidad -= 25 # Escuadras/Ángulo superior

probabilidad = max(0.0, min(100.0, probabilidad)) # Limitar entre 0% y 100%

# --- MOSTRAR RESULTADOS EN STREAMLIT ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Análisis del Tiro")
    st.metric(label="Tiempo de Reacción Disponible", value=f"{tiempo_reaccion:.2f} segundos")
    st.metric(label="Velocidad del Balón", value=f"{velocidad_ms:.1f} m/s ({velocidad_kmh} km/h)")
    st.metric(label="Distancia del Disparo", value=f"{distancia_tiro} metros")

with col2:
    st.subheader("🧤 Análisis de la Atajada")
    st.metric(label="Probabilidad de Atajada", value=f"{probabilidad:.1f} %")
    st.info(f"**Zona de la atajada:** {zona_altura}")
    st.success(f"**Recomendación:** {recomendacion}")

st.markdown("---")

# --- REPRESENTACIÓN GRÁFICA DE LA PORTERÍA ---
st.subheader("🎯 Visualización del Disparo en la Portería")

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 4))

# Dibujar Marco de la Portería
ax.plot([0, 0, ancho_porteria, ancho_porteria], [0, alto_porteria, alto_porteria, 0], color="black", lw=5)
# Línea de Gol (Suelo)
ax.plot([-0.5, ancho_porteria + 0.5], [0, 0], color="green", lw=3)

# Posición del Portero (Centro, parado)
ax.plot([centro_x, centro_x], [0, min(altura_portero, alto_porteria)], color="blue", lw=4, label="Portero (Inicio)")
ax.scatter([centro_x], [min(altura_portero, alto_porteria)], color="blue", s=100)

# Punto de Impacto del Balón
ax.scatter([coordenada_x], [coordenada_y], color="red", s=200, zorder=5, label="Ubicación del Balón")

# Ajustar límites del gráfico
ax.set_xlim(-1, ancho_porteria + 1)
ax.set_ylim(-0.2, alto_porteria + 0.5)
ax.set_xlabel("Ancho (m)")
ax.set_ylabel("Alto (m)")
ax.set_title("Vista Frontal de la Portería")
ax.legend(loc="upper right")
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)
